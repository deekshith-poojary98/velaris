"""TestSpec IR — format-agnostic test representation for the execution engine."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


def noop_test(**_kwargs: Any) -> None:
    """Default body for declaration-only tests (e.g. YAML).

    Accepts any injected capability kwargs and does nothing. The runner still
    resolves capabilities and runs lifecycle/teardown — only the body is empty.
    """
    return None


@dataclass(frozen=True)
class TestSpec:
    """Minimal internal representation of one executable test.

    ``callable`` defaults to :func:`noop_test` so authoring styles that declare
    a test without a Python body (YAML, future BDD) still produce a valid spec.
    The runner is unaware of which authoring style produced the spec.
    """

    __test__ = False  # pytest: not a test class

    name: str
    capabilities: list[str]
    callable: Callable[..., Any] = field(default=noop_test)
