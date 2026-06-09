"""Public API for Velaris capability plugin authors.

Import from this module only when authoring providers. Framework internals
(registry resolution, runner, reporting) should not be required reading.
"""

from __future__ import annotations

from velaris_core.plugin_loader import register_manual_plugins
from velaris_core.provider_context import pop_emit
from velaris_core.registry import Registry
from velaris_core.reporting import EMIT_OPTION_KEY, capability_observed
from velaris_core.types import ProviderFactory, Teardown

__all__ = [
    "EMIT_OPTION_KEY",
    "ProviderFactory",
    "Registry",
    "Teardown",
    "capability_observed",
    "pop_emit",
    "register_manual_plugins",
]
