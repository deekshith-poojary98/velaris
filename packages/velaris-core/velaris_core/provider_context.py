"""Provider helpers for optional event emission."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from velaris_core.reporting import EMIT_OPTION_KEY


def pop_emit(options: dict[str, Any]) -> tuple[dict[str, Any], Callable[[object], None] | None]:
    """Remove the internal emit callback from provider options."""
    cleaned = dict(options)
    emit = cleaned.pop(EMIT_OPTION_KEY, None)
    if callable(emit):
        return cleaned, emit
    return cleaned, None
