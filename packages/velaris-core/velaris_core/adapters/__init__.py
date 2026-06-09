"""Authoring adapters: compile a frontend file into TestSpec IR.

Every adapter turns one authoring style (Python, YAML, future BDD) into the
same :class:`~velaris_core.testspec.TestSpec`. The runner, resolver, and
reporting never know which adapter produced a spec.
"""

from __future__ import annotations

from velaris_core.adapters.base import AuthoringAdapter, default_adapters
from velaris_core.adapters.bdd_adapter import BddAdapter
from velaris_core.adapters.python_adapter import PythonAdapter
from velaris_core.adapters.yaml_adapter import YamlAdapter

__all__ = [
    "AuthoringAdapter",
    "BddAdapter",
    "PythonAdapter",
    "YamlAdapter",
    "default_adapters",
]
