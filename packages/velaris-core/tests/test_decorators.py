"""Capability declaration tests."""

import pytest

from velaris_core.decorators import test as velaris_test
from velaris_core.errors import CollectionError


def test_explicit_capabilities() -> None:
    @velaris_test("api", "secrets")
    def sample(api, secrets) -> None:
        pass

    assert sample.__velaris_capabilities__ == ["api", "secrets"]


def test_bare_decorator_infers_from_params() -> None:
    @velaris_test
    def sample(api) -> None:
        pass

    assert sample.__velaris_capabilities__ == ["api"]


def test_mismatched_capability_raises() -> None:
    with pytest.raises(CollectionError, match="no parameter named 'secrets'"):

        @velaris_test("api", "secrets")
        def sample(api) -> None:
            pass


def test_extra_parameter_raises() -> None:
    with pytest.raises(CollectionError, match="does not match parameters"):

        @velaris_test("api")
        def sample(api, secrets) -> None:
            pass
