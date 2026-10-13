import pytest

from utils.labels import CATEGORY_LABELS

MAX_MEDIA = 6  # photos + video per product


@pytest.mark.smoke
def test_shows_name_category_and_model(product_page, product):
    product_page.open_product(product.slug)
    assert product_page.title() == product.display_name
    subtitle = product_page.subtitle().lower()
    assert CATEGORY_LABELS[product.cat].lower() in subtitle
    if product.patreon:
        assert product.patreon.lower() in subtitle


def test_first_scale_is_selected_by_default(product_page, scaled_product):
    product_page.open_product(scaled_product.slug)
    first = scaled_product.scales[0]
    assert product_page.scale_names() == [s.name for s in scaled_product.scales]
    assert product_page.selected_scale() == first.name
    assert product_page.price() == first.price
    if first.height:
        assert product_page.height_text() == first.height


def test_choosing_a_scale_updates_price_and_height(product_page, multi_scale_product):
    product_page.open_product(multi_scale_product.slug)
    for scale in multi_scale_product.scales:
        product_page.select_scale(scale.name)
        product_page.wait.until(lambda d: product_page.price() == scale.price)
        if scale.height:
            assert product_page.height_text() == scale.height


def test_product_without_scales_shows_its_single_price(product_page, plain_product):
    product_page.open_product(plain_product.slug)
    assert product_page.price() == plain_product.price


@pytest.mark.smoke
def test_quote_button_opens_whatsapp_with_the_product(product_page, product, whatsapp_number):
    product_page.open_product(product.slug)
    address, message = product_page.quote_link()
    assert address == f"wa.me/{whatsapp_number}"
    assert product.name in message


def test_quote_message_follows_the_chosen_scale(product_page, multi_scale_product):
    product_page.open_product(multi_scale_product.slug)
    last = multi_scale_product.scales[-1]
    product_page.select_scale(last.name)
    product_page.wait.until(lambda d: f"escala {last.name}" in product_page.quote_link()[1])


def test_gallery_never_shows_more_than_six_media(product_page, product):
    product_page.open_product(product.slug)
    product_page.title()  # wait for the page to render
    has_video = bool(product.video_id)
    media = min(product.photos, MAX_MEDIA - has_video) + has_video
    expected_thumbs = media if media > 1 else 0
    assert len(product_page.find_all(product_page.THUMBS)) == expected_thumbs <= MAX_MEDIA


def test_video_thumbnail_plays_the_youtube_video_and_photos_bring_it_back(product_page, video_product):
    product_page.open_product(video_product.slug)
    src = product_page.open_video()
    assert f"youtube-nocookie.com/embed/{video_product.video_id}" in src
    product_page.show_photo(0)
    assert product_page.main_image_visible()
    assert not product_page.find_all(product_page.MAIN_VIDEO)


def test_unknown_product_shows_the_not_found_message(product_page):
    product_page.open_product("this-product-does-not-exist")
    assert product_page.not_found_visible()
