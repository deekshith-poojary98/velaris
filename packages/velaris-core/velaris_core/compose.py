"""Config-level composition conventions (Model A — no capability dependencies).

These functions merge capability *bindings* before resolution.
They do not resolve capabilities or pass instances between factories.
"""

from __future__ import annotations

from velaris_core.types import CapabilityBinding


def apply_bootstrap_conventions(
    bindings: dict[str, CapabilityBinding],
) -> dict[str, CapabilityBinding]:
    """Return bindings after documented bootstrap merge rules."""
    merged = dict(bindings)
    merged = _merge_api_base_url_from_target_environment(merged)
    return merged


def _merge_api_base_url_from_target_environment(
    bindings: dict[str, CapabilityBinding],
) -> dict[str, CapabilityBinding]:
    """If ``api.options.base_url`` is unset, copy ``target_environment.endpoints.api``.

    Convention only — not a capability dependency. ``target_environment`` does not
    need to appear in the test's ``@test(...)`` declaration for this merge to run.
    Explicit ``base_url`` in config always wins.
    """
    api = bindings.get("api")
    target = bindings.get("target_environment")
    if api is None or target is None:
        return bindings

    api_options = dict(api.options)
    base_url = api_options.get("base_url")
    if isinstance(base_url, str) and base_url.strip():
        return bindings

    endpoints = target.options.get("endpoints", {})
    if not isinstance(endpoints, dict):
        return bindings
    endpoint = endpoints.get("api")
    if not endpoint:
        return bindings

    api_options["base_url"] = str(endpoint)
    result = dict(bindings)
    result["api"] = CapabilityBinding(
        capability_id=api.capability_id,
        provider=api.provider,
        options=api_options,
    )
    return result
