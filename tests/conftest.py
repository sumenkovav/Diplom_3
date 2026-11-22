from functools import partial
from secrets import token_urlsafe
from uuid import uuid4

import allure
import pytest
import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from config import BASE_URL, REQUEST_TIMEOUT
from pages.base_page import BasePage
from pages.constructor_page import ConstructorPage
from pages.login_page import LoginPage


BROWSERS = ("chrome", "firefox")


def pytest_addoption(parser):
    parser.addoption("--browser", action="append", choices=BROWSERS,
                     help="Браузер Chrome или Firefox. По умолчанию используются оба.")
    parser.addoption("--headed", action="store_true",
                     help="Запускать браузер с видимым окном.")


def pytest_generate_tests(metafunc):
    if "driver" in metafunc.fixturenames:
        browsers = metafunc.config.getoption("--browser") or BROWSERS
        metafunc.parametrize("driver", browsers, indirect=True)


def start_firefox(options):
    try:
        return webdriver.Firefox(options=options)
    except WebDriverException as error:
        if not (error.msg or "").strip().endswith("unexpectedly closed with status 0"):
            raise

    with allure.step("Повторяем запуск после преждевременного закрытия Firefox"):
        return webdriver.Firefox(options=options)


@pytest.fixture
def driver(request):
    headed = request.config.getoption("--headed")
    with allure.step(f"Запускаем {request.param}"):
        if request.param == "chrome":
            options = webdriver.ChromeOptions()
            if not headed:
                options.add_argument("--headless=new")
            browser = webdriver.Chrome(options=options)
        else:
            options = webdriver.FirefoxOptions()
            options.accept_insecure_certs = False
            if not headed:
                options.add_argument("-headless")
            browser = start_firefox(options)

    session = BasePage(browser)
    request.addfinalizer(session.quit_browser)
    session.configure_browser(width=1440, height=1000, page_load_timeout=35)
    allure.dynamic.parameter("browser_version", session.browser_version)
    return browser


def delete_test_account(token):
    with allure.step("Удаляем созданную тестовую учётную запись"):
        response = requests.delete(
            f"{BASE_URL}/api/auth/user",
            headers={"Authorization": token},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()


@pytest.fixture
def signed_in_constructor(driver, request):
    account = {
        "email": f"qa-ui-{uuid4().hex}@example.com",
        "name": "QA UI",
        "password": token_urlsafe(16),
    }
    with allure.step("Подготавливаем отдельную тестовую учётную запись"):
        response = requests.post(
            f"{BASE_URL}/api/auth/register", json=account, timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        token = response.json()["accessToken"]
        request.addfinalizer(partial(delete_test_account, token))

    login = LoginPage(driver)
    login.open()
    login.sign_in(account["email"], account["password"])
    constructor = ConstructorPage(driver)
    constructor.heading()
    return constructor


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    result = yield
    report = result.get_result()
    browser = item.funcargs.get("driver")
    if report.failed and report.when in ("setup", "call") and browser is not None:
        try:
            allure.attach(
                BasePage(browser).screenshot(),
                "Экран в момент ошибки",
                allure.attachment_type.PNG,
            )
        except WebDriverException:
            pass
