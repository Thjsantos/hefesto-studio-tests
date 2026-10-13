from urllib.parse import parse_qs, unquote, urlparse

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.site_data import parse_brl


class ProductPage(BasePage):
    PATH = "produto.html"

    TITLE = (By.CSS_SELECTOR, ".summary h1")
    SUBTITLE = (By.CSS_SELECTOR, ".summary small")
    PRICE = (By.CSS_SELECTOR, "#price")
    SCALE_BUTTONS = (By.CSS_SELECTOR, ".scales button")
    HEIGHT = (By.CSS_SELECTOR, "#height")
    QUOTE_BUTTON = (By.CSS_SELECTOR, "#quote")
    THUMBS = (By.CSS_SELECTOR, ".thumbs button")
    VIDEO_THUMB = (By.CSS_SELECTOR, ".thumbs button.vid")
    MAIN_IMAGE = (By.CSS_SELECTOR, "#main img")
    MAIN_VIDEO = (By.CSS_SELECTOR, "#main iframe")
    NOT_FOUND = (By.CSS_SELECTOR, "#empty")

    def open_product(self, slug: str):
        return self.open(f"{self.PATH}?id={slug}")

    def title(self) -> str:
        return self.visible(self.TITLE).text.strip()

    def subtitle(self) -> str:
        return self.visible(self.SUBTITLE).get_attribute("textContent").strip()

    def price(self) -> float:
        return parse_brl(self.visible(self.PRICE).get_attribute("textContent"))

    def scale_names(self) -> list[str]:
        self.find(self.SCALE_BUTTONS)
        return [b.text.strip() for b in self.find_all(self.SCALE_BUTTONS)]

    def selected_scale(self) -> str:
        self.find(self.SCALE_BUTTONS)  # the buttons are drawn after the product data loads
        selected = [b for b in self.find_all(self.SCALE_BUTTONS) if "on" in b.get_attribute("class").split()]
        return selected[0].text.strip() if selected else ""

    def select_scale(self, name: str):
        self.find(self.SCALE_BUTTONS)  # the buttons are drawn after the product data loads
        for button in self.find_all(self.SCALE_BUTTONS):
            if button.text.strip() == name:
                self.tap(button)
                self.wait.until(lambda d: "on" in button.get_attribute("class").split())
                return self
        raise AssertionError(f"No scale button {name!r}")

    def height_text(self) -> str:
        return self.find(self.HEIGHT).get_attribute("textContent").strip()

    def quote_link(self) -> tuple[str, str]:
        """(wa.me address, decoded message) of the 'Pedir orçamento' button."""
        href = self.find(self.QUOTE_BUTTON).get_attribute("href")
        parsed = urlparse(href)
        return parsed.netloc + parsed.path, unquote(parse_qs(parsed.query).get("text", [""])[0])

    def thumb_count(self) -> int:
        self.find(self.THUMBS)
        return len(self.find_all(self.THUMBS))

    def open_video(self) -> str:
        """Taps the video thumbnail and returns the address of the embedded player."""
        self.tap(self.visible(self.VIDEO_THUMB))
        return self.find(self.MAIN_VIDEO).get_attribute("src")

    def show_photo(self, index: int = 0):
        self.tap(self.find_all(self.THUMBS)[index])

    def main_image_visible(self) -> bool:
        return self.find(self.MAIN_IMAGE).is_displayed()

    def not_found_visible(self) -> bool:
        return self.visible(self.NOT_FOUND).is_displayed()
