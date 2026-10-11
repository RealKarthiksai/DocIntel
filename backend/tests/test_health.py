import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_check_returns_healthy():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("healthy", "degraded")
        assert data["postgres"] == "connected"
        assert data["mongodb"] == "connected"
        assert "connected" in data["chromadb"]

@pytest.mark.asyncio
async def test_metrics_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "total_documents" in data
        assert "total_audit_events" in data
