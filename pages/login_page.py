import allure
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LoginPage(BasePage):
    PATH = "/login"
    EMAIL = (By.CSS_SELECTOR, "form input[name='name']")
    PASSWORD = (By.CSS_SELECTOR, "form input[type='password']")
    SUBMIT = (By.XPATH, "//form//button[normalize-space()='Войти']")

    def sign_in(self, email, password):
        with allure.step("Входим в тестовую учётную запись через интерфейс"):
            self.visible(self.EMAIL).send_keys(email)
            self.visible(self.PASSWORD).send_keys(password)
            self.click(self.SUBMIT)
            self.wait_for_path("/")
