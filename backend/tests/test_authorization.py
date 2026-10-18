import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app
from backend.app.repositories.scoped import BirthProfileRepository, ChartRepository
from backend.tests.conftest import TestingSessionLocal


@pytest.mark.asyncio
async def test_unauthenticated_access_denied():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get("/api/v1/birth-profiles")
        assert res.status_code == 401
        assert "credentials are required" in res.json()["detail"]


@pytest.mark.asyncio
async def test_user_a_can_create_and_read_own_profile():
    transport = ASGITransport(app=app)
    headers_a = {"Authorization": "Bearer test-token-user-a"}
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        payload = {
            "name": "User A Chart",
            "birth_date": "1990-01-15",
            "birth_time": "10:30:00",
            "timezone": "Asia/Kolkata",
            "birthplace": "New Delhi, India",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "birth_time_confidence": "exact",
        }
        create_res = await client.post("/api/v1/birth-profiles", json=payload, headers=headers_a)
        assert create_res.status_code == 201
        created = create_res.json()
        assert created["owner_id"] == "user-a"
        assert created["name"] == "User A Chart"

        profile_id = created["id"]
        read_res = await client.get(f"/api/v1/birth-profiles/{profile_id}", headers=headers_a)
        assert read_res.status_code == 200
        assert read_res.json()["id"] == profile_id


@pytest.mark.asyncio
async def test_user_b_cannot_read_user_a_profile():
    transport = ASGITransport(app=app)
    headers_a = {"Authorization": "Bearer test-token-user-a"}
    headers_b = {"Authorization": "Bearer test-token-user-b"}

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # User A creates a profile
        payload = {
            "name": "Private Record A",
            "birth_date": "1995-07-20",
            "birth_time": "08:15:00",
            "timezone": "America/New_York",
            "birthplace": "New York, USA",
            "latitude": 40.7128,
            "longitude": -74.0060,
        }
        res_a = await client.post("/api/v1/birth-profiles", json=payload, headers=headers_a)
        profile_id = res_a.json()["id"]

        # User B attempts to read User A's profile
        res_b = await client.get(f"/api/v1/birth-profiles/{profile_id}", headers=headers_b)
        assert res_b.status_code == 404
        assert res_b.json()["detail"] == "Birth profile not found."


@pytest.mark.asyncio
async def test_user_b_cannot_update_or_delete_user_a_profile():
    transport = ASGITransport(app=app)
    headers_a = {"Authorization": "Bearer test-token-user-a"}
    headers_b = {"Authorization": "Bearer test-token-user-b"}

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # User A creates a profile
        payload = {
            "name": "Target Record",
            "birth_date": "1988-12-05",
            "timezone": "Europe/London",
            "birthplace": "London, UK",
            "latitude": 51.5074,
            "longitude": -0.1278,
        }
        res_a = await client.post("/api/v1/birth-profiles", json=payload, headers=headers_a)
        profile_id = res_a.json()["id"]

        # User B attempts to UPDATE User A's profile
        res_update = await client.put(
            f"/api/v1/birth-profiles/{profile_id}",
            json={"name": "Hacked Title"},
            headers=headers_b,
        )
        assert res_update.status_code == 404

        # User B attempts to DELETE User A's profile
        res_delete = await client.delete(
            f"/api/v1/birth-profiles/{profile_id}",
            headers=headers_b,
        )
        assert res_delete.status_code == 404

        # Verify record still safely exists for User A unchanged
        verify_res = await client.get(f"/api/v1/birth-profiles/{profile_id}", headers=headers_a)
        assert verify_res.status_code == 200
        assert verify_res.json()["name"] == "Target Record"


@pytest.mark.asyncio
async def test_user_list_isolation():
    transport = ASGITransport(app=app)
    headers_a = {"Authorization": "Bearer test-token-user-a"}
    headers_b = {"Authorization": "Bearer test-token-user-b"}

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # User A creates 2 profiles
        await client.post(
            "/api/v1/birth-profiles",
            json={
                "name": "Profile A1",
                "birth_date": "1990-01-01",
                "timezone": "UTC",
                "birthplace": "Greenwich",
                "latitude": 51.48,
                "longitude": 0.0,
            },
            headers=headers_a,
        )
        # User B creates 1 profile
        await client.post(
            "/api/v1/birth-profiles",
            json={
                "name": "Profile B1",
                "birth_date": "1992-02-02",
                "timezone": "UTC",
                "birthplace": "Greenwich",
                "latitude": 51.48,
                "longitude": 0.0,
            },
            headers=headers_b,
        )

        list_a = await client.get("/api/v1/birth-profiles", headers=headers_a)
        assert list_a.status_code == 200
        data_a = list_a.json()
        assert len(data_a) == 1
        assert data_a[0]["name"] == "Profile A1"
        assert all(item["owner_id"] == "user-a" for item in data_a)

        list_b = await client.get("/api/v1/birth-profiles", headers=headers_b)
        assert list_b.status_code == 200
        data_b = list_b.json()
        assert len(data_b) == 1
        assert data_b[0]["name"] == "Profile B1"
        assert all(item["owner_id"] == "user-b" for item in data_b)


@pytest.mark.asyncio
async def test_validation_rejects_invalid_timezone_and_coordinates():
    transport = ASGITransport(app=app)
    headers = {"Authorization": "Bearer test-token-user-a"}
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Invalid timezone
        bad_tz = await client.post(
            "/api/v1/birth-profiles",
            json={
                "name": "Bad TZ",
                "birth_date": "1990-01-01",
                "timezone": "Invalid/Fake_Zone",
                "birthplace": "Nowhere",
                "latitude": 20.0,
                "longitude": 20.0,
            },
            headers=headers,
        )
        assert bad_tz.status_code == 422
        assert "not a valid IANA timezone" in str(bad_tz.json())

        # Invalid coordinates (latitude > 90)
        bad_coords = await client.post(
            "/api/v1/birth-profiles",
            json={
                "name": "Bad Coords",
                "birth_date": "1990-01-01",
                "timezone": "Asia/Kolkata",
                "birthplace": "Nowhere",
                "latitude": 120.0,
                "longitude": 20.0,
            },
            headers=headers,
        )
        assert bad_coords.status_code == 422


def test_repository_layer_cross_user_denial():
    db = TestingSessionLocal()
    repo = BirthProfileRepository(db)
    chart_repo = ChartRepository(db)

    # 1. User A creates profile directly in DB
    profile_a = repo.create(
        owner_id="user-a",
        data={
            "name": "Repo Profile A",
            "birth_date": "1990-05-10",
            "timezone": "Asia/Kolkata",
            "birthplace": "Kolkata, India",
            "latitude": 22.5726,
            "longitude": 88.3639,
        },
    )
    assert profile_a.id is not None

    # 2. User B cannot get User A's profile via repo
    assert repo.get_by_id(profile_id=profile_a.id, owner_id="user-b") is None

    # 3. User B cannot update User A's profile via repo
    assert repo.update(profile_id=profile_a.id, owner_id="user-b", data={"name": "Tampered"}) is None

    # 4. User B cannot delete User A's profile via repo
    assert repo.delete(profile_id=profile_a.id, owner_id="user-b") is False

    # 5. User B cannot attach a chart to User A's profile
    with pytest.raises(PermissionError, match="Access denied"):
        chart_repo.create(
            owner_id="user-b",
            birth_profile_id=profile_a.id,
            chart_data={"calculation_type": "D1"},
        )

    db.close()
