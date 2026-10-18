from datetime import UTC, datetime

from fastapi.testclient import TestClient

from backend.app.astrology.transits.engine import TransitEngine
from backend.app.models.entities import BirthProfile, ChartCalculation


def test_transit_engine_sade_sati_detection():
    # If natal Moon is in Pisces (Sign 12)
    # When Saturn is in Aquarius (Sign 11), that is the 12th house from Moon -> Sade Sati Phase 1 (Rising)
    # When Saturn is in Pisces (Sign 12), that is the 1st house from Moon -> Sade Sati Phase 2 (Peak)
    # When Saturn is in Aries (Sign 1), that is the 2nd house from Moon -> Sade Sati Phase 3 (Setting)
    natal_calc = {
        "ascendant_sign_number": 1,
        "planets": [
            {"planet_id": "Moon", "sign_number": 12, "longitude": 340.0},
        ],
    }

    # Evaluate transits for 2024 (Saturn in Aquarius, Sign 11)
    res_2024 = TransitEngine.evaluate_transits(
        natal_chart_calc=natal_calc,
        transit_dt=datetime(2024, 6, 1, 12, 0, tzinfo=UTC),
    )
    assert res_2024["sade_sati"]["is_active"] is True
    assert "Rising" in str(res_2024["sade_sati"]["phase"])

    # Evaluate transits for natal Moon in Leo (Sign 5) during 2024 (Saturn in Aquarius 11 -> 7th house)
    # Not in 12th, 1st, or 2nd from Leo -> Not active
    natal_leo = {
        "ascendant_sign_number": 1,
        "planets": [{"planet_id": "Moon", "sign_number": 5, "longitude": 130.0}],
    }
    res_leo = TransitEngine.evaluate_transits(
        natal_chart_calc=natal_leo,
        transit_dt=datetime(2024, 6, 1, 12, 0, tzinfo=UTC),
    )
    assert res_leo["sade_sati"]["is_active"] is False


def test_transit_api_and_cross_user_denial(client: TestClient, db):
    prof = BirthProfile(
        id="prof_transit_test",
        owner_id="test_user_a",
        name="Transit User",
        birth_date="1985-02-10",
        timezone="Asia/Kolkata",
        birthplace="Delhi",
        latitude=28.6,
        longitude=77.2,
    )
    db.add(prof)

    chart = ChartCalculation(
        id="chart_transit_test",
        owner_id="test_user_a",
        birth_profile_id=prof.id,
        calculation_type="D1",
        engine="pyswisseph",
        engine_version="2.10",
        config_version="v1",
        ayanamsa="lahiri",
        planetary_positions=[
            {"planet_id": "Moon", "sign_number": 4, "nakshatra_index": 8, "pada": 1, "degree_in_sign": 10.0, "sign_name": "Cancer", "longitude": 100.0, "is_retrograde": False, "speed": 13.0, "sanskrit_name": "Chandra", "nakshatra_name": "Pushya", "nakshatra_ruler": "Saturn", "sign_sanskrit": "Karka", "house_number": 1}
        ],
        ascendant=100.0,
        houses=[],
    )
    db.add(chart)
    db.commit()

    # User A accesses own transits
    resp = client.get(
        f"/api/v1/charts/{chart.id}/transits",
        headers={"Authorization": "Bearer test-token-test_user_a"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["natal_moon_sign"] == 4
    assert len(data["transits"]) >= 7

    # User B denied access to User A's transits
    resp_b = client.get(
        f"/api/v1/charts/{chart.id}/transits",
        headers={"Authorization": "Bearer test-token-test_user_b"},
    )
    assert resp_b.status_code == 404
