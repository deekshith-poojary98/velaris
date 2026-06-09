"""Parse YAML actions into serialized capability calls and build a callable.

An action is a single serialized capability method call:

    browser.open("/login")
    browser.type("#username", "demo")

Parsing is done with Python's ``ast`` module — we read the *structure* of the
expression, we never ``eval`` it. The only runtime reflection is a capability
method lookup (``getattr``). There is no keyword registry, no step matching,
and no DSL.
"""

from __future__ import annotations

import ast
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from velaris_core.errors import CollectionError, VelarisError


@dataclass(frozen=True)
class ParsedAction:
    """One serialized capability call, validated at compile time."""

    capability: str
    method: str
    args: tuple[Any, ...]
    kwargs: dict[str, Any] = field(default_factory=dict)
    source: str = ""


def parse_action(
    text: object,
    declared: set[str] | None,
    *,
    where: str,
) -> ParsedAction:
    """Parse a single action string into a :class:`ParsedAction`.

    Validates (at compile time): syntax, the ``capability.method(...)`` shape,
    that the capability is declared by the test, and that all arguments are
    literals. Method existence and argument count are validated at execution
    (see :func:`build_callable`) because the capability interface is not known
    until the provider is resolved.
    """
    if not isinstance(text, str) or not text.strip():
        raise CollectionError(f"{where}: action must be a non-empty string, got {text!r}.")
    source = text.strip()

    try:
        tree = ast.parse(source, mode="eval")
    except SyntaxError as exc:
        raise CollectionError(f"{where}: invalid action syntax: {source!r} ({exc.msg}).") from exc

    call = tree.body
    if not isinstance(call, ast.Call):
        raise CollectionError(
            f"{where}: action must be a capability call like 'browser.open(\"/\")', got {source!r}."
        )
    func = call.func
    if not isinstance(func, ast.Attribute) or not isinstance(func.value, ast.Name):
        raise CollectionError(
            f"{where}: action must be 'capability.method(...)', got {source!r}."
        )

    capability = func.value.id
    method = func.attr
    if declared is not None and capability not in declared:
        raise CollectionError(
            f"{where}: action {source!r} uses capability {capability!r} "
            f"which is not declared in 'capabilities'."
        )

    args = tuple(_literal(arg, source=source, where=where) for arg in call.args)
    kwargs = {}
    for keyword in call.keywords:
        if keyword.arg is None:
            raise CollectionError(f"{where}: '**' splats are not allowed in {source!r}.")
        kwargs[keyword.arg] = _literal(keyword.value, source=source, where=where)

    return ParsedAction(
        capability=capability,
        method=method,
        args=args,
        kwargs=kwargs,
        source=source,
    )


def _literal(node: ast.expr, *, source: str, where: str) -> Any:
    if isinstance(node, ast.Starred):
        raise CollectionError(f"{where}: '*' splats are not allowed in {source!r}.")
    try:
        return ast.literal_eval(node)
    except (ValueError, SyntaxError) as exc:
        raise CollectionError(
            f"{where}: action arguments must be literals (str, number, bool, None, "
            f"list, dict), got a non-literal in {source!r}."
        ) from exc


def build_callable(
    name: str,
    actions: list[ParsedAction],
    *,
    prefix: str = "generated",
) -> Callable[..., None]:
    """Generate the executable body for an adapter-compiled test.

    The returned callable has the exact same shape the runner expects from a
    Python test: it accepts resolved capabilities as keyword arguments. Each
    action is dispatched via a single capability method lookup.
    """

    def generated_callable(**capabilities: Any) -> None:
        for action in actions:
            target = capabilities[action.capability]
            try:
                method = getattr(target, action.method)
            except AttributeError as exc:
                raise VelarisError(
                    f"action {action.source!r}: capability {action.capability!r} "
                    f"has no method {action.method!r}."
                ) from exc
            try:
                method(*action.args, **action.kwargs)
            except TypeError as exc:
                raise VelarisError(
                    f"action {action.source!r}: invalid call to "
                    f"{action.capability}.{action.method} — {exc}."
                ) from exc

    generated_callable.__name__ = f"{prefix}::{name}"
    generated_callable.__qualname__ = generated_callable.__name__
    return generated_callable
