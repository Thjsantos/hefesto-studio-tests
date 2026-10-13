"""Behaviour shared by every page: opening, waiting, tapping and the elements present on all pages."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config


class BasePage:
    PATH = ""

    BURGER = (By.CSS_SELECTOR, "button.burger")
    NAV = (By.CSS_SELECTOR, "header nav")
    NAV_LINKS = (By.CSS_SELECTOR, "header nav a")
    WHATSAPP_BUTTON = (By.CSS_SELECTOR, "a.wpp")
    INSTAGRAM_BUTTON = (By.CSS_SELECTOR, "a.ig")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, config.DEFAULT_TIMEOUT)

    # ---- navigation
    def open(self, path: str | None = None):
        self.driver.get(config.BASE_URL + (self.PATH if path is None else path))
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        return self

    # ---- helpers
    def find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_all(self, locator):
        return self.driver.find_elements(*locator)

    def visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def text_content(self, element) -> str:
        """The element's textContent, ignoring CSS (so text-transform and hidden text do not matter).
        Read through JavaScript: get_attribute("textContent") returns None on the real phone."""
        return self.driver.execute_script("return arguments[0].textContent;", element) or ""

    def classes(self, element) -> list[str]:
        """The element's CSS classes. Read through JavaScript: get_attribute("class") sometimes
        returns None on the real phone."""
        return self.driver.execute_script("return Array.from(arguments[0].classList);", element) or []

    def tap(self, element):
        """Scroll the element to the middle of the screen first, so the floating buttons
        in the corner never cover it, then tap. The scroll must be instant: the site uses
        scroll-behavior: smooth, and tapping while the page is still animating hits the wrong spot."""
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});", element)
        self.wait.until(EC.element_to_be_clickable(element))
        element.click()

    # ---- layout
    def has_horizontal_scroll(self) -> bool:
        return self.driver.execute_script(
            "const e = document.documentElement; return e.scrollWidth > e.clientWidth;")

    def viewport_width(self) -> int:
        return self.driver.execute_script("return window.innerWidth;")

    # ---- menu and floating buttons
    def open_menu(self):
        self.tap(self.visible(self.BURGER))
        self.wait.until(lambda d: "open" in self.classes(self.find(self.NAV)))

    def nav_link_texts(self) -> list[str]:
        return [a.text.strip() for a in self.find_all(self.NAV_LINKS) if a.text.strip()]

    def whatsapp_href(self) -> str:
        # the link is filled in by JavaScript once the page scripts have run
        button = self.find(self.WHATSAPP_BUTTON)
        self.wait.until(lambda d: button.get_attribute("href"))
        return button.get_attribute("href")

    def instagram_href(self) -> str:
        return self.find(self.INSTAGRAM_BUTTON).get_attribute("href")
