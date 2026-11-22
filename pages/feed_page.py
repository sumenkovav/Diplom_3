import allure
from selenium.common.exceptions import TimeoutException

from locators import feed_page as locators
from pages.base_page import BasePage


class FeedPage(BasePage):
    PATH = "/feed"
    TOTAL = "Выполнено за все время"
    TODAY = "Выполнено за сегодня"

    def heading(self):
        self.wait_for_path(self.PATH)
        return self.text(locators.HEADING)

    def counter(self, label):
        return int(self.text(locators.counter(label)))

    def wait_for_counter_increase(self, label, before):
        locator = locators.counter(label)

        def increased():
            text = self.text_if_visible(locator)
            if not text:
                return False
            current = int(text)
            return current if current > before else False

        with allure.step(f"Проверяем увеличение счётчика «{label}»"):
            return self.wait_for(increased, f"Счётчик «{label}» не вырос после {before}")

    def wait_for_order_in_feed(self, number):
        with allure.step(f"Находим оформленный заказ №{number} в ленте"):
            self.visible(
                locators.order_card(number),
                f"Карточка заказа №{number} не появилась в ленте",
            )

    def start_watching_in_progress(self):
        with allure.step("Начинаем наблюдать за номерами в списке «В работе»"):
            order_list = self.visible(locators.IN_PROGRESS_LIST)
            self.execute_script(
                r"""
                const [orderList, itemSelector] = arguments;
                const observed = new Set();
                const record = () => {
                    for (const item of orderList.querySelectorAll(itemSelector)) {
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
                locators.IN_PROGRESS_ITEMS,
            )

    def wait_for_in_progress_order(self, number) -> bool:
        with allure.step(f"Ищем заказ №{number} в списке «В работе»"):
            try:
                return self.wait_for(
                    lambda: self.execute_script(
                        "return window.stellarOrdersInProgress.has(arguments[0]);",
                        number,
                    ),
                )
            except TimeoutException:
                return False
