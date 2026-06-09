"""Manual plugin registration from a project-local ``velaris_plugins`` module."""

from __future__ import annotations

import importlib.util
import sys
from collections.abc import Sequence
from pathlib import Path

from velaris_core.registry import Registry


def register_manual_plugins(
    registry: Registry,
    *,
    search_dirs: Sequence[Path | str] | None = None,
) -> bool:
    """Load ``velaris_plugins.py`` and call ``register(registry)`` if present.

    Searches ``search_dirs`` first, then the current working directory.
    Returns ``True`` when a module was loaded and invoked.
    """
    candidates: list[Path] = []
    if search_dirs:
        candidates.extend(Path(directory) for directory in search_dirs)
    candidates.append(Path.cwd())

    seen: set[Path] = set()
    for directory in candidates:
        resolved = directory.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)

        module_path = resolved / "velaris_plugins.py"
        if not module_path.is_file():
            continue

        _load_and_register(module_path, registry)
        return True
    return False


def _load_and_register(module_path: Path, registry: Registry) -> None:
    module_name = "velaris_plugins"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load plugin module from {module_path}")

    module = importlib.util.module_from_spec(spec)
    module_dir = str(module_path.parent)
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)

    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    register = getattr(module, "register", None)
    if not callable(register):
        raise TypeError(
            f"{module_path} must define register(registry: Registry) -> None"
        )
    register(registry)
