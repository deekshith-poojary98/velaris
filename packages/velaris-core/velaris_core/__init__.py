"""Velaris core — configuration, registry, resolver, execution."""

from velaris_core.bootstrap import register_builtin_providers
from velaris_core.config import KNOWN_PROVIDERS, load_config, require_binding
from velaris_core.errors import (
    CapabilitySetupError,
    CollectionError,
    ConfigError,
    DuplicateProviderError,
    VelarisError,
    ProviderNotConfiguredError,
    UnknownProviderError,
)
from velaris_core.registry import Registry
from velaris_core.resolver import Resolver
from velaris_core.runner import run
from velaris_core.testspec import TestSpec
from velaris_core.types import CapabilityBinding, VelarisConfig, ProviderFactory, Teardown

__all__ = [
    "CapabilityBinding",
    "CapabilitySetupError",
    "CollectionError",
    "ConfigError",
    "DuplicateProviderError",
    "KNOWN_PROVIDERS",
    "VelarisConfig",
    "VelarisError",
    "ProviderFactory",
    "ProviderNotConfiguredError",
    "Registry",
    "Resolver",
    "Teardown",
    "TestSpec",
    "UnknownProviderError",
    "load_config",
    "register_builtin_providers",
    "require_binding",
    "run",
]

__version__ = "0.1.0"
