"""Minimal Gherkin parser for BDD adapter (architectural validation only).

Supported syntax::

    Feature: Login

    Scenario: User logs in

      Given browser.open("/login")
      When browser.type("#username", "demo")
      Then browser.click("#submit")

Given/When/Then lines are serialized capability calls — the keywords carry no
semantics beyond ordering. There is no keyword engine, step registry, or
natural-language parsing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from velaris_core.errors import CollectionError

_FEATURE = re.compile(r"^\s*Feature:\s*(.+?)\s*$", re.IGNORECASE)
_SCENARIO = re.compile(r"^\s*Scenario:\s*(.+?)\s*$", re.IGNORECASE)
_STEP = re.compile(r"^\s*(Given|When|Then)\s+(.+?)\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class ParsedScenario:
    """One scenario compiled from a ``.feature`` file."""

    feature: str
    name: str
    steps: tuple[str, ...]
    tags: tuple[str, ...]


def parse_feature(path: Path) -> list[ParsedScenario]:
    """Parse a minimal ``.feature`` file into one or more scenarios."""
    text = path.read_text(encoding="utf-8")
    feature_name = ""
    feature_tags: list[str] = []
    scenarios: list[ParsedScenario] = []
    current_name: str | None = None
    current_steps: list[str] = []
    current_tags: list[str] = []
    scenario_tags: list[str] = []

    def finalize() -> None:
        nonlocal current_name, current_steps, scenario_tags
        if current_name is None:
            return
        if not current_steps:
            raise CollectionError(
                f"{path}: scenario {current_name!r} must contain at least one step."
            )
        from velaris_core.testspec import _validate_tags
        combined_tags = feature_tags + scenario_tags
        try:
            _validate_tags(current_name, combined_tags)
        except CollectionError as exc:
            raise CollectionError(f"{path}: {exc}") from exc

        scenarios.append(
            ParsedScenario(
                feature=feature_name or "Feature",
                name=current_name,
                steps=tuple(current_steps),
                tags=tuple(combined_tags),
            )
        )
        current_name = None
        current_steps = []
        scenario_tags = []

    for line_no, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        where = f"{path}:{line_no}"

        if line.startswith("@"):
            parts = line.split()
            for part in parts:
                if not part.startswith("@"):
                    raise CollectionError(f"{where}: invalid tag format {part!r}.")
                tag_name = part[1:]
                if not tag_name:
                    raise CollectionError(f"{where}: tag name cannot be empty.")
                current_tags.append(tag_name)
            continue

        feature_match = _FEATURE.match(line)
        if feature_match:
            finalize()
            feature_name = feature_match.group(1).strip()
            feature_tags = list(current_tags)
            current_tags = []
            continue

        scenario_match = _SCENARIO.match(line)
        if scenario_match:
            finalize()
            current_name = scenario_match.group(1).strip()
            if not current_name:
                raise CollectionError(f"{where}: scenario name must be non-empty.")
            scenario_tags = list(current_tags)
            current_tags = []
            continue

        step_match = _STEP.match(line)
        if step_match:
            if current_tags:
                raise CollectionError(f"{where}: tags {current_tags} cannot be placed before a step.")
            if current_name is None:
                raise CollectionError(
                    f"{where}: step must appear inside a Scenario block."
                )
            current_steps.append(step_match.group(2).strip())
            continue

        raise CollectionError(
            f"{where}: unsupported line {raw!r}. "
            "Only Feature, Scenario, and Given/When/Then capability calls are supported."
        )

    finalize()
    if current_tags:
        raise CollectionError(f"{path}: orphaned tags {current_tags} at the end of file.")
    if not scenarios:
        raise CollectionError(f"{path}: feature file must contain at least one scenario.")
    return scenarios
