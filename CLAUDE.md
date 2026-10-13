# Hefesto Studio – mobile test automation (pytest + Appium)

Automated tests for the Hefesto Studio website (a catalog of resin figures that sends orders through WhatsApp). The goal of this project is to **practice mobile testing and show it on the owner's GitHub portfolio**. The website itself lives in a separate repo/folder: `C:\Users\tmend\hefesto-studio` (https://github.com/Thjsantos/hefesto-studio, live at https://thjsantos.github.io/hefesto-studio/). Do not change the website from this project.

## Decisions already made by the owner
- Language and framework: **Python with pytest**, page object pattern.
- Tests run on the owner's **own Android phone** through **Appium** (Chrome on the phone opening the live site). No emulator.
- The site is a PWA. The "Instalar app" button is **not** tested (Chrome decides when to show it, tests cannot trigger it reliably).
- Separate project and separate GitHub repo (planned name: `hefesto-studio-tests`, public). New repo: first push is fine, afterwards use branch + PR if the owner asks for it.
- Commits: use the GitHub no-reply email (`42556262+Thjsantos@users.noreply.github.com`), not the Gmail address.
- The owner writes in English and Portuguese. Code, comments and README in English.

## What is built (all in this folder)
- `conftest.py` – `driver` fixture. `--target android` (default, real phone via Appium) or `--target emulated` (desktop Chrome with Pixel 7 emulation, `--headless` for CI). Screenshot saved and attached to the HTML report on failure. `pytest_generate_tests` runs tests once per product / category found in the live `products.json` (fixtures `product`, `scaled_product`, `multi_scale_product`, `plain_product`, `video_product`, `category`).
- `pages/` – `base_page.py` (open, waits, `tap()` with instant scroll, menu, floating buttons), `home_page.py`, `catalog_page.py`, `product_page.py`.
- `utils/site_data.py` – reads the live `data/products.json` and the WhatsApp number from `products.js` so tests compare the screen with the source of truth. `Product.display_name` collapses repeated spaces (the product "War-  Darksiders" has a double space in the CMS, HTML collapses it). `utils/labels.py` – category names.
- `tests/` – 65 tests: `test_catalog.py`, `test_product.py`, `test_home_and_layout.py` (smoke marker on the main ones).
- `config.py`, `.env.example` (HEFESTO_URL, APPIUM_URL, ANDROID_UDID), `pytest.ini` (HTML report in `reports/`), `requirements.txt`, `.gitignore`.

## Status
- The full suite passed 8 runs in a row with `--target emulated --headless` (65 passed, about 20 s). **Never run on the real phone yet.**
- Not a git repo yet. **Still to do:** README (purpose, setup on Windows, phone setup, how to run, project layout), GitHub Actions workflow running `pytest --target emulated --headless` (and publishing the HTML report), first commit and public GitHub repo, first run on the phone, fix whatever the real phone shows.

## Lessons learned (keep in mind)
- The site CSS has `scroll-behavior: smooth`; tapping right after `scrollIntoView` hit the wrong spot. `tap()` scrolls with `behavior: 'instant'`.
- The product page and catalog draw their content after `fetch(products.json)`. Always wait for the element (scale buttons, cards) before reading it. The catalog's WhatsApp link is filled by JavaScript, so wait for a non-empty `href`.
- HTML collapses repeated spaces, compare displayed names with `display_name`; the WhatsApp message uses the raw name.
- Selenium's `.text` returns text after CSS `text-transform` (nav links are uppercase), compare case-insensitively or use `textContent`.

## Environment on the owner's PC (Windows 11, PowerShell)
- Installed: Python 3.12 (`python`), Node 24, Java 25, `adb` in `%LOCALAPPDATA%\Android\platform-tools` (on the user PATH), Appium 3.8 (`npm i -g appium`) with the `uiautomator2` driver. Android Studio is not installed and not needed.
- Virtual environment: `.venv` (`.\.venv\Scripts\python.exe -m pytest ...`).
- Run on the phone: enable Developer options and USB debugging, connect by USB and accept the prompt, check `adb devices`, start Appium with `appium --allow-insecure=uiautomator2:chromedriver_autodownload`, then `.\.venv\Scripts\python.exe -m pytest`.
- Run without a phone: `.\.venv\Scripts\python.exe -m pytest --target emulated --headless`.
- Note for the shell tool: very long PowerShell commands that mix `Remove-Item` with quoted paths containing spaces can be blocked by the safety check, run them as separate commands.
