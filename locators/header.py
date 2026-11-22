from selenium.webdriver.common.by import By


CONSTRUCTOR_LINK = (By.XPATH, "//header//a[@href='/' and normalize-space()='Конструктор']")
FEED_LINK = (By.CSS_SELECTOR, "header a[href='/feed']")
