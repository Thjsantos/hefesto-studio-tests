from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class HomePage(BasePage):
    PATH = "index.html"

    HEADLINE = (By.CSS_SELECTOR, ".hero h1")
    CATALOG_BUTTON = (By.CSS_SELECTOR, ".hero .cta a.btn:not(.ghost)")
    ORDER_BUTTON = (By.CSS_SELECTOR, "#wpp-main")
    STEPS = (By.CSS_SELECTOR, "#como-comprar .step")

    def headline(self) -> str:
        return self.visible(self.HEADLINE).text

    def go_to_catalog(self):
        self.tap(self.visible(self.CATALOG_BUTTON))

    def how_to_buy_steps(self) -> int:
        self.find(self.STEPS)
        return len(self.find_all(self.STEPS))

    def order_href(self) -> str:
        return self.find(self.ORDER_BUTTON).get_attribute("href")
