from __future__ import annotations

from velaris_core.sdk import Registry
from velaris_playwright.provider import register_playwright_providers


def register(registry: Registry) -> None:
    register_playwright_providers(registry)
