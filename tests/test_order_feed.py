import allure
import pytest

from pages.constructor_page import ConstructorPage
from pages.feed_page import FeedPage
from pages.header import Header


@allure.feature("Лента заказов")
class TestOrderFeed:
    @allure.title("Счётчик «{counter}» увеличивается после оформления заказа")
    @pytest.mark.parametrize(
        "counter", [FeedPage.TOTAL, FeedPage.TODAY], ids=["all-time", "today"],
    )
    def test_completed_counter_increases(self, driver, signed_in_constructor, counter):
        feed = FeedPage(driver)
        header = Header(driver)
        header.go_to_feed()
        before = feed.counter(counter)

        header.go_to_constructor()
        number = signed_in_constructor.place_order()
        signed_in_constructor.close_modal()
        header.go_to_feed()

        feed.wait_for_order_in_feed(number)
        assert feed.wait_for_counter_increase(counter, before) > before

    @allure.title("Номер оформленного заказа появляется в списке «В работе»")
    def test_order_appears_in_progress(self, driver, signed_in_constructor):
        Header(driver).go_to_feed()
        feed = FeedPage(driver)
        feed.start_watching_in_progress()
        feed_tab = driver.current_window_handle

        driver.switch_to.new_window("tab")
        constructor = ConstructorPage(driver)
        constructor.open()
        number = constructor.place_order()

        driver.switch_to.window(feed_tab)
        feed.wait_for_in_progress_order(number)
