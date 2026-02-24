"""Compatibility shim for legacy ``selenium_firefox`` imports.

Older MoneyPrinter forks imported ``from selenium_firefox import *``.
That third-party package is incompatible with recent Selenium releases
because it imports ``selenium.webdriver.firefox.firefox_binary``.

This local module keeps those legacy imports working by re-exporting the
same Selenium symbols used in the project.
"""

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common import keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

try:
    # Selenium < 4.11
    from selenium.webdriver.firefox.firefox_binary import FirefoxBinary  # type: ignore
except Exception:  # pragma: no cover - only used on newer Selenium versions
    FirefoxBinary = None  # Backward-compatible placeholder.

__all__ = [
    "webdriver",
    "exceptions",
    "keys",
    "By",
    "Options",
    "Service",
    "GeckoDriverManager",
    "FirefoxBinary",
]
