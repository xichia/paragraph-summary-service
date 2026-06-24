def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["provider_default"] == "mock"
    assert data["external_provider_calls_enabled"] is False
