import allure
import pytest

from pages.feed_page import FeedPage
from pages.header import Header


@allure.feature("Лента заказов")
class TestOrderFeed:
    @allure.title("Счётчик «{counter}» увеличивается после оформления заказа")
    @pytest.mark.parametrize(
        "counter", [FeedPage.TOTAL, FeedPage.TODAY], ids=["all-time", "today"],
    )
    def test_completed_counter_increases(self, driver, signed_in_constructor, counter):
        constructor = signed_in_constructor
        feed = FeedPage(driver)
        header = Header(driver)
        header.go_to_feed()
        before = feed.counter(counter)

        header.go_to_constructor()
        constructor.assemble_burger()
        previous_number = constructor.order_number_before_submission()
        constructor.submit_order()
        number = constructor.wait_for_new_order_number(previous_number)
        constructor.close_modal()
        header.go_to_feed()

        feed.wait_for_order_in_feed(number)
        assert feed.wait_for_counter_increase(counter, before) > before

    @allure.title("Номер оформленного заказа появляется в списке «В работе»")
    def test_order_appears_in_progress(self, driver, signed_in_constructor):
        constructor = signed_in_constructor
        Header(driver).go_to_feed()
        feed = FeedPage(driver)
        feed.start_watching_in_progress()
        feed_tab = feed.current_tab_handle()

        constructor.open_in_new_tab()
        constructor.assemble_burger()
        previous_number = constructor.order_number_before_submission()
        constructor.submit_order()
        number = constructor.wait_for_new_order_number(previous_number)

        feed.switch_to_tab(feed_tab)
        assert feed.wait_for_in_progress_order(number), (
            f"Заказ №{number} не появился в списке «В работе»"
        )
