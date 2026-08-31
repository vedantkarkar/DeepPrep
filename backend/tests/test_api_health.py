import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_check_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["service"] == "DeepPrep"
    assert data["ai_provider"] == "mock"

@pytest.mark.asyncio
async def test_root_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["docs"] == "/docs"

@pytest.mark.asyncio
async def test_global_exception_handler_sanitizes_errors():
    """Verify that unhandled server exceptions do not leak stack traces or internal details to clients."""
    @app.get("/test-error-endpoint-for-audit")
    async def error_route():
        raise RuntimeError("CRITICAL_INTERNAL_DATABASE_SECRET_PATH_/var/secrets/key.pem")

    async with AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test"
    ) as ac:
        response = await ac.get("/test-error-endpoint-for-audit")

    assert response.status_code == 500
    data = response.json()
    assert data == {"detail": "An unexpected server error occurred."}
    assert "CRITICAL_INTERNAL" not in response.text
