"""Unit tests for the helpers that read the site data. They do not need a browser or a phone."""
import pytest

from utils.site_data import format_height, parse_brl, slugify


@pytest.mark.parametrize("value, shown", [
    (32, "32 cm"),
    (27.5, "27,5 cm"),
    (32.0, "32 cm"),
    ("32 cm", "32 cm"),   # older data stored as text
    ("", ""),
    (None, ""),
])
def test_format_height_matches_what_the_site_shows(value, shown):
    assert format_height(value) == shown


@pytest.mark.parametrize("name, slug", [
    ("War - Darksiders", "war-darksiders"),
    ("War-  Darksiders", "war-darksiders"),   # the old name with a double space gives the same address
    ("Tokito - Demon Slayer", "tokito-demon-slayer"),
    ("Névoa & Aço", "nevoa-aco"),
])
def test_slugify_matches_the_site(name, slug):
    assert slugify(name) == slug


def test_parse_brl_ignores_text_around_the_amount():
    assert parse_brl("A partir de R$\xa01.900,00") == 1900.0
