from selenium.webdriver.common.by import By


HEADING = (By.XPATH, "//h1[normalize-space()='Соберите бургер']")
DROP_ZONE = (By.CSS_SELECTOR, "section[class*='BurgerConstructor_basket__']")
COUNTER = (By.CSS_SELECTOR, "p[class*='counter_counter__num__']")
_OPEN_MODAL = "section[class*='Modal_modal_opened__']"
DETAILS_TITLE = (
    By.XPATH,
    "//section[contains(@class,'Modal_modal_opened__')]"
    "//h2[normalize-space()='Детали ингредиента']",
)
MODAL = (By.CSS_SELECTOR, f"{_OPEN_MODAL} div[class*='Modal_modal__container__']")
CLOSE_MODAL = (By.CSS_SELECTOR, f"{_OPEN_MODAL} button[class*='Modal_modal__close__']")
LOADER = (By.CSS_SELECTOR, "div[class*='Modal_modal_opened__'] img[alt='loading animation']")
ORDER_BUTTON = (By.XPATH, "//button[normalize-space()='Оформить заказ']")
ORDER_NUMBER = (
    By.XPATH,
    "//p[normalize-space()='идентификатор заказа']/preceding-sibling::h2[1]",
)


def ingredient_card(name):
    return (By.XPATH, f'//a[starts-with(@href,"/ingredient/")][img[@alt="{name}"]]')
