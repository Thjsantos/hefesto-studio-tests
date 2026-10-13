"""Test settings, read from environment variables (see .env.example)."""
import os

BASE_URL = os.getenv("HEFESTO_URL", "https://thjsantos.github.io/hefesto-studio/").rstrip("/") + "/"
APPIUM_URL = os.getenv("APPIUM_URL", "http://127.0.0.1:4723")
ANDROID_UDID = os.getenv("ANDROID_UDID", "")
PWA_PACKAGE = os.getenv("HEFESTO_PWA_PACKAGE", "")  # only for --target pwa; found automatically when empty

DEFAULT_TIMEOUT = 15  # seconds to wait for an element
