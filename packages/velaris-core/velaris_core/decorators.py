"""Test authoring decorators."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import Any, TypeVar, overload

from velaris_core.errors import CollectionError

F = TypeVar("F", bound=Callable[..., Any])


@overload
def test(func: F) -> F: ...


@overload
def test(*capabilities: str) -> Callable[[F], F]: ...


def test(*capabilities: str | F) -> F | Callable[[F], F]:
    """Mark a function as a Velaris test and declare required capabilities.

    Explicit declaration (recommended)::

        @test("api", "secrets")
        def test_checkout(api, secrets): ...

    Bare decorator infers capabilities from parameter names (in signature order)::

        @test
        def test_users(api): ...
    """
    if len(capabilities) == 1 and callable(capabilities[0]):
        func = capabilities[0]
        caps = _capabilities_from_params(func)
        _validate_capabilities(func, caps)
        func.__velaris_test__ = True  # type: ignore[attr-defined]
        func.__velaris_capabilities__ = caps  # type: ignore[attr-defined]
        return func

    cap_list = [str(cap) for cap in capabilities]

    def decorator(func: F) -> F:
        _validate_capabilities(func, cap_list)
        func.__velaris_test__ = True  # type: ignore[attr-defined]
        func.__velaris_capabilities__ = cap_list  # type: ignore[attr-defined]
        return func

    return decorator


def _capabilities_from_params(func: Callable[..., Any]) -> list[str]:
    return list(inspect.signature(func).parameters)


def _validate_capabilities(func: Callable[..., Any], capabilities: list[str]) -> None:
    params = list(inspect.signature(func).parameters)
    if not capabilities:
        raise CollectionError(
            f"Test {func.__name__!r} must declare at least one capability "
            f"via @test('capability', ...) or accept capability parameters."
        )
    for cap in capabilities:
        if cap not in params:
            raise CollectionError(
                f"Test {func.__name__!r} declares capability {cap!r} "
                f"but has no parameter named {cap!r}."
            )
    if set(capabilities) != set(params):
        raise CollectionError(
            f"Test {func.__name__!r} capability list {capabilities!r} "
            f"does not match parameters {params!r}."
        )
