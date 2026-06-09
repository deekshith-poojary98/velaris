"""Composition via bootstrap convention — target_environment in config only."""

from velaris_core.decorators import test


@test("api", "secrets")
def test_compose_in_bootstrap(api, secrets):
    token = secrets.get("API_TOKEN")
    response = api.get("/orders", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
