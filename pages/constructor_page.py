import allure
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as conditions

from config import BUN, SAUCE
from pages.base_page import BasePage


class ConstructorPage(BasePage):
    PATH = "/"
    HEADING = (By.XPATH, "//h1[normalize-space()='Соберите бургер']")
    DROP_ZONE = (By.CSS_SELECTOR, "section[class*='BurgerConstructor_basket__']")
    COUNTER = (By.CSS_SELECTOR, "p[class*='counter_counter__num__']")
    OPEN_MODAL = "section[class*='Modal_modal_opened__']"
    DETAILS_TITLE = (By.XPATH, "//section[contains(@class,'Modal_modal_opened__')]"
                              "//h2[normalize-space()='Детали ингредиента']")
    MODAL = (By.CSS_SELECTOR, f"{OPEN_MODAL} div[class*='Modal_modal__container__']")
    CLOSE_MODAL = (By.CSS_SELECTOR, f"{OPEN_MODAL} button[class*='Modal_modal__close__']")
    LOADER = (
        By.CSS_SELECTOR, "div[class*='Modal_modal_opened__'] img[alt='loading animation']",
    )
    ORDER_BUTTON = (By.XPATH, "//button[normalize-space()='Оформить заказ']")
    ORDER_NUMBER = (
        By.XPATH,
        "//p[normalize-space()='идентификатор заказа']/preceding-sibling::h2[1]",
    )

    @staticmethod
    def ingredient_locator(name):
        return (By.XPATH, f'//a[starts-with(@href,"/ingredient/")][img[@alt="{name}"]]')

    def heading(self):
        return self.visible(self.HEADING).text

    def open_ingredient_details(self, name):
        with allure.step(f"Открываем карточку «{name}»"):
            self.click(self.ingredient_locator(name))

    def ingredient_details(self):
        title = self.visible(self.DETAILS_TITLE).text
        return title, self.visible(self.MODAL).text

    def close_modal(self):
        with allure.step("Закрываем окно по крестику"):
            self.click(self.CLOSE_MODAL)
            self.wait.until(conditions.invisibility_of_element_located(self.MODAL))

    def ingredient_count(self, name):
        card = self.visible(self.ingredient_locator(name))
        text = card.find_element(*self.COUNTER).text
        return int(text) if text else 0

    def wait_for_ingredient_count(self, name, count):
        self.wait.until(
            lambda _: self.ingredient_count(name) == count,
            f"Счётчик «{name}» должен показать {count}",
        )

    def add_ingredient(self, name):
        with allure.step(f"Перетаскиваем «{name}» в конструктор"):
            source = self.visible(self.ingredient_locator(name))
            target = self.visible(self.DROP_ZONE)
            if self.driver.capabilities["browserName"] == "firefox":
                self._drag_with_html5_events(source, target)
                return

            (
                ActionChains(self.driver)
                .move_to_element(source)
                .click_and_hold()
                .move_by_offset(12, 0)
                .move_to_element(target)
                .release()
                .perform()
            )

    def _drag_with_html5_events(self, source, target):
        self.driver.execute_async_script(
            """
            const [source, target, done] = arguments;
            source.scrollIntoView({ block: "nearest" });
            const dataTransfer = new DataTransfer();
            dataTransfer.setData("text/plain", source.getAttribute("href"));

            function dispatchDrag(element, name) {
                const rect = element.getBoundingClientRect();
                element.dispatchEvent(new DragEvent(name, {
                    bubbles: true,
                    cancelable: true,
                    dataTransfer,
                    clientX: Math.round(rect.left + rect.width / 2),
                    clientY: Math.round(rect.top + rect.height / 2),
                }));
            }

            dispatchDrag(source, "dragstart");
            // React DnD publishes the drag source on the next turn of the event loop.
            setTimeout(() => {
                dispatchDrag(target, "dragenter");
                dispatchDrag(target, "dragover");
                dispatchDrag(target, "drop");
                dispatchDrag(source, "dragend");
                done();
            }, 0);
            """,
            source,
            target,
        )

    def place_order(self):
        self.add_ingredient(BUN)
        self.wait_for_ingredient_count(BUN, 2)
        self.add_ingredient(SAUCE)
        self.wait_for_ingredient_count(SAUCE, 1)
        with allure.step("Оформляем заказ и получаем его номер из окна подтверждения"):
            order_title = self.wait.until(conditions.presence_of_element_located(self.ORDER_NUMBER))
            previous_number = order_title.get_property("textContent").strip()
            self.click(self.ORDER_BUTTON)
            return self.wait_for_new_order_number(previous_number)

    def wait_for_new_order_number(self, previous_number):
        visible_number = conditions.visibility_of_element_located(self.ORDER_NUMBER)
        loading_finished = conditions.invisibility_of_element_located(self.LOADER)

        def confirmed_number(driver):
            title = visible_number(driver)
            if not title or not loading_finished(driver):
                return False
            text = title.text.strip()
            if text == previous_number or not text.isdecimal():
                return False
            return int(text)

        return self.wait.until(
            confirmed_number,
            "Окно подтверждения не показало новый номер заказа после оформления",
        )
    