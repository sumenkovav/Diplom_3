from selenium.webdriver.common.by import By


HEADING = (By.XPATH, "//h1[normalize-space()='Лента заказов']")
IN_PROGRESS_LIST = (By.XPATH, "//p[normalize-space()='В работе:']/following-sibling::ul[2]")
IN_PROGRESS_ITEMS = "li"


def counter(label):
    return (By.XPATH, f'//p[normalize-space()="{label}:"]/following-sibling::p[1]')


def order_card(number):
    return (
        By.XPATH,
        f'//a[starts-with(@href,"/feed/")]//p[normalize-space()="#0{number}"]',
    )
