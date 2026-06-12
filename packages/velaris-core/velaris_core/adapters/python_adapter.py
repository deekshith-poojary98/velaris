"""Python authoring adapter.

Discovers ``@test``-decorated functions in a Python module and compiles each
into a TestSpec. Behavior is identical to the original collector.
"""

from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path
from typing import Any

from velaris_core.errors import CollectionError
from velaris_core.testspec import TestSpec


class PythonAdapter:
    """Compile ``@test`` functions in a ``.py`` module into TestSpec IR."""

    extensions: tuple[str, ...] = (".py",)
    authoring_style: str = "python"

    def collect(self, path: Path) -> list[TestSpec]:
        module = self._load_module(path)
        specs: list[TestSpec] = []
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if not getattr(obj, "__velaris_test__", False):
                continue
            capabilities = list(getattr(obj, "__velaris_capabilities__", []))
            tags = list(getattr(obj, "__velaris_tags__", []))
            specs.append(
                TestSpec(name=name, capabilities=capabilities, callable=obj, tags=tags)
            )
        return specs

    @staticmethod
    def _load_module(filepath: Path) -> Any:
        name = f"velaris_collected_{filepath.stem}_{abs(hash(filepath))}"
        spec = importlib.util.spec_from_file_location(name, filepath)
        if spec is None or spec.loader is None:
            raise CollectionError(f"Cannot import {filepath}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
