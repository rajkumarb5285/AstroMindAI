from fastapi.testclient import TestClient

from backend.app.astrology.compatibility.ashta_koota import (
    calculate_ashta_koota,
)
from backend.app.models.entities import BirthProfile, ChartCalculation


def test_ashta_koota_full_calculation():
    # Test pairing:
    # Bride: Taurus Moon (Sign 2), Rohini (Nakshatra 4, Pada 1)
    # Groom: Virgo Moon (Sign 6), Hasta (Nakshatra 13, Pada 2)
    # Signs: Taurus (Venus) & Virgo (Mercury) -> Mutual Friends
    # Distance: Taurus to Virgo is 5 houses; Virgo to Taurus is 9 houses (Navapanchaka 9/5)
    # Sign lords Venus & Mercury are mutual friends -> Bhakoot Dosha is cancelled!
    res = calculate_ashta_koota(
        bride_moon_sign=2,
        bride_nakshatra=4,
        bride_pada=1,
        groom_moon_sign=6,
        groom_nakshatra=13,
        groom_pada=2,
    )

    assert res["total_points"] > 18.0
    assert res["max_points"] == 36.0
    assert res["verdict"] in ["Good", "Excellent"]
    assert len(res["kootas"]) == 8

    k_names = [k["koota_name"] for k in res["kootas"]]
    assert k_names == ["Varna", "Vashya", "Tara", "Yoni", "Graha Maitri", "Gana", "Bhakoot", "Nadi"]


def test_bhakoot_dosha_cancellation_same_lord():
    # Aries (Sign 1, Mars) and Scorpio (Sign 8, Mars) -> 6/8 Shadashtaka distance
    # Classical rule: Since both signs are ruled by Mars, Bhakoot dosha is CANCELLED!
    res = calculate_ashta_koota(
        bride_moon_sign=1,
        bride_nakshatra=1,  # Ashwini
        bride_pada=1,
        groom_moon_sign=8,
        groom_nakshatra=16,  # Anuradha
        groom_pada=1,
    )

    bhakoot = next(k for k in res["kootas"] if k["koota_name"] == "Bhakoot")
    assert bhakoot["points_obtained"] == 7.0
    assert bhakoot["status"] == "cancelled"
    assert "Mars" in str(bhakoot["cancellation_reason"])


def test_nadi_dosha_cancellation_different_rashis():
    # Krittika spans Aries (Pada 1) and Taurus (Padas 2, 3, 4)
    # Both have Krittika Nakshatra (Antya Nadi), but Bride is Aries and Groom is Taurus
    # Classical rule: Different Moon signs cancel Nadi dosha!
    res = calculate_ashta_koota(
        bride_moon_sign=1,
        bride_nakshatra=3,  # Krittika
        bride_pada=1,
        groom_moon_sign=2,
        groom_nakshatra=3,  # Krittika
        groom_pada=2,
    )

    nadi = next(k for k in res["kootas"] if k["koota_name"] == "Nadi")
    assert nadi["points_obtained"] == 8.0
    assert nadi["status"] == "cancelled"
    assert "different Moon signs" in str(nadi["cancellation_reason"])


def test_vairi_yoni_sworn_enemies():
    # Cow Yoni (Uttara Phalguni, Nakshatra 12) vs Tiger Yoni (Chitra, Nakshatra 14)
    # Classical sworn enemy pair -> 0 points in Yoni
    res = calculate_ashta_koota(
        bride_moon_sign=6,
        bride_nakshatra=12,
        bride_pada=1,
        groom_moon_sign=6,
        groom_nakshatra=14,
        groom_pada=1,
    )

    yoni = next(k for k in res["kootas"] if k["koota_name"] == "Yoni")
    assert yoni["points_obtained"] == 0.0
    assert yoni["status"] == "dosha"
    assert any("Vairi Yoni" in d for d in res["doshas"])


def test_compatibility_api_with_charts(client: TestClient, db):
    # Setup test User A with 2 charts
    prof_a = BirthProfile(
        id="prof_comp_bride",
        owner_id="test_user_a",
        name="Bride Profile",
        birth_date="1992-05-15",
        timezone="Asia/Kolkata",
        birthplace="Delhi",
        latitude=28.6,
        longitude=77.2,
    )
    prof_b = BirthProfile(
        id="prof_comp_groom",
        owner_id="test_user_a",
        name="Groom Profile",
        birth_date="1990-08-20",
        timezone="Asia/Kolkata",
        birthplace="Mumbai",
        latitude=19.0,
        longitude=72.8,
    )
    db.add_all([prof_a, prof_b])

    chart_a = ChartCalculation(
        id="chart_comp_bride",
        owner_id="test_user_a",
        birth_profile_id=prof_a.id,
        calculation_type="D1",
        engine="pyswisseph",
        engine_version="2.10",
        config_version="v1",
        ayanamsa="lahiri",
        planetary_positions=[
            {"planet_id": "Moon", "sign_number": 2, "nakshatra_index": 4, "pada": 1, "degree_in_sign": 15.0, "sign_name": "Taurus", "longitude": 45.0, "is_retrograde": False, "speed": 13.0, "sanskrit_name": "Chandra", "nakshatra_name": "Rohini", "nakshatra_ruler": "Moon", "sign_sanskrit": "Vrishabha", "house_number": 1}
        ],
        ascendant=45.0,
        houses=[],
    )
    chart_b = ChartCalculation(
        id="chart_comp_groom",
        owner_id="test_user_a",
        birth_profile_id=prof_b.id,
        calculation_type="D1",
        engine="pyswisseph",
        engine_version="2.10",
        config_version="v1",
        ayanamsa="lahiri",
        planetary_positions=[
            {"planet_id": "Moon", "sign_number": 6, "nakshatra_index": 13, "pada": 2, "degree_in_sign": 12.0, "sign_name": "Virgo", "longitude": 162.0, "is_retrograde": False, "speed": 12.5, "sanskrit_name": "Chandra", "nakshatra_name": "Hasta", "nakshatra_ruler": "Moon", "sign_sanskrit": "Kanya", "house_number": 1}
        ],
        ascendant=162.0,
        houses=[],
    )
    db.add_all([chart_a, chart_b])
    db.commit()

    # User A requests compatibility
    resp = client.post(
        "/api/v1/compatibility",
        headers={"Authorization": "Bearer test-token-test_user_a"},
        json={"bride_chart_id": chart_a.id, "groom_chart_id": chart_b.id},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_points"] > 18.0
    assert len(data["kootas"]) == 8

    # User B unauthorized attempt to use User A's bride chart
    resp_b = client.post(
        "/api/v1/compatibility",
        headers={"Authorization": "Bearer test-token-test_user_b"},
        json={"bride_chart_id": chart_a.id, "groom_chart_id": chart_b.id},
    )
    assert resp_b.status_code == 404
