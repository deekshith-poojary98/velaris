"""Registry capability= keyword alias."""

from velaris_core.registry import Registry
from velaris_core.types import Teardown


def test_register_capability_keyword() -> None:
    registry = Registry()

    def factory(options: dict) -> tuple[str, Teardown]:
        return "ok", lambda: None

    registry.register(capability="api", provider="requests", factory=factory)
    instance, _ = registry.get_factory("api", "requests")({})
    assert instance == "ok"
