"""Composition in test code — test wires capabilities together."""

from velaris_core.decorators import test


@test("api", "secrets", "target_environment")
def test_compose_in_test(api, secrets, target_environment):
    token = secrets.get("API_TOKEN")
    root = target_environment.endpoint("api").rstrip("/")
    response = api.get(
        f"{root}/orders",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
