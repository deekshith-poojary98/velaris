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
def test(*capabilities: str, tags: list[str] | None = None) -> Callable[[F], F]: ...


def test(*capabilities: str | F, tags: list[str] | None = None) -> F | Callable[[F], F]:
    """Mark a function as a Velaris test and declare required capabilities and tags.

    Explicit declaration (recommended)::

        @test("api", "secrets", tags=["smoke"])
        def test_checkout(api, secrets): ...

    Bare decorator infers capabilities from parameter names (in signature order)::

        @test
        def test_users(api): ...
    """
    if len(capabilities) == 1 and callable(capabilities[0]) and tags is None:
        func = capabilities[0]
        caps = _capabilities_from_params(func)
        _validate_capabilities(func, caps)
        func.__velaris_test__ = True  # type: ignore[attr-defined]
        func.__velaris_capabilities__ = caps  # type: ignore[attr-defined]
        func.__velaris_tags__ = []  # type: ignore[attr-defined]
        return func

    cap_list = [str(cap) for cap in capabilities]
    actual_tags = tags if tags is not None else []

    from velaris_core.testspec import _validate_tags
    _validate_tags(None, actual_tags)

    def decorator(func: F) -> F:
        nonlocal cap_list
        if not cap_list:
            caps = _capabilities_from_params(func)
        else:
            caps = cap_list
        _validate_capabilities(func, caps)
        _validate_tags(func.__name__, actual_tags)
        func.__velaris_test__ = True  # type: ignore[attr-defined]
        func.__velaris_capabilities__ = caps  # type: ignore[attr-defined]
        func.__velaris_tags__ = actual_tags  # type: ignore[attr-defined]
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
