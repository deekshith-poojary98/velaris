"""Minimal execution engine demonstration."""

from velaris_core.decorators import test


@test("api")
def test_users(api):
    response = api.get("/users")
    assert response.status_code == 200
