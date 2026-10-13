import pytest

from utils.labels import CATEGORY_LABELS, categories_in_use, products_in_category
from utils.site_data import parse_brl


@pytest.mark.smoke
def test_catalog_lists_every_product(catalog, products):
    catalog.open()
    assert sorted(catalog.card_names()) == sorted(p.display_name for p in products)


def test_card_shows_the_starting_price(catalog, product):
    catalog.open().wait_for_cards()
    assert catalog.card_price(product.display_name) == product.starting_price


def test_card_says_a_partir_de_when_the_product_has_scales(catalog, scaled_product):
    catalog.open().wait_for_cards()
    assert "a partir de" in catalog.card_price_text(scaled_product.display_name).lower()


def test_filter_buttons_only_exist_for_categories_with_products(catalog, products):
    catalog.open()
    expected = ["Todos"] + [CATEGORY_LABELS[k] for k in categories_in_use(products)]
    assert [label.lower() for label in catalog.filter_labels()] == [label.lower() for label in expected]


def test_filter_shows_only_the_chosen_category(catalog, products, category):
    catalog.open().wait_for_cards()
    catalog.filter_by(CATEGORY_LABELS[category])
    expected = sorted(p.display_name for p in products_in_category(products, category))
    catalog.wait.until(lambda d: sorted(catalog.card_names()) == expected)


def test_search_finds_a_product_by_name(catalog, product):
    word = max(product.display_name.split(), key=len).lower().strip("-")
    catalog.open().wait_for_cards()
    catalog.search(word)
    catalog.wait.until(lambda d: product.display_name in catalog.card_names())
    assert all(word in name.lower() for name in catalog.card_names())


def test_search_without_results_shows_the_empty_message(catalog):
    catalog.open().wait_for_cards()
    catalog.search("zzzxqjk")
    catalog.wait.until(lambda d: len(catalog.cards()) == 0)
    assert catalog.empty_message_visible()


@pytest.mark.smoke
def test_tapping_a_card_opens_its_product_page(catalog, product_page, product):
    catalog.open().wait_for_cards()
    catalog.open_product(product.display_name)
    product_page.wait.until(lambda d: "produto.html" in d.current_url)
    assert product.slug in product_page.driver.current_url
    assert product_page.title() == product.display_name
