import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "AstroMind AI"
        assert data["status"] == "operational"
        assert "request_id" in data
        assert "X-Request-ID" in response.headers
        assert "X-Process-Time" in response.headers


@pytest.mark.asyncio
async def test_health_liveness():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        # Ensure no secrets or environment topology leaked
        assert "database_url" not in data
        assert "supabase" not in data


@pytest.mark.asyncio
async def test_health_readiness():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["database"] == "connected"
        assert "timestamp" in data
