"""Shared fixtures: starts the browser session (real Android phone through Appium, or Chrome with
mobile emulation), loads the site data and takes a screenshot when a test fails."""
import base64
from pathlib import Path

import pytest
from selenium import webdriver as selenium_webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

import config
from pages.catalog_page import CatalogPage
from pages.home_page import HomePage
from pages.product_page import ProductPage
from utils import site_data
from utils.labels import categories_in_use

REPORTS = Path(__file__).parent / "reports"


def pytest_addoption(parser):
    parser.addoption("--target", choices=["android", "emulated"], default="android",
                     help="android: real phone through Appium (default). "
                          "emulated: desktop Chrome with phone emulation, no phone or Appium needed (used in CI).")
    parser.addoption("--headless", action="store_true", help="Only for --target emulated.")


def _android_driver():
    from appium import webdriver as appium_webdriver
    from appium.options.android import UiAutomator2Options

    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.browser_name = "Chrome"
    options.no_reset = True
    options.new_command_timeout = 300
    options.native_web_screenshot = True
    options.set_capability("appium:chromedriverAutodownload", True)
    options.set_capability("goog:chromeOptions", {"args": ["--no-first-run", "--disable-fre"]})
    if config.ANDROID_UDID:
        options.udid = config.ANDROID_UDID
    return appium_webdriver.Remote(config.APPIUM_URL, options=options)


def _emulated_driver(headless: bool):
    options = ChromeOptions()
    options.add_experimental_option("mobileEmulation", {"deviceName": "Pixel 7"})
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    return selenium_webdriver.Chrome(options=options)


@pytest.fixture(scope="session")
def driver(request):
    if request.config.getoption("--target") == "android":
        drv = _android_driver()
    else:
        drv = _emulated_driver(request.config.getoption("--headless"))
    drv.implicitly_wait(0)  # explicit waits only
    yield drv
    drv.quit()


_PRODUCTS_CACHE = []


def _all_products():
    if not _PRODUCTS_CACHE:
        _PRODUCTS_CACHE.extend(site_data.load_products())
    return _PRODUCTS_CACHE


def pytest_generate_tests(metafunc):
    """Runs a test once per product (or per category) found in the live products.json, so new
    products added in the CMS are covered automatically."""
    selectors = {
        "product": lambda p: True,
        "scaled_product": lambda p: bool(p.scales),
        "multi_scale_product": lambda p: len(p.scales) > 1,
        "plain_product": lambda p: not p.scales,
        "video_product": lambda p: bool(p.video_id),
    }
    for fixture_name, keep in selectors.items():
        if fixture_name in metafunc.fixturenames:
            chosen = [p for p in _all_products() if keep(p)]
            metafunc.parametrize(fixture_name, chosen, ids=[p.name for p in chosen])
    if "category" in metafunc.fixturenames:
        used = categories_in_use(_all_products())
        metafunc.parametrize("category", used, ids=used)


@pytest.fixture(scope="session")
def products():
    return _all_products()


@pytest.fixture(scope="session")
def whatsapp_number():
    return site_data.whatsapp_number()


@pytest.fixture
def home(driver):
    return HomePage(driver)


@pytest.fixture
def catalog(driver):
    return CatalogPage(driver)


@pytest.fixture
def product_page(driver):
    return ProductPage(driver)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    drv = item.funcargs.get("driver") if hasattr(item, "funcargs") else None
    if report.when == "call" and report.failed and drv is not None:
        try:
            png = drv.get_screenshot_as_png()
        except Exception:
            return
        shots = REPORTS / "screenshots"
        shots.mkdir(parents=True, exist_ok=True)
        (shots / f"{item.name.replace('/', '_')}.png").write_bytes(png)
        try:
            import pytest_html
            report.extras = getattr(report, "extras", []) + [
                pytest_html.extras.image(base64.b64encode(png).decode(), "screenshot at failure")]
        except ImportError:
            pass
