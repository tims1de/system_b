import pytest


@pytest.mark.asyncio
async def test_health_returns_200(client):
    """GET /api/health should return status 200."""
    response = await client.get("/api/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_returns_ok_text(client):
    """GET /api/health should return 'OK'."""
    response = await client.get("/api/health")
    assert response.text == "OK"