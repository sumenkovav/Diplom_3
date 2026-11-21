import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as conditions

from pages.base_page import BasePage


class FeedPage(BasePage):
    PATH = "/feed"
    HEADING = (By.XPATH, "//h1[normalize-space()='Лента заказов']")
    IN_PROGRESS_LIST = (By.XPATH, "//p[normalize-space()='В работе:']/following-sibling::ul[2]")
    TOTAL = "Выполнено за все время"
    TODAY = "Выполнено за сегодня"

    def heading(self):
        self.wait_for_path(self.PATH)
        return self.visible(self.HEADING).text

    @staticmethod
    def counter_locator(label):
        return (
            By.XPATH, f'//p[normalize-space()="{label}:"]/following-sibling::p[1]',
        )

    def counter(self, label):
        return int(self.visible(self.counter_locator(label)).text)

    def wait_for_counter_increase(self, label, before):
        with allure.step(f"Проверяем увеличение счётчика «{label}»"):
            locator = self.counter_locator(label)

            def increased(driver):
                current = int(driver.find_element(*locator).text)
                return current if current > before else False

            return self.wait.until(increased, f"Счётчик «{label}» не вырос после {before}")

    def wait_for_order_in_feed(self, number):
        locator = (
            By.XPATH,
            f'//a[starts-with(@href,"/feed/")]'
            f'//p[normalize-space()="#0{number}"]',
        )
        with allure.step(f"Находим оформленный заказ №{number} в ленте"):
            self.wait.until(
                conditions.visibility_of_element_located(locator),
                f"Карточка заказа №{number} не появилась в ленте",
            )

    def start_watching_in_progress(self):
        with allure.step("Начинаем наблюдать за номерами в списке «В работе»"):
            order_list = self.visible(self.IN_PROGRESS_LIST)
            self.driver.execute_script(
                r"""
                const orderList = arguments[0];
                const observed = new Set();
                const record = () => {
                    for (const item of orderList.querySelectorAll("li")) {
                        const text = item.textContent.trim();
                        if (/^\d+$/.test(text)) observed.add(Number(text));
                    }
                };
                record();
                new MutationObserver(record).observe(orderList, {
                    childList: true, subtree: true, characterData: true
                });
                window.stellarOrdersInProgress = observed;
                """,
                order_list,
            )

    def wait_for_in_progress_order(self, number):
        with allure.step(f"Ищем заказ №{number} в списке «В работе»"):
            self.wait.until(
                lambda driver: driver.execute_script(
                    "return window.stellarOrdersInProgress.has(arguments[0]);",
                    number,
                ),
                f"Заказ №{number} не появился в списке «В работе»",
            )
