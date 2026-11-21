import allure
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class Header(BasePage):
    CONSTRUCTOR_LINK = (
        By.XPATH, "//header//a[@href='/' and normalize-space()='Конструктор']",
    )
    FEED_LINK = (By.CSS_SELECTOR, "header a[href='/feed']")

    def go_to_constructor(self):
        with allure.step("Нажимаем «Конструктор» в шапке"):
            self.click(self.CONSTRUCTOR_LINK)

    def go_to_feed(self):
        with allure.step("Нажимаем «Лента заказов» в шапке"):
            self.click(self.FEED_LINK)
