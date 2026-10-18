import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.core.config import settings
from backend.app.main import app


@pytest.mark.asyncio
async def test_security_headers_present():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/health/live")
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
        assert "Content-Security-Policy" in response.headers
        assert "Permissions-Policy" in response.headers


@pytest.mark.asyncio
async def test_custom_request_id_propagation():
    transport = ASGITransport(app=app)
    custom_id = "test-custom-trace-uuid-12345"
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/health/live", headers={"X-Request-ID": custom_id})
        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == custom_id


@pytest.mark.asyncio
async def test_payload_too_large_rejection():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Send header simulating a payload exceeding 1MB
        oversized_bytes = settings.MAX_REQUEST_BODY_BYTES + 1024
        response = await client.post(
            "/",
            headers={"Content-Length": str(oversized_bytes)},
            content=b"x" * 10,
        )
        assert response.status_code == 413
        data = response.json()
        assert data["error"]["code"] == "PAYLOAD_TOO_LARGE"
        assert "request_id" in data["error"]
