"""Home page behaviour and the mobile-specific checks (layout, menu, floating buttons)."""
import pytest

PHONE_MAX_WIDTH = 820  # the site switches to its mobile layout below this width


@pytest.mark.smoke
def test_home_button_opens_the_catalog(home, catalog):
    home.open()
    home.go_to_catalog()
    home.wait.until(lambda d: "catalogo.html" in d.current_url)
    assert len(catalog.wait_for_cards().cards()) > 0


def test_how_to_buy_explains_four_steps(home):
    home.open()
    assert home.how_to_buy_steps() == 4


def test_order_button_goes_to_whatsapp(home, whatsapp_number):
    home.open()
    assert home.order_href().startswith(f"https://wa.me/{whatsapp_number}")


# ---- mobile layout

def test_site_uses_the_phone_layout(home):
    home.open()
    assert home.viewport_width() < PHONE_MAX_WIDTH


def test_home_has_no_horizontal_scroll(home):
    home.open()
    assert not home.has_horizontal_scroll()


def test_catalog_has_no_horizontal_scroll(catalog):
    catalog.open().wait_for_cards()
    assert not catalog.has_horizontal_scroll()


def test_product_page_has_no_horizontal_scroll(product_page, product):
    product_page.open_product(product.slug)
    product_page.title()
    assert not product_page.has_horizontal_scroll()


def test_burger_menu_shows_the_navigation_links(home):
    home.open()
    home.open_menu()
    links = [text.lower() for text in home.nav_link_texts()]
    assert links == ["início", "catálogo", "como comprar", "contato"]


@pytest.mark.parametrize("page_name", ["home", "catalog"])
def test_floating_buttons_link_to_instagram_and_whatsapp(request, page_name, whatsapp_number):
    page = request.getfixturevalue(page_name)
    page.open()
    assert page.instagram_href().rstrip("/") == "https://instagram.com/hefesto_studioo"
    assert page.whatsapp_href().startswith(f"https://wa.me/{whatsapp_number}")
