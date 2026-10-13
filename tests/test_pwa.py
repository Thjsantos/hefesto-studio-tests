"""PWA behaviour: what the site declares, and (with --target pwa) how it runs in the installed app."""
from urllib.parse import urljoin

import pytest
import requests


def test_manifest_declares_a_standalone_app_with_icons(home):
    home.open()
    manifest_url = home.driver.execute_script("return document.querySelector('link[rel=manifest]').href;")
    manifest = requests.get(manifest_url, timeout=15).json()

    assert manifest["name"]
    assert manifest["display"] == "standalone"
    assert requests.get(urljoin(manifest_url, manifest["start_url"]), timeout=15).ok
    sizes = {icon["sizes"] for icon in manifest["icons"]}
    assert {"192x192", "512x512"} <= sizes
    for icon in manifest["icons"]:
        assert requests.get(urljoin(manifest_url, icon["src"]), timeout=15).ok, icon["src"]


def test_installed_app_runs_in_standalone_mode(home, target):
    if target != "pwa":
        pytest.skip("only meaningful with --target pwa (the site open in the installed app)")
    home.open()
    assert home.driver.execute_script("return window.matchMedia('(display-mode: standalone)').matches;")
