"""Authoring adapter contract.

The smallest abstraction that lets multiple frontends feed one engine:
an adapter declares which file extensions it owns and compiles a single file
into a list of TestSpec.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from velaris_core.testspec import TestSpec


@runtime_checkable
class AuthoringAdapter(Protocol):
    """Compile one authoring file into TestSpec IR.

    ``extensions`` are lowercase suffixes including the dot (e.g. ``".py"``).
    ``collect`` receives a single file path and returns zero or more specs.
    """

    extensions: tuple[str, ...]

    def collect(self, path: Path) -> list[TestSpec]:
        """Compile the file at ``path`` into TestSpec IR."""
        ...


def default_adapters() -> list[AuthoringAdapter]:
    """Built-in adapters, in collection order."""
    # Imported here to avoid a circular import at module load time.
    from velaris_core.adapters.bdd_adapter import BddAdapter
    from velaris_core.adapters.python_adapter import PythonAdapter
    from velaris_core.adapters.yaml_adapter import YamlAdapter

    return [PythonAdapter(), YamlAdapter(), BddAdapter()]
