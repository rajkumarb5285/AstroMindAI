import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.tests.conftest import TestingSessionLocal


def test_auth_signup_and_login_flow(client: TestClient):
    # 1. Signup new user
    signup_resp = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "divya.sharma@example.com",
            "password": "SecurePassword123!",
            "full_name": "Divya Sharma",
        },
    )
    assert signup_resp.status_code == 201
    data = signup_resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == "divya.sharma@example.com"
    assert data["user"]["full_name"] == "Divya Sharma"
    token = data["access_token"]

    # 2. Get current user profile with token
    me_resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "divya.sharma@example.com"

    # 3. Duplicate email signup rejected
    dup_resp = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "divya.sharma@example.com",
            "password": "AnotherPassword456",
        },
    )
    assert dup_resp.status_code == 409

    # 4. Login with correct credentials
    login_resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": "divya.sharma@example.com",
            "password": "SecurePassword123!",
        },
    )
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()

    # 5. Login with incorrect password rejected
    wrong_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "divya.sharma@example.com",
            "password": "WrongPassword!",
        },
    )
    assert wrong_login.status_code == 401
