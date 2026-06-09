"""Provider swap demo: same test, different secrets provider via config."""

from velaris_core.decorators import test


@test("secrets")
def test_token(secrets):
    assert secrets.get("API_TOKEN") == "swap-demo-token"
