import allure

from locators import header as locators
from pages.base_page import BasePage


class Header(BasePage):
    def go_to_constructor(self):
        with allure.step("Нажимаем «Конструктор» в шапке"):
            self.click(locators.CONSTRUCTOR_LINK)

    def go_to_feed(self):
        with allure.step("Нажимаем «Лента заказов» в шапке"):
            self.click(locators.FEED_LINK)
