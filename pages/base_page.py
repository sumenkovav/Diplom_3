from urllib.parse import urlparse

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
)
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.support.ui import WebDriverWait

from config import BASE_URL, WAIT_SECONDS


class BasePage:
    PATH = ""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(
            driver, WAIT_SECONDS, poll_frequency=0.2,
            ignored_exceptions=(StaleElementReferenceException,),
        )

    def open(self):
        self.driver.get(BASE_URL + self.PATH)

    def wait_for_path(self, path):
        self.wait.until(
            lambda driver: urlparse(driver.current_url).path == path,
            f"Ожидался маршрут {path}",
        )

    def visible(self, locator):
        return self.wait.until(conditions.visibility_of_element_located(locator))

    def click(self, locator):
        clickable = conditions.element_to_be_clickable(locator)

        def click_when_ready(driver):
            element = clickable(driver)
            if not element:
                return False
            try:
                element.click()
            except ElementClickInterceptedException:
                return False
            return True

        self.wait.until(click_when_ready, f"Не удалось нажать элемент {locator[1]}")
