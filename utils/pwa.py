"""Finds the installed Hefesto Studio app (a Chrome WebAPK) on the connected phone."""
import os
import shutil
import subprocess
from urllib.parse import urlparse

import config


def _adb() -> str:
    found = shutil.which("adb")
    if found:
        return found
    for root in (os.getenv("ANDROID_HOME"), os.getenv("ANDROID_SDK_ROOT"),
                 os.path.join(os.getenv("LOCALAPPDATA", ""), "Android")):
        candidate = os.path.join(root or "", "platform-tools", "adb.exe" if os.name == "nt" else "adb")
        if os.path.exists(candidate):
            return candidate
    raise RuntimeError("adb not found. Add platform-tools to PATH or set HEFESTO_PWA_PACKAGE.")


def _shell(*args: str) -> str:
    cmd = [_adb()] + (["-s", config.ANDROID_UDID] if config.ANDROID_UDID else []) + ["shell", *args]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout


def launch_activity(package: str) -> str:
    """The activity that opens the app (its launcher icon). Appium needs it to bring the app to the front."""
    output = _shell("cmd", "package", "resolve-activity", "--brief", "-c", "android.intent.category.LAUNCHER", package)
    for line in output.splitlines():
        if line.strip().startswith(package + "/"):
            return line.strip().split("/", 1)[1]
    raise RuntimeError(f"Could not find the launcher activity of {package}.")


def find_package() -> str:
    """The package of the installed app whose scope is the site under test.
    HEFESTO_PWA_PACKAGE overrides the search."""
    if config.PWA_PACKAGE:
        return config.PWA_PACKAGE
    site = urlparse(config.BASE_URL)
    for line in _shell("pm", "list", "packages", "webapk").splitlines():
        package = line.replace("package:", "").strip()
        if package and f'Authority: "{site.netloc}"' in _shell("dumpsys", "package", package) \
                and site.path in _shell("dumpsys", "package", package):
            return package
    raise RuntimeError(f"No installed app found for {config.BASE_URL}. Check that the phone is listed by "
                       "`adb devices`, and that the app is installed from Chrome (menu > Install app). "
                       "Or set HEFESTO_PWA_PACKAGE.")
