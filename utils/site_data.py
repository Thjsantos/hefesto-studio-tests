"""Reads the site's own data (products.json) so tests compare the screen with the source of truth
instead of hard-coding names and prices that change in the CMS."""
import re
import time
import unicodedata
from dataclasses import dataclass, field

import requests

import config


def slugify(name: str) -> str:
    """Same rule as slugify() in products.js, used for the product page address."""
    ascii_name = unicodedata.normalize("NFD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-")


def parse_brl(text: str) -> float:
    """'R$ 1.900,00' -> 1900.0. Ignores any other text around the amount (e.g. 'A partir de')."""
    match = re.search(r"R\$\s*([\d.]+,\d{2})", text.replace("\xa0", " "))
    if not match:
        raise ValueError(f"No price found in {text!r}")
    return float(match.group(1).replace(".", "").replace(",", "."))


def format_height(value) -> str:
    """How the site shows a scale's height. The CMS stores a number of centimetres (32 -> '32 cm',
    27.5 -> '27,5 cm'); older data may still be text such as '32 cm', which is shown as it is."""
    if value is None or value == "":
        return ""
    if isinstance(value, (int, float)):
        return f"{value:g}".replace(".", ",") + " cm"
    return str(value).strip()

@dataclass
class Scale:
    name: str
    price: float
    height: str = ""


@dataclass
class Product:
    name: str
    cat: str
    patreon: str = ""
    price: float | None = None
    scales: list[Scale] = field(default_factory=list)
    video: str = ""
    photos: int = 0
    pronta: bool = False

    @property
    def display_name(self) -> str:
        """The name as shown on screen: HTML collapses repeated spaces."""
        return " ".join(self.name.split())

    @property
    def slug(self) -> str:
        return slugify(self.name)

    @property
    def starting_price(self) -> float:
        """The price the catalog card shows ('A partir de' the cheapest scale)."""
        return min(s.price for s in self.scales) if self.scales else self.price

    @property
    def video_id(self) -> str:
        match = re.search(r"(?:youtu\.be/|youtube\.com/(?:shorts/|embed/|watch\?(?:.*&)?v=))([\w-]{11})", self.video)
        return match.group(1) if match else ""


def _get(path: str) -> requests.Response:
    # cache-busting query so a fresh CMS save is always seen
    response = requests.get(config.BASE_URL + path, params={"t": int(time.time())}, timeout=20)
    response.raise_for_status()
    return response


def load_products() -> list[Product]:
    products = []
    for p in _get("data/products.json").json()["products"]:
        photos = [x for x in [p.get("img"), p.get("img2"), *p.get("gallery", [])] if x]
        products.append(Product(
            name=p["name"],
            cat=p["cat"],
            patreon=p.get("patreon", ""),
            price=p.get("price"),
            scales=[Scale(s["name"], s["price"], format_height(s.get("height"))) for s in p.get("scales", [])],
            video=p.get("video", ""),
            photos=len(photos),
            pronta=bool(p.get("pronta")),
        ))
    return products


def whatsapp_number() -> str:
    """The WhatsApp number configured in products.js."""
    match = re.search(r'WHATSAPP\s*=\s*"(\d+)"', _get("products.js").text)
    assert match, "WHATSAPP constant not found in products.js"
    return match.group(1)
