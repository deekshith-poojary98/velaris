"""Velaris capability contracts."""

from velaris_contracts._metadata import CapabilityContract, ContractMetadata
from velaris_contracts.api.v0_1 import (
    CAPABILITY_ID as API_CAPABILITY_ID,
    CONTRACT_METADATA as API_CONTRACT_METADATA,
    CONTRACT_VERSION as API_CONTRACT_VERSION,
    ApiClient,
    Response,
)
from velaris_contracts.browser.v0_1 import (
    CAPABILITY_ID as BROWSER_CAPABILITY_ID,
    CONTRACT_METADATA as BROWSER_CONTRACT_METADATA,
    CONTRACT_VERSION as BROWSER_CONTRACT_VERSION,
    Browser,
)
from velaris_contracts.secrets.v0_1 import (
    CAPABILITY_ID as SECRETS_CAPABILITY_ID,
    CONTRACT_METADATA as SECRETS_CONTRACT_METADATA,
    CONTRACT_VERSION as SECRETS_CONTRACT_VERSION,
    Secrets,
)
from velaris_contracts.target_environment.v0_1 import (
    CAPABILITY_ID as TARGET_ENV_CAPABILITY_ID,
    CONTRACT_METADATA as TARGET_ENV_CONTRACT_METADATA,
    CONTRACT_VERSION as TARGET_ENV_CONTRACT_VERSION,
    TargetEnvironment,
)

# Index of published contracts: capability_id -> (metadata, Protocol class).
# This is an index over the metadata each contract module already defines, so
# introspection tools can enumerate contracts without duplicating descriptions.
CAPABILITY_CONTRACTS: dict[str, CapabilityContract] = {
    API_CAPABILITY_ID: (API_CONTRACT_METADATA, ApiClient),
    BROWSER_CAPABILITY_ID: (BROWSER_CONTRACT_METADATA, Browser),
    SECRETS_CAPABILITY_ID: (SECRETS_CONTRACT_METADATA, Secrets),
    TARGET_ENV_CAPABILITY_ID: (TARGET_ENV_CONTRACT_METADATA, TargetEnvironment),
}

__all__ = [
    "CapabilityContract",
    "ContractMetadata",
    "CAPABILITY_CONTRACTS",
    "API_CAPABILITY_ID",
    "API_CONTRACT_METADATA",
    "API_CONTRACT_VERSION",
    "ApiClient",
    "Response",
    "BROWSER_CAPABILITY_ID",
    "BROWSER_CONTRACT_METADATA",
    "BROWSER_CONTRACT_VERSION",
    "Browser",
    "SECRETS_CAPABILITY_ID",
    "SECRETS_CONTRACT_METADATA",
    "SECRETS_CONTRACT_VERSION",
    "Secrets",
    "TARGET_ENV_CAPABILITY_ID",
    "TARGET_ENV_CONTRACT_METADATA",
    "TARGET_ENV_CONTRACT_VERSION",
    "TargetEnvironment",
]

__version__ = "0.1.0"
