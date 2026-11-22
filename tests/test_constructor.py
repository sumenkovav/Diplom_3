import allure

from config import BUN, SAUCE
from pages.constructor_page import ConstructorPage
from pages.feed_page import FeedPage
from pages.header import Header


@allure.feature("Основная функциональность")
class TestConstructor:
    @allure.title("Переход в конструктор из ленты заказов")
    def test_go_to_constructor(self, driver):
        feed = FeedPage(driver)
        feed.open()
        feed.heading()
        Header(driver).go_to_constructor()
        constructor = ConstructorPage(driver)
        constructor.wait_for_path(constructor.PATH)
        assert constructor.heading() == "Соберите бургер"

    @allure.title("Переход в ленту заказов из конструктора")
    def test_go_to_feed(self, driver):
        constructor = ConstructorPage(driver)
        constructor.open()
        constructor.heading()
        Header(driver).go_to_feed()
        assert FeedPage(driver).heading() == "Лента заказов"

    @allure.title("На карточке ингредиента открывается окно деталей")
    def test_open_ingredient_details(self, driver):
        page = ConstructorPage(driver)
        page.open()
        page.open_ingredient_details(SAUCE)

        title, content = page.ingredient_details()
        assert title == "Детали ингредиента"
        assert SAUCE in content
        for label in ("Калории", "Белки", "Жиры", "Углеводы"):
            assert label in content

    @allure.title("Окно деталей ингредиента закрывается по крестику")
    def test_close_ingredient_details(self, driver):
        page = ConstructorPage(driver)
        page.open()
        page.open_ingredient_details(SAUCE)
        page.ingredient_details()
        page.close_modal()

        assert page.heading() == "Соберите бургер"

    @allure.title("Счётчик соуса увеличивается на один после добавления")
    def test_ingredient_counter_increases(self, driver):
        page = ConstructorPage(driver)
        page.open()
        page.add_ingredient(BUN)
        page.wait_for_ingredient_count(BUN, 2)
        before = page.ingredient_count(SAUCE)

        page.add_ingredient(SAUCE)
        page.wait_for_ingredient_count(SAUCE, before + 1)
        assert page.ingredient_count(SAUCE) == before + 1
