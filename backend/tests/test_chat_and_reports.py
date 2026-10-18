from fastapi.testclient import TestClient

from backend.app.models.entities import BirthProfile, ChartCalculation


def test_conversation_lifecycle_and_cross_user_denial(client: TestClient, db):
    prof = BirthProfile(
        id="prof_chat_lifecycle",
        owner_id="test_user_a",
        name="Chat User",
        birth_date="1980-01-01",
        timezone="Asia/Kolkata",
        birthplace="Delhi",
        latitude=28.6,
        longitude=77.2,
    )
    db.add(prof)

    chart = ChartCalculation(
        id="chart_chat_lifecycle",
        owner_id="test_user_a",
        birth_profile_id=prof.id,
        calculation_type="D1",
        engine="pyswisseph",
        engine_version="2.10",
        config_version="v1",
        ayanamsa="lahiri",
        planetary_positions=[
            {"planet_id": "Sun", "sign_number": 9, "degree_in_sign": 15.0, "sign_name": "Sagittarius", "longitude": 255.0, "is_retrograde": False, "speed": 1.0, "sanskrit_name": "Surya", "nakshatra_name": "Purva Ashadha", "nakshatra_ruler": "Venus", "sign_sanskrit": "Dhanu", "nakshatra_index": 20, "pada": 1, "house_number": 10},
            {"planet_id": "Mercury", "sign_number": 9, "degree_in_sign": 18.0, "sign_name": "Sagittarius", "longitude": 258.0, "is_retrograde": False, "speed": 1.2, "sanskrit_name": "Budha", "nakshatra_name": "Purva Ashadha", "nakshatra_ruler": "Venus", "sign_sanskrit": "Dhanu", "nakshatra_index": 20, "pada": 2, "house_number": 10},
            {"planet_id": "Moon", "sign_number": 3, "degree_in_sign": 5.0, "sign_name": "Gemini", "longitude": 65.0, "is_retrograde": False, "speed": 13.0, "sanskrit_name": "Chandra", "nakshatra_name": "Mrigashira", "nakshatra_ruler": "Mars", "sign_sanskrit": "Mithuna", "nakshatra_index": 5, "pada": 4, "house_number": 4},
        ],
        ascendant=343.0,
        houses=[],
    )
    db.add(chart)
    db.commit()

    # 1. User A creates conversation
    create_resp = client.post(
        "/api/v1/conversations",
        headers={"Authorization": "Bearer test-token-test_user_a"},
        json={"title": "Career & Yogas Inquiry", "chart_id": chart.id},
    )
    assert create_resp.status_code == 201
    conv = create_resp.json()
    conv_id = conv["id"]
    assert conv["title"] == "Career & Yogas Inquiry"

    # 2. User A sends message (triggers orchestrator)
    msg_resp = client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        headers={"Authorization": "Bearer test-token-test_user_a"},
        json={"content": "What yogas are present in my chart?"},
    )
    assert msg_resp.status_code == 200
    msg_data = msg_resp.json()
    assert msg_data["user_message"]["content"] == "What yogas are present in my chart?"
    assert "Budhaditya" in msg_data["assistant_message"]["content"] or len(msg_data["tools_called"]) > 0
    assert len(msg_data["citations"]) > 0
    assert len(msg_data["disclaimer"]) > 0

    # 3. User A lists messages
    list_resp = client.get(
        f"/api/v1/conversations/{conv_id}/messages",
        headers={"Authorization": "Bearer test-token-test_user_a"},
    )
    assert list_resp.status_code == 200
    msgs = list_resp.json()
    assert len(msgs) == 2  # user + assistant

    # 4. User B cannot access User A's conversation
    denied_resp = client.get(
        f"/api/v1/conversations/{conv_id}/messages",
        headers={"Authorization": "Bearer test-token-test_user_b"},
    )
    assert denied_resp.status_code == 404

    # 5. User B cannot send message to User A's conversation
    denied_send = client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        headers={"Authorization": "Bearer test-token-test_user_b"},
        json={"content": "Malicious intrusion attempt"},
    )
    assert denied_send.status_code == 404


def test_pdf_report_generation_and_download(client: TestClient, db):
    prof = BirthProfile(
        id="prof_report_test",
        owner_id="test_user_a",
        name="Report Native",
        birth_date="1980-01-01",
        birth_time="12:00:00",
        timezone="Asia/Kolkata",
        birthplace="Delhi, India",
        latitude=28.6139,
        longitude=77.2090,
    )
    db.add(prof)

    chart = ChartCalculation(
        id="chart_report_test",
        owner_id="test_user_a",
        birth_profile_id=prof.id,
        calculation_type="D1",
        engine="pyswisseph",
        engine_version="2.10",
        config_version="v1",
        ayanamsa="lahiri",
        planetary_positions=[
            {"planet_id": "Sun", "sign_number": 9, "degree_in_sign": 15.0, "sign_name": "Sagittarius", "longitude": 255.0, "is_retrograde": False, "speed": 1.0, "sanskrit_name": "Surya", "nakshatra_name": "Purva Ashadha", "nakshatra_ruler": "Venus", "sign_sanskrit": "Dhanu", "nakshatra_index": 20, "pada": 1, "house_number": 10},
            {"planet_id": "Moon", "sign_number": 3, "degree_in_sign": 5.0, "sign_name": "Gemini", "longitude": 65.0, "is_retrograde": False, "speed": 13.0, "sanskrit_name": "Chandra", "nakshatra_name": "Mrigashira", "nakshatra_ruler": "Mars", "sign_sanskrit": "Mithuna", "nakshatra_index": 5, "pada": 4, "house_number": 4},
        ],
        ascendant=343.0,
        houses=[],
        dasha_data=[
            {"lord": "Mars", "start_date": "1980-01-01T00:00:00Z", "end_date": "1985-05-10T00:00:00Z", "duration_years": 5.35}
        ],
    )
    db.add(chart)
    db.commit()

    # 1. User A generates PDF report
    gen_resp = client.post(
        f"/api/v1/charts/{chart.id}/reports",
        headers={"Authorization": "Bearer test-token-test_user_a"},
        json={"title": "Official Vedic Kundli Report"},
    )
    assert gen_resp.status_code == 201
    rep_data = gen_resp.json()
    rep_id = rep_data["report_id"]
    assert rep_data["status"] == "completed"
    assert "/download" in rep_data["download_url"]

    # 2. User A downloads PDF report
    dl_resp = client.get(
        f"/api/v1/reports/{rep_id}/download",
        headers={"Authorization": "Bearer test-token-test_user_a"},
    )
    assert dl_resp.status_code == 200
    assert dl_resp.headers["content-type"] == "application/pdf"
    assert dl_resp.content.startswith(b"%PDF-")  # Valid PDF binary signature
    assert len(dl_resp.content) > 1000

    # 3. User B cannot download User A's report (IDOR defense)
    dl_resp_b = client.get(
        f"/api/v1/reports/{rep_id}/download",
        headers={"Authorization": "Bearer test-token-test_user_b"},
    )
    assert dl_resp_b.status_code == 404
