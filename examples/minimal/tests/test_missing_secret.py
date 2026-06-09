"""Failure scenario: missing secret at runtime."""

from velaris_core.decorators import test


@test("secrets")
def test_missing_secret(secrets):
    secrets.get("DOES_NOT_EXIST")
