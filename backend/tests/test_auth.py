import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_auth_valid_login():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Admin login
        res = await client.post("/auth/login", json={
            "email": "admin@example.com",
            "password": "AdminPass123!"
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["role"] == "ADMIN"
        assert len(data["permissions"]) > 0
        assert "documents:read" in data["permissions"]
        assert data["tenant_id"] == "tenant-default"

@pytest.mark.asyncio
async def test_auth_invalid_password():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/auth/login", json={
            "email": "admin@example.com",
            "password": "WrongPassword!"
        })
        assert res.status_code == 401

@pytest.mark.asyncio
async def test_auth_me_valid_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Login
        login_res = await client.post("/auth/login", json={
            "email": "manager@example.com",
            "password": "ManagerPass123!"
        })
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]

        # 2. Get /auth/me
        me_res = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_res.status_code == 200
        data = me_res.json()
        assert data["email"] == "manager@example.com"
        assert data["role_name"] == "MANAGER"
        assert data.get("department") == "finance"
        assert "documents:read" in data["permissions"]

@pytest.mark.asyncio
async def test_auth_invalid_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/auth/me", headers={"Authorization": "Bearer invalid.fake.token"})
        assert res.status_code == 401
