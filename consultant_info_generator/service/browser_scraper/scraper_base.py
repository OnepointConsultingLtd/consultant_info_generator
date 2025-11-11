from time import sleep
from webbrowser import Chrome

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from consultant_info_generator.logger import logger
from consultant_info_generator.service.browser_scraper.actions import VERIFY_LOGIN_ID


class ScraperBase:

    driver: webdriver.Chrome

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    @staticmethod
    def wait(duration):
        sleep(int(duration))

    