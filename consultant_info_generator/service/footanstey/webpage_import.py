import logging
import httpx
from bs4 import BeautifulSoup
from typing import AsyncIterator

from consultant_info_generator.model.model import Consultant, Skill
from consultant_info_generator.service.persistence_service_consultants_async import (
    save_consultant,
    delete_consultant_by_profile_id,
)
from consultant_info_generator.service.cv_summary import extract_cv_summary
from consultant_info_generator.service.industry_name_extraction import (
    extract_industry_name,
)

ConsultantInfo = tuple[str | None, str | None, list[str], str, str]

logger = logging.getLogger("footanstey_importer")

_headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
    "DNT": "1",  # Do Not Track
    "Upgrade-Insecure-Requests": "1",
}

START_URL = "https://www.footanstey.com/our-people/"

TIMEOUT = 10.0


class ConsultantCallback:

    def __init__(self):
        self.consultants = []

    async def callback(self, consultant: Consultant):
        await delete_consultant_by_profile_id(consultant.linkedin_profile_url)
        summary = await extract_cv_summary(consultant.cv)
        consultant.summary = summary.summary
        await save_consultant(consultant)
        self.consultants.append(consultant)


async def import_consultants(url: str) -> list[Consultant]:
    """Legacy function that returns all consultants as a list."""
    callback = ConsultantCallback()
    await _scrape_webpage(url, callback)
    return callback.consultants


async def _scrape_webpage(url: str, callback: ConsultantCallback):
    """Async iterator that yields consultants one by one as they're scraped."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        soup = await _create_soup(client, url)
        last_page_number = _extract_last_page_number(soup)

        if isinstance(last_page_number, int):
            for page_number in range(1, last_page_number + 1):
                if page_number == 1:
                    page_url = START_URL
                else:
                    page_url = (
                        f"https://www.footanstey.com/our-people/page/{page_number}/"
                    )

                # Get consultants from this page
                await _extract_consultant_info(page_url, callback)


async def _create_soup(client: httpx.AsyncClient, url: str) -> BeautifulSoup:
    response = await client.get(url, headers=_headers)
    return BeautifulSoup(response.text, "html.parser")


def _extract_last_page_number(soup: BeautifulSoup) -> int | None:
    page_links = soup.select(".container .pagination  a.page-numbers")
    last_page_number = None
    for link in page_links:
        candidate_page_number = link.text
        if candidate_page_number.isdigit():
            last_page_number = int(candidate_page_number)
    return last_page_number


async def _extract_consultant_info(url: str, callback: ConsultantCallback):
    logger.info(f"Accessing: {url}")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        soup = await _create_soup(client, url)
        card_feed_blue = soup.select(".card.card-feed.card-feed--blue")
        for card in card_feed_blue:
            try:
                consultant_info = await _extract_consultant_info_from_card(card)
                if consultant_info:
                    await callback.callback(consultant_info)
            except Exception as e:
                logger.exception(f"Error extracting consultant info from card: {e}")
                logger.error(f"Error extracting consultant info from card: {e}")


async def _extract_consultant_info_from_card(card: BeautifulSoup) -> Consultant | None:
    card_info_title = card.select_one(".card-info__title")
    if not card_info_title:
        return None
    names = card_info_title.text.strip().split(" ")
    if len(names) < 2:
        return None
    card_info_email = f"{names[0]}.{names[-1]}@footanstey.com".lower()
    card_info_role_element = card.select_one(".card-info__role p")
    role = card_info_role_element.text.strip() if card_info_role_element else ""
    card_info_extra_element = card.select_one(".card-info__extra")
    card_info_extra = (
        card_info_extra_element.text.strip() if card_info_extra_element else ""
    )
    user_profile_url = (
        card_info_title.select_one("h3 > a").attrs["href"]
        if card_info_title.select_one("h3 > a")
        else ""
    )
    user_profile, linkedin_profile_url, accolades, team, image = (
        await _extract_user_profile_url(user_profile_url)
    )
    skills = [Skill(name=s) for s in [role, card_info_extra, *accolades]]
    industry_name = await extract_industry_name(user_profile)
    consultant_info = Consultant(
        given_name=names[0],
        surname=names[-1],
        email=card_info_email,
        linkedin_profile_url=linkedin_profile_url or "",
        skills=skills,
        cv=user_profile,
        industry_name=industry_name.industry_name,
        geo_location="London",
        experiences=[],
        photo_200=image,
        photo_400=image,
    )
    return consultant_info


async def _extract_user_profile_url(url: str) -> ConsultantInfo:
    logger.info(f"Extracting user profile URL: {url}")
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        soup = await _create_soup(client, url)
        person_bio = soup.select_one(".d-none.d-md-block.person-bio")
        linkedin_profile_url_element = soup.select_one(".social-link-linkedin")
        bio_content = None
        linkedin_profile_url = None
        if person_bio and person_bio.text.strip():
            bio_content_element = person_bio.select_one(".wp-editor-wrapper")
            bio_content = (
                bio_content_element.text.strip() if bio_content_element else None
            )
        if linkedin_profile_url_element:
            linkedin_profile_url = linkedin_profile_url_element.attrs["href"]
        accolades_element = soup.select(".person-bio__title ~ .wp-editor-wrapper ul li")
        accolades = []
        for accolade in accolades_element:
            accolades.append(accolade.text.strip())
        team = ""
        team_element = soup.select_one(".person-intro__team p a")
        if team_element:
            team = team_element.text.strip()
        image = ""
        image_element = soup.select_one(".person-contact__img img")
        if image_element:
            image = image_element.attrs["src"]
        return bio_content, linkedin_profile_url, accolades, team, image


if __name__ == "__main__":
    import asyncio

    asyncio.run(import_consultants(START_URL))
