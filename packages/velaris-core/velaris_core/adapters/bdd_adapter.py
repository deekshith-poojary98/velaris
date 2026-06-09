"""Minimal BDD authoring adapter.

Compiles a tiny Gherkin feature into TestSpec IR. Given/When/Then lines are
serialized capability calls — identical to executable YAML ``actions``. The
adapter infers ``capabilities`` from the step calls and reuses the YAML action
parser and callable generator.

This is not Behave or Cucumber. It validates that BDD is just another adapter.
"""

from __future__ import annotations

from pathlib import Path

from velaris_core.adapters.bdd_parser import parse_feature
from velaris_core.adapters.yaml_actions import build_callable, parse_action
from velaris_core.testspec import TestSpec


class BddAdapter:
    """Compile a ``.feature`` scenario into TestSpec IR."""

    extensions: tuple[str, ...] = (".feature",)

    def collect(self, path: Path) -> list[TestSpec]:
        specs: list[TestSpec] = []
        for scenario in parse_feature(path):
            parsed = [
                parse_action(
                    step,
                    None,
                    where=f"{path} ({scenario.name}, step {index + 1})",
                )
                for index, step in enumerate(scenario.steps)
            ]
            capabilities = sorted({action.capability for action in parsed})
            callable_obj = build_callable(scenario.name, parsed, prefix="bdd")
            specs.append(
                TestSpec(
                    name=scenario.name,
                    capabilities=capabilities,
                    callable=callable_obj,
                )
            )
        return specs
