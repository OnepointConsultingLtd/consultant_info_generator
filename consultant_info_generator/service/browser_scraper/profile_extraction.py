from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from consultant_info_generator.logger import logger
from consultant_info_generator.model.model import (
    Consultant,
    Experience as ModelExperience,
    Company,
    Skill,
)
from consultant_info_generator.service.browser_scraper.cookie_manager import (
    login_with_cookies,
)
from consultant_info_generator.config import cfg
from consultant_info_generator.service.browser_scraper.linkedin_util_functions import (
    correct_linkedin_url,
)
from consultant_info_generator.model.browser_scraper.linkedin_person import (
    Person,
    Experience as LinkedInExperience,
)
from consultant_info_generator.service.browser_scraper.profile_scraper import Scraper


def _create_driver(headless: bool = True) -> webdriver.Chrome:  #
    # Configure Chrome options
    options = Options()
    if headless:
        options.add_argument("--headless=new")  # 'new' mode for Chrome >= 109
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )


def _convert_to_consultant(person: Person | None) -> Consultant | None:
    if not person:
        return None
    names = person.name.split(" ")
    if len(names) == 0:
        return None
    if len(names) == 1:
        surname = ""
    else:
        surname = names[1]
    return Consultant(
        given_name=names[0],
        surname=surname,
        email="",
        cv=person.about if person.about else "",
        industry_name=person.headline,
        geo_location=person.location,
        linkedin_profile_url=person.linkedin_url,
        experiences=_convert_to_model_experience(person.experiences),
        educations=person.educations,
        skills=[Skill(name=s) for s in person.skills],
    )


def _convert_to_model_experience(
    experience: list[LinkedInExperience],
) -> list[ModelExperience]:
    model_experiences = []

    def convert(date_str: str) -> datetime:
        if date_str == "Present":
            return datetime.now()
        if date_str.endswith("-") or len(date_str) == 4:
            return datetime.strptime(date_str.split("-")[0].strip(), "%Y")
        return datetime.strptime(date_str, "%b %Y")

    for e in experience:
        try:
            model_experience = ModelExperience(
                location=e.location,
                title=e.position_title,
                start=convert(e.from_date),
                end=convert(e.to_date),
                company=Company(name=e.institution_name),
            )
        except Exception as e:
            logger.error(f"Error converting experience: {e}")
            continue
        model_experiences.append(model_experience)
    return model_experiences


def extract_consultant(
    profile: str,
    force_login: bool = False,
    extract_educations: bool = False,
    extract_skills: bool = False,
    headless: bool = True,
) -> Consultant | None:
    """
    Extract a LinkedIn profile using web scraping with Selenium.

    Args:
        profile: LinkedIn profile URL or username
        force_login: If True, skip cookie loading and force a fresh login
        extract_educations: If True, extract educations
        extract_experiences_from_homepage: If True, extract experiences from the homepage
    Returns:
        Profile object if successful, None otherwise
    """
    driver = _create_driver(headless=headless)
    logger.info(f"Extracting profile: {profile}")
    user, password = cfg.get_random_linkedin_credential()

    # Use cookie-based login (will fall back to regular login if cookies don't work)
    login_with_cookies(driver, user, password, force_login=force_login)
    logger.info("Logged in to LinkedIn")

    profile = correct_linkedin_url(profile)
    logger.info(f"Corrected LinkedIn URL: {profile}")
    scraper = Scraper(
        driver,
        profile,
        extract_educations=extract_educations,
        extract_skills=extract_skills,
    )
    scraper.scrape()
    person = scraper.person
    logger.info(f"Extracted profile: {person}")
    consultant = _convert_to_consultant(person)
    consultant.email = f"{profile.split('/')[-1]}@linkedin.com"
    return consultant
