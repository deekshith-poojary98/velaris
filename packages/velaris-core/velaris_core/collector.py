"""Collection dispatcher — route authoring files to adapters, produce TestSpec IR.

This module no longer knows how any single authoring style works. It walks the
given paths, hands each file to the adapter that owns its extension, and
validates the combined TestSpec list. The runner imports only ``collect`` and
remains unaware of authoring styles.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from velaris_core.adapters.base import AuthoringAdapter, default_adapters
from velaris_core.errors import CollectionError
from velaris_core.testspec import TestSpec


@dataclass(frozen=True)
class SourcedSpec:
    """A TestSpec paired with the collection metadata the engine never sees.

    ``source`` is the file the spec was compiled from and ``authoring_style`` is
    the adapter that produced it. This pairing exists only for introspection
    (``velaris collect``); ``TestSpec`` itself stays minimal and execution-only.
    """

    spec: TestSpec
    source: Path
    authoring_style: str


def collect(
    paths: list[str | Path],
    *,
    adapters: list[AuthoringAdapter] | None = None,
) -> list[TestSpec]:
    """Discover tests across authoring styles and return validated TestSpec IR."""
    return [item.spec for item in collect_sourced(paths, adapters=adapters)]


def collect_sourced(
    paths: list[str | Path],
    *,
    adapters: list[AuthoringAdapter] | None = None,
) -> list[SourcedSpec]:
    """Collect tests while retaining source path and authoring style per spec.

    Shares one walk and one validation pass with :func:`collect`, so collection
    rules (duplicate names, capability checks) apply identically to ``run`` and
    ``collect``.
    """
    active = adapters if adapters is not None else default_adapters()

    sourced: list[SourcedSpec] = []
    for path in paths:
        resolved = Path(path)
        if resolved.is_dir():
            sourced.extend(_collect_dir(resolved, active))
        elif resolved.is_file():
            adapter = _adapter_for(resolved, active)
            if adapter is None:
                raise CollectionError(
                    f"No authoring adapter for {resolved} "
                    f"(supported: {_supported_extensions(active)})"
                )
            sourced.extend(_sourced(adapter, resolved))
        else:
            raise CollectionError(f"Path not found: {resolved}")

    validate_testspecs([item.spec for item in sourced])
    return sourced


def _sourced(adapter: AuthoringAdapter, path: Path) -> list[SourcedSpec]:
    style = getattr(adapter, "authoring_style", "unknown")
    return [SourcedSpec(spec=spec, source=path, authoring_style=style)
            for spec in adapter.collect(path)]


def _collect_dir(
    directory: Path, adapters: list[AuthoringAdapter]
) -> list[SourcedSpec]:
    sourced: list[SourcedSpec] = []
    # Adapter order is stable (Python first, then YAML) for deterministic output.
    for adapter in adapters:
        for file_path in sorted(directory.rglob("*")):
            if not file_path.is_file():
                continue
            if file_path.name.startswith("_"):
                continue
            if file_path.suffix.lower() in adapter.extensions:
                sourced.extend(_sourced(adapter, file_path))
    return sourced


def _adapter_for(
    path: Path, adapters: list[AuthoringAdapter]
) -> AuthoringAdapter | None:
    suffix = path.suffix.lower()
    for adapter in adapters:
        if suffix in adapter.extensions:
            return adapter
    return None


def _supported_extensions(adapters: list[AuthoringAdapter]) -> str:
    exts = sorted({ext for adapter in adapters for ext in adapter.extensions})
    return ", ".join(exts) or "(none)"


def validate_testspecs(specs: list[TestSpec]) -> None:
    """Validate the combined TestSpec list before execution.

    Runs regardless of which adapter produced each spec, so authoring styles
    cannot bypass the execution contract.
    """
    seen: set[str] = set()
    for spec in specs:
        if spec.name in seen:
            raise CollectionError(f"Duplicate test name: {spec.name!r}")
        seen.add(spec.name)

        if not spec.capabilities:
            raise CollectionError(f"Test {spec.name!r} declares no capabilities.")
        for capability in spec.capabilities:
            if not isinstance(capability, str) or not capability.strip():
                raise CollectionError(
                    f"Test {spec.name!r} has invalid capability name: {capability!r}"
                )

        if not callable(spec.callable):
            raise CollectionError(f"Test {spec.name!r} has no callable target.")
