

from dataclasses import dataclass
from webbrowser import Chrome

from selenium.webdriver.common.by import By
from consultant_info_generator.model.browser_scraper.linkedin_person import PersonSearchResult
from consultant_info_generator.service.browser_scraper.linkedin_util_functions import extract_profile_id
from consultant_info_generator.service.browser_scraper.scraper_base import ScraperBase


class PersonSearchScraper(ScraperBase):

    def __init__(self, driver: Chrome = None):
        super().__init__(driver)


    def search(self, query: str) -> list[PersonSearchResult]:
        if self.is_signed_in():
            self.driver.get(f"https://www.linkedin.com/search/results/people/?keywords={query}")
            self.wait_for_element_to_load(By.CSS_SELECTOR, "div[data-view-name=people-search-result]")
            results = self.driver.find_elements(By.CSS_SELECTOR, "a[data-view-name=search-result-lockup-title]")
            person_search_results = []
            for result in results:
                person_url = result.get_attribute("href")
                person_name = result.text
                person_profile_id = extract_profile_id(person_url)
                following_siblings = result.find_elements(By.XPATH, "../following-sibling::*")
                title = ""
                if len(following_siblings) > 0:
                    title = following_siblings[0].text
                person_search_results.append(PersonSearchResult(
                    person_name=person_name,
                    person_linkedin_url=person_url,
                    profile_id=person_profile_id,
                    title=title
                ))
            return person_search_results
        else:
            raise Exception("you are not logged in!")