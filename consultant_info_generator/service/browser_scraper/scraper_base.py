from time import sleep

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement


class ScraperBase:

    driver: webdriver.Chrome

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    @staticmethod
    def wait(duration):
        sleep(int(duration))

    def focus(self):
        self.driver.execute_script('alert("Focus window")')
        self.driver.switch_to.alert.accept()

    def mouse_click(self, elem: WebElement):
        action = webdriver.ActionChains(self.driver)
        action.move_to_element(elem).perform()
    