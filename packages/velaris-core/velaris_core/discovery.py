"""Test discovery and introspection — the read-only half of collection.

``velaris collect`` runs the collection stage (Collect → TestSpec) and stops.
No resolution, no provider creation, no execution, no reporting. This module
turns the engine's internal :class:`~velaris_core.testspec.TestSpec` into a
small, user-facing :class:`CollectedTest` view and renders it as a human tree
or JSON. It deliberately does not expose the callable or any execution detail.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from velaris_core.adapters.base import AuthoringAdapter
from velaris_core.collector import collect_sourced


@dataclass(frozen=True)
class CollectedTest:
    """What a user can know about a test before running it.

    This is the first public serialization of TestSpec-like information. It
    carries only discovery facts — name, capabilities, source, authoring style —
    never the callable or resolved providers.
    """

    name: str
    authoring_style: str
    source: str
    capabilities: list[str]


def discover(
    paths: list[str | Path],
    *,
    adapters: list[AuthoringAdapter] | None = None,
    base: str | Path | None = None,
) -> list[CollectedTest]:
    """Collect tests and return introspection records (no execution).

    ``source`` paths are made relative to ``base`` (defaulting to the current
    working directory) for readable output, falling back to the absolute path
    when the file lives outside ``base``.
    """
    base_path = Path(base) if base is not None else Path.cwd()
    return [
        CollectedTest(
            name=item.spec.name,
            authoring_style=item.authoring_style,
            source=_display_source(item.source, base_path),
            capabilities=list(item.spec.capabilities),
        )
        for item in collect_sourced(paths, adapters=adapters)
    ]


def _display_source(source: Path, base: Path) -> str:
    try:
        return str(source.resolve().relative_to(base.resolve()))
    except ValueError:
        return str(source)


def format_tree(tests: list[CollectedTest]) -> str:
    """Render collected tests as the default human-readable tree."""
    count = len(tests)
    header = f"Found {count} test" if count == 1 else f"Found {count} tests"
    if not tests:
        return header

    blocks: list[str] = [header]
    for test in tests:
        lines = [
            "",
            test.name,
            f"  source: {test.source}",
            f"  authoring_style: {test.authoring_style}",
            "  capabilities:",
        ]
        lines.extend(f"    - {cap}" for cap in test.capabilities)
        blocks.append("\n".join(lines))
    return "\n".join(blocks)


def to_json(tests: list[CollectedTest]) -> str:
    """Render collected tests as a stable, indented JSON array."""
    return json.dumps([asdict(test) for test in tests], indent=2)
