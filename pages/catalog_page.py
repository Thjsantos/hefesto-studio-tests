from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from utils.site_data import parse_brl


class CatalogPage(BasePage):
    PATH = "catalogo.html"

    CARDS = (By.CSS_SELECTOR, "#grid .card")
    FILTERS = (By.CSS_SELECTOR, "#filters button")
    SEARCH = (By.CSS_SELECTOR, "#q")
    EMPTY_MESSAGE = (By.CSS_SELECTOR, "#empty")

    def wait_for_cards(self):
        self.wait.until(lambda d: len(self.find_all(self.CARDS)) > 0)
        return self

    def cards(self):
        return self.find_all(self.CARDS)

    def card_names(self) -> list[str]:
        self.wait_for_cards()
        return [c.find_element(By.CSS_SELECTOR, "h3").text.strip() for c in self.cards()]

    def card_categories(self) -> list[str]:
        """The small label above the name, e.g. 'ANIME · MY ANIMATE' -> 'anime'."""
        return [c.find_element(By.CSS_SELECTOR, "small").get_attribute("textContent").split("·")[0].strip().lower()
                for c in self.cards()]

    def card_price(self, name: str) -> float:
        for card in self.cards():
            if card.find_element(By.CSS_SELECTOR, "h3").text.strip() == name:
                return parse_brl(card.find_element(By.CSS_SELECTOR, ".price").get_attribute("textContent"))
        raise AssertionError(f"No card named {name!r}")

    def card_price_text(self, name: str) -> str:
        for card in self.cards():
            if card.find_element(By.CSS_SELECTOR, "h3").text.strip() == name:
                return card.find_element(By.CSS_SELECTOR, ".price").get_attribute("textContent")
        raise AssertionError(f"No card named {name!r}")

    def filter_labels(self) -> list[str]:
        self.find(self.FILTERS)
        return [b.text.strip() for b in self.find_all(self.FILTERS)]

    def filter_by(self, label: str):
        for button in self.find_all(self.FILTERS):
            if button.text.strip().lower() == label.lower():
                self.tap(button)
                self.wait.until(lambda d: "on" in button.get_attribute("class"))
                return self
        raise AssertionError(f"No filter button {label!r}")

    def search(self, text: str):
        box = self.visible(self.SEARCH)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});", box)
        box.clear()
        box.send_keys(text)
        return self

    def empty_message_visible(self) -> bool:
        return self.find(self.EMPTY_MESSAGE).is_displayed()

    def open_product(self, name: str):
        for card in self.cards():
            if card.find_element(By.CSS_SELECTOR, "h3").text.strip() == name:
                self.tap(card.find_element(By.CSS_SELECTOR, "a.pic"))
                return
        raise AssertionError(f"No card named {name!r}")
