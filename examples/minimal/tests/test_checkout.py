"""Multiple capability demonstration."""

from velaris_core.decorators import test


@test("api", "secrets")
def test_checkout(api, secrets):
    token = secrets.get("API_TOKEN")
    response = api.get("/orders", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
