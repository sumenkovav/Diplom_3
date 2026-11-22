import allure

from config import BUN, SAUCE
from locators import constructor_page as locators
from pages.base_page import BasePage


class ConstructorPage(BasePage):
    PATH = "/"

    def heading(self):
        return self.text(locators.HEADING)

    def open_ingredient_details(self, name):
        with allure.step(f"Открываем карточку «{name}»"):
            self.click(locators.ingredient_card(name))

    def ingredient_details(self):
        return self.text(locators.DETAILS_TITLE), self.text(locators.MODAL)

    def close_modal(self):
        with allure.step("Закрываем окно по крестику"):
            self.click(locators.CLOSE_MODAL)
            self.wait_for(lambda: self.is_hidden(locators.MODAL))

    def ingredient_count(self, name):
        text = self.child_text(locators.ingredient_card(name), locators.COUNTER)
        return int(text) if text else 0

    def wait_for_ingredient_count(self, name, count):
        self.wait_for(
            lambda: self.ingredient_count(name) == count,
            f"Счётчик «{name}» должен показать {count}",
        )

    def add_ingredient(self, name):
        with allure.step(f"Перетаскиваем «{name}» в конструктор"):
            self.drag_and_drop(locators.ingredient_card(name), locators.DROP_ZONE)

    def assemble_burger(self):
        with allure.step("Собираем бургер из булки и соуса"):
            self.add_ingredient(BUN)
            self.wait_for_ingredient_count(BUN, 2)
            self.add_ingredient(SAUCE)
            self.wait_for_ingredient_count(SAUCE, 1)

    def order_number_before_submission(self):
        return self.property_value(locators.ORDER_NUMBER, "textContent").strip()

    def submit_order(self):
        with allure.step("Нажимаем «Оформить заказ»"):
            self.click(locators.ORDER_BUTTON)

    def wait_for_new_order_number(self, previous_number):
        def confirmed_number():
            text = self.text_if_visible(locators.ORDER_NUMBER).strip()
            if text == previous_number or not text.isdecimal():
                return False
            if not self.is_hidden(locators.LOADER):
                return False
            return int(text)

        with allure.step("Получаем номер заказа из окна подтверждения"):
            return self.wait_for(
                confirmed_number,
                "Окно подтверждения не показало новый номер заказа после оформления",
            )
