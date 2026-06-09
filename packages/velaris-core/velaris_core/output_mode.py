"""Terminal output verbosity for stdout reporting."""

from __future__ import annotations

from enum import Enum


class OutputMode(str, Enum):
    """How much execution detail to print to the terminal."""

    DEFAULT = "default"
    VERBOSE = "verbose"
    DEBUG = "debug"
