import allure

from locators import login_page as locators
from pages.base_page import BasePage


class LoginPage(BasePage):
    PATH = "/login"

    def sign_in(self, email, password):
        with allure.step("Входим в тестовую учётную запись через интерфейс"):
            self.enter_text(locators.EMAIL, email)
            self.enter_text(locators.PASSWORD, password)
            self.click(locators.SUBMIT)
            self.wait_for_path("/")
