"""YAML authoring adapter.

Compiles a small YAML document into a TestSpec. Supported keys:

    name: test_login
    capabilities:
      - browser
    actions:                       # optional
      - browser.open("/login")
      - browser.click("#submit")

``actions`` are serialized capability calls — nothing else. No loops, no
conditions, no variables, no templates, no keywords, no user-defined functions.
When ``actions`` are present the adapter compiles them into a normal executable
callable; when absent the test is declaration-only and uses the default no-op
body. Either way the result is an ordinary TestSpec the runner cannot tell
apart from a Python test.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from velaris_core.adapters.yaml_actions import build_callable, parse_action
from velaris_core.errors import CollectionError
from velaris_core.testspec import TestSpec


class YamlAdapter:
    """Compile a ``.yaml`` test (declaration-only or executable) into TestSpec IR."""

    extensions: tuple[str, ...] = (".yaml", ".yml")
    authoring_style: str = "yaml"

    def collect(self, path: Path) -> list[TestSpec]:
        raw = self._parse(path)
        if not isinstance(raw, dict):
            raise CollectionError(
                f"{path}: YAML test must be a mapping with 'name' and 'capabilities'."
            )

        name = raw.get("name")
        if not isinstance(name, str) or not name.strip():
            raise CollectionError(f"{path}: 'name' must be a non-empty string.")
        name = name.strip()

        capabilities = raw.get("capabilities")
        if not isinstance(capabilities, list) or not capabilities:
            raise CollectionError(f"{path}: 'capabilities' must be a non-empty list.")
        for cap in capabilities:
            if not isinstance(cap, str) or not cap.strip():
                raise CollectionError(
                    f"{path}: capability names must be non-empty strings, got {cap!r}."
                )
        capabilities = [c.strip() for c in capabilities]

        callable_obj = self._compile_actions(raw.get("actions"), name, capabilities, path)
        if callable_obj is None:
            return [TestSpec(name=name, capabilities=capabilities)]
        return [TestSpec(name=name, capabilities=capabilities, callable=callable_obj)]

    @staticmethod
    def _compile_actions(
        actions: Any,
        name: str,
        capabilities: list[str],
        path: Path,
    ) -> Any:
        if actions is None:
            return None  # declaration-only
        if not isinstance(actions, list) or not actions:
            raise CollectionError(
                f"{path}: 'actions' must be a non-empty list of capability calls."
            )

        declared = set(capabilities)
        parsed = [
            parse_action(action, declared, where=f"{path} (action {index + 1})")
            for index, action in enumerate(actions)
        ]
        return build_callable(name, parsed, prefix="yaml")

    @staticmethod
    def _parse(path: Path) -> Any:
        try:
            with path.open("r", encoding="utf-8") as handle:
                return yaml.safe_load(handle)
        except yaml.YAMLError as exc:
            raise CollectionError(f"{path}: invalid YAML — {exc}") from exc
