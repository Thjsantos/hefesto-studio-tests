# Hefesto Studio – mobile test automation

[![Tests](https://github.com/Thjsantos/hefesto-studio-tests/actions/workflows/tests.yml/badge.svg)](https://github.com/Thjsantos/hefesto-studio-tests/actions/workflows/tests.yml) [Latest test report](https://thjsantos.github.io/hefesto-studio-tests/)

Automated mobile tests for [Hefesto Studio](https://thjsantos.github.io/hefesto-studio/), a catalog of resin figures that sends orders through WhatsApp. The site is a PWA with its own repo: [hefesto-studio](https://github.com/Thjsantos/hefesto-studio).

Built with **Python, pytest, Selenium and Appium**, using the **page object pattern**. The tests run on a **real Android phone** (Chrome opening the live site) and, for CI and quick local checks, on desktop Chrome with Pixel 7 emulation.

## What is tested

65 tests in three files:

| File | Covers |
| --- | --- |
| `tests/test_catalog.py` | Product cards, starting prices, category filters, search (with and without results), opening a product from a card |
| `tests/test_product.py` | Name, category and model, scale selector (price and height update), single-price products, WhatsApp quote link and message, gallery limit, YouTube video thumbnail, "not found" page |
| `tests/test_home_and_layout.py` | Home button, "how to buy" steps, order button, phone layout, no horizontal scroll on every page, burger menu, floating Instagram/WhatsApp buttons |

Tests marked `smoke` are the quick checks that the main pages work.

**The tests read the live data.** `utils/site_data.py` downloads the site's `products.json` and the WhatsApp number, so the screen is compared with the source of truth. Product and category tests run once per item found, which means a product added in the CMS is covered automatically.

Not tested on purpose: the "Instalar app" button. Chrome decides when to show it, so a test cannot trigger it reliably.

## Project layout

```
conftest.py            driver fixture (android / emulated), per-product parametrization,
                       screenshot on failure attached to the HTML report
config.py              site URL, Appium URL and phone serial (from environment variables)
pages/                 page objects: base_page, home_page, catalog_page, product_page
tests/                 test_catalog, test_product, test_home_and_layout
utils/site_data.py     reads the live products.json and the WhatsApp number
utils/labels.py        category names
pytest.ini             HTML report in reports/, smoke marker
```

## Setup (Windows, PowerShell)

Requirements: Python 3.12, and Google Chrome for the emulated target.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Settings have working defaults. To change them, set the environment variables `HEFESTO_URL`, `APPIUM_URL` and `ANDROID_UDID` (see `.env.example`), for example `$env:ANDROID_UDID = "R58M..."` in PowerShell.

## Run without a phone (emulated)

Desktop Chrome with Pixel 7 emulation. This is what CI runs.

```powershell
.\.venv\Scripts\python.exe -m pytest --target emulated --headless
```

Drop `--headless` to watch the browser. The full suite takes about 20 seconds.

## Run on a real Android phone

One-time setup:

1. Install Node.js, Java (JDK) and `adb` (Android platform-tools), and make sure `adb` is on your PATH.
2. Install Appium and its driver:
   ```powershell
   npm i -g appium
   appium driver install uiautomator2
   ```
3. On the phone, enable **Developer options** and **USB debugging**, connect it by USB and accept the prompt.
4. Check that the phone is listed:
   ```powershell
   adb devices
   ```

Every run:

```powershell
# terminal 1
appium --allow-insecure=uiautomator2:chromedriver_autodownload

# terminal 2
.\.venv\Scripts\python.exe -m pytest
```

`--target android` is the default. With more than one device connected, set `ANDROID_UDID` to the serial shown by `adb devices`. Appium downloads the ChromeDriver that matches the Chrome version on the phone.

## Useful commands

```powershell
# only the smoke tests
.\.venv\Scripts\python.exe -m pytest --target emulated --headless -m smoke

# one file, or tests matching a name
.\.venv\Scripts\python.exe -m pytest --target emulated tests/test_product.py -k scale
```

## Reports

Every run writes a self-contained HTML report to `reports/report.html`. When a test fails, a screenshot is attached to the report and also saved in `reports/screenshots/`. On GitHub:

- The latest run on `main` is published as a web page: **[latest test report](https://thjsantos.github.io/hefesto-studio-tests/)**.
- Every CI run (pull requests too) shows a short result summary on its Summary page and uploads the report as a downloadable artifact.

## Notes from building it

- The site uses `scroll-behavior: smooth`, so tapping right after `scrollIntoView` hit the wrong spot. `BasePage.tap()` scrolls with `behavior: 'instant'`.
- Catalog and product pages draw their content after `fetch(products.json)`. Tests wait for the element to exist before reading it, including the catalog's WhatsApp link, which JavaScript fills in later.
- HTML collapses repeated spaces (one product name has a double space in the CMS), so displayed names are compared with `Product.display_name`, while the WhatsApp message uses the raw name.
- Selenium's `.text` returns text after CSS `text-transform` (nav links are uppercase), so those comparisons ignore case.
