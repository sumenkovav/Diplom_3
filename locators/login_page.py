from selenium.webdriver.common.by import By


EMAIL = (By.CSS_SELECTOR, "form input[name='name']")
PASSWORD = (By.CSS_SELECTOR, "form input[type='password']")
SUBMIT = (By.XPATH, "//form//button[normalize-space()='Войти']")
