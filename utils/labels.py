"""Names the site shows for each category, in the order of CATEGORIES in products.js."""
CATEGORY_LABELS = {
    "anime": "Anime",
    "games": "Games",
    "cosplay": "Cosplay",
    "mitologia": "Mitologia",
    "pronta": "Pronta Entrega",
}


def categories_in_use(products) -> list[str]:
    """Categories that have at least one product (the catalog hides the empty ones)."""
    return [key for key in CATEGORY_LABELS
            if any(p.cat == key or (key == "pronta" and p.pronta) for p in products)]


def products_in_category(products, key: str):
    return [p for p in products if p.cat == key or (key == "pronta" and p.pronta)]
