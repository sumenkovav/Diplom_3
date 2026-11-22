from urllib.parse import urlparse

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
)
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.support.ui import WebDriverWait

from config import BASE_URL, WAIT_SECONDS


class BasePage:
    PATH = ""

    def __init__(self, driver):
        self._driver = driver
        self._wait = WebDriverWait(
            driver,
            WAIT_SECONDS,
            poll_frequency=0.2,
            ignored_exceptions=(StaleElementReferenceException,),
        )

    def open(self):
        self._driver.get(BASE_URL + self.PATH)

    def open_in_new_tab(self):
        self._driver.switch_to.new_window("tab")
        self.open()

    def current_tab_handle(self):
        return self._driver.current_window_handle

    def switch_to_tab(self, handle):
        self._driver.switch_to.window(handle)

    def configure_browser(self, width, height, page_load_timeout):
        self._driver.set_window_size(width, height)
        self._driver.set_page_load_timeout(page_load_timeout)

    @property
    def browser_version(self):
        return self._driver.capabilities["browserVersion"]

    def quit_browser(self):
        self._driver.quit()

    def screenshot(self):
        return self._driver.get_screenshot_as_png()

    def wait_for_path(self, path):
        self.wait_for(
            lambda: urlparse(self._driver.current_url).path == path,
            f"Ожидался маршрут {path}",
        )

    def wait_for(self, condition, message=""):
        return self._wait.until(lambda _: condition(), message)

    def visible(self, locator, message=""):
        return self._wait.until(conditions.visibility_of_element_located(locator), message)

    def is_hidden(self, locator):
        return bool(conditions.invisibility_of_element_located(locator)(self._driver))

    def text(self, locator):
        return self.visible(locator).text

    def text_if_visible(self, locator):
        element = conditions.visibility_of_element_located(locator)(self._driver)
        return element.text if element else ""

    def child_text(self, parent_locator, child_locator):
        return self.visible(parent_locator).find_element(*child_locator).text

    def property_value(self, locator, name):
        element = self._wait.until(conditions.presence_of_element_located(locator))
        return element.get_property(name)

    def enter_text(self, locator, value):
        self.visible(locator).send_keys(value)

    def click(self, locator):
        clickable = conditions.element_to_be_clickable(locator)

        def click_when_ready(driver):
            element = clickable(driver)
            if not element:
                return False
            try:
                element.click()
            except ElementClickInterceptedException:
                return False
            return True

        self._wait.until(click_when_ready, f"Не удалось нажать элемент {locator[1]}")

    def execute_script(self, script, *args):
        return self._driver.execute_script(script, *args)

    def drag_and_drop(self, source_locator, target_locator):
        source = self.visible(source_locator)
        target = self.visible(target_locator)
        if self._driver.capabilities["browserName"] == "firefox":
            self._drag_with_html5_events(source, target)
            return

        (
            ActionChains(self._driver)
            .move_to_element(source)
            .click_and_hold()
            .move_by_offset(12, 0)
            .move_to_element(target)
            .release()
            .perform()
        )

    def _drag_with_html5_events(self, source, target):
        self._driver.execute_async_script(
            """
            const [source, target, done] = arguments;
            source.scrollIntoView({ block: "nearest" });
            const dataTransfer = new DataTransfer();
            dataTransfer.setData("text/plain", source.getAttribute("href"));

            function dispatchDrag(element, name) {
                const rect = element.getBoundingClientRect();
                element.dispatchEvent(new DragEvent(name, {
                    bubbles: true,
                    cancelable: true,
                    dataTransfer,
                    clientX: Math.round(rect.left + rect.width / 2),
                    clientY: Math.round(rect.top + rect.height / 2),
                }));
            }

            dispatchDrag(source, "dragstart");
            // React DnD публикует источник на следующем обороте цикла событий.
            setTimeout(() => {
                dispatchDrag(target, "dragenter");
                dispatchDrag(target, "dragover");
                dispatchDrag(target, "drop");
                dispatchDrag(source, "dragend");
                done();
            }, 0);
            """,
            source,
            target,
        )
