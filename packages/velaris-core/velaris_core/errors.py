"""Velaris exception hierarchy."""


class VelarisError(Exception):
    """Base exception for all Velaris errors."""


class ConfigError(VelarisError):
    """Invalid or missing configuration."""


class ProviderNotConfiguredError(ConfigError):
    """No provider bound for a capability."""


class UnknownProviderError(ConfigError):
    """Configured provider is not registered."""


class DuplicateProviderError(VelarisError):
    """Provider already registered for a capability."""


class CapabilitySetupError(VelarisError):
    """Capability factory setup failed."""


class CollectionError(VelarisError):
    """Test discovery or collection failed."""
