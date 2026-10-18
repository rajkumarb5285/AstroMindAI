import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app


@pytest.mark.asyncio
async def test_chart_creation_and_owner_scoped_retrieval():
    transport = ASGITransport(app=app)
    headers_a = {"Authorization": "Bearer test-token-user-a"}
    headers_b = {"Authorization": "Bearer test-token-user-b"}

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. User A creates a birth profile
        profile_res = await client.post(
            "/api/v1/birth-profiles",
            json={
                "name": "Arjun Sharma",
                "birth_date": "1990-01-15",
                "birth_time": "12:00:00",
                "timezone": "Asia/Kolkata",
                "birthplace": "New Delhi, India",
                "latitude": 28.6139,
                "longitude": 77.2090,
            },
            headers=headers_a,
        )
        assert profile_res.status_code == 201
        profile_id = profile_res.json()["id"]

        # 2. User A generates a chart
        calc_res = await client.post(
            f"/api/v1/birth-profiles/{profile_id}/charts",
            json={"ayanamsa": "lahiri", "node_mode": "mean", "calculation_type": "D1"},
            headers=headers_a,
        )
        assert calc_res.status_code == 201
        chart_data = calc_res.json()
        assert chart_data["owner_id"] == "user-a"
        assert chart_data["birth_profile_id"] == profile_id
        chart_id = chart_data["id"]

        result = chart_data["calculation_result"]
        assert len(result["planets"]) == 9
        assert len(result["houses"]) == 12
        assert len(result["vimshottari_dashas"]) == 9
        assert result["metadata"]["engine"] == "pyswisseph"

        # 3. User A can retrieve their own chart by ID
        get_res_a = await client.get(f"/api/v1/charts/{chart_id}", headers=headers_a)
        assert get_res_a.status_code == 200
        assert get_res_a.json()["id"] == chart_id

        # 4. BOLA / IDOR Defense: User B attempts to retrieve User A's chart -> 404 Not Found
        get_res_b = await client.get(f"/api/v1/charts/{chart_id}", headers=headers_b)
        assert get_res_b.status_code == 404
        assert get_res_b.json()["detail"] == "Chart calculation not found."

        # 5. User B attempts to create a chart for User A's profile -> 404 Not Found
        hack_calc = await client.post(
            f"/api/v1/birth-profiles/{profile_id}/charts",
            json={"ayanamsa": "lahiri"},
            headers=headers_b,
        )
        assert hack_calc.status_code == 404

        # 6. Unauthenticated request -> 401 Unauthorized
        unauth_res = await client.get(f"/api/v1/charts/{chart_id}")
        assert unauth_res.status_code == 401

        # 7. List charts for profile
        list_res = await client.get(f"/api/v1/birth-profiles/{profile_id}/charts", headers=headers_a)
        assert list_res.status_code == 200
        assert len(list_res.json()) >= 1
        assert list_res.json()[0]["id"] == chart_id
