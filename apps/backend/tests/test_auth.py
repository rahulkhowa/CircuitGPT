import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_user_registration_and_login(async_client: AsyncClient):
    # 1. Register User
    register_payload = {
        "email": "student@circuitgpt.edu",
        "password": "SecurePassword123!",
        "full_name": "Test Student",
        "role": "student"
    }
    register_resp = await async_client.post("/api/v1/auth/register", json=register_payload)
    assert register_resp.status_code == 201
    user_data = register_resp.json()
    assert user_data["email"] == "student@circuitgpt.edu"
    assert user_data["full_name"] == "Test Student"

    # 2. Login User
    login_payload = {
        "email": "student@circuitgpt.edu",
        "password": "SecurePassword123!"
    }
    login_resp = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["token_type"] == "bearer"

    # 3. Access Protected /me endpoint
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    me_resp = await async_client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == "student@circuitgpt.edu"
