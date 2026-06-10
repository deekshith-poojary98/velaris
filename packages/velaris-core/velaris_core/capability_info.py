"""Capability introspection — the read-only "what can Velaris do" surface.

Backs ``velaris capabilities`` and ``velaris capability <id>``. It composes two
sources that already exist, without duplicating either:

* **Contracts** (``velaris_contracts.CAPABILITY_CONTRACTS``) supply the
  description and the Protocol whose methods/properties describe the surface.
* **The registry** (built-ins + manual plugins) supplies the providers
  registered for each capability.

It performs no resolution and creates no providers — it only reads metadata.
"""

from __future__ import annotations

import inspect
from dataclasses import asdict, dataclass

from velaris_contracts import CAPABILITY_CONTRACTS

from velaris_core.bootstrap import register_builtin_providers
from velaris_core.registry import Registry


@dataclass(frozen=True)
class CapabilityMetadata:
    """A user-facing description of one capability.

    Derived at runtime from the contract Protocol and the provider registry;
    nothing here is hand-maintained alongside the contracts.
    """

    id: str
    description: str
    methods: list[str]
    providers: list[str]


def _build_registry() -> Registry:
    """A registry populated exactly like a run would, including manual plugins."""
    registry = Registry()
    register_builtin_providers(registry)
    return registry


def _signature(name: str, func: object) -> str:
    """Render ``name(param, ...)`` from a callable, dropping ``self``/``cls``."""
    try:
        params = inspect.signature(func).parameters  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return f"{name}(...)"
    names = [
        p.name
        for p in params.values()
        if p.name not in ("self", "cls")
        and p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)
    ]
    return f"{name}({', '.join(names)})"


def _protocol_surface(protocol: object) -> list[str]:
    """List a Protocol's public methods and properties in definition order.

    Methods render as ``name(args)``; read-only properties render as bare
    ``name`` so the surface stays readable in both tree and JSON output.
    """
    surface: list[str] = []
    for name, member in vars(protocol).items():
        if name.startswith("_"):
            continue
        if isinstance(member, property):
            surface.append(name)
        elif inspect.isfunction(member):
            surface.append(_signature(name, member))
    return surface


def list_capabilities() -> list[str]:
    """All capability IDs known to Velaris: contracts plus registered providers."""
    registry = _build_registry()
    ids = set(CAPABILITY_CONTRACTS) | set(registry.list_capabilities())
    return sorted(ids)


def describe_capability(capability_id: str) -> CapabilityMetadata:
    """Build full metadata for one capability from contracts + registry.

    Capabilities without a published contract (e.g. plugin-only capabilities)
    still resolve: they report their providers with an empty method surface.
    """
    registry = _build_registry()
    known = set(CAPABILITY_CONTRACTS) | set(registry.list_capabilities())
    if capability_id not in known:
        available = ", ".join(sorted(known)) or "(none)"
        raise UnknownCapabilityError(
            f"Unknown capability {capability_id!r}.\n  Available: {available}"
        )

    contract = CAPABILITY_CONTRACTS.get(capability_id)
    if contract is not None:
        metadata, protocol = contract
        description = metadata.get("description", "")
        methods = _protocol_surface(protocol)
    else:
        description = ""
        methods = []

    return CapabilityMetadata(
        id=capability_id,
        description=description,
        methods=methods,
        providers=registry.list_providers(capability_id),
    )


class UnknownCapabilityError(Exception):
    """Raised when introspecting a capability Velaris does not know about."""


def format_capabilities_list(capability_ids: list[str]) -> str:
    """Render the ``velaris capabilities`` tree."""
    if not capability_ids:
        return "No capabilities available"
    lines = ["Available capabilities", ""]
    lines.extend(capability_ids)
    return "\n".join(lines)


def format_capability_detail(meta: CapabilityMetadata) -> str:
    """Render the ``velaris capability <id>`` detail block."""
    lines = [f"Capability: {meta.id}", ""]

    lines.append("Description:")
    lines.append(meta.description or "(no description available)")
    lines.append("")

    lines.append("Methods:")
    if meta.methods:
        lines.extend(f"  {method}" for method in meta.methods)
    else:
        lines.append("  (no contract methods published)")
    lines.append("")

    lines.append("Providers:")
    if meta.providers:
        lines.extend(f"  {provider}" for provider in meta.providers)
    else:
        lines.append("  (none registered)")

    return "\n".join(lines)


def capabilities_to_json(capability_ids: list[str]) -> str:
    """Render the capability list as JSON."""
    import json

    return json.dumps(capability_ids, indent=2)


def capability_to_json(meta: CapabilityMetadata) -> str:
    """Render one capability's metadata as JSON."""
    import json

    return json.dumps(asdict(meta), indent=2)
