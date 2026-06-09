"""Composition in config — base_url set directly on api.options."""

from velaris_core.decorators import test


@test("api", "secrets")
def test_compose_in_config(api, secrets):
    token = secrets.get("API_TOKEN")
    response = api.get("/orders", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
