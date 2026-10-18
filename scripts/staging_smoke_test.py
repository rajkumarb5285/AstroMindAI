#!/usr/bin/env python3
"""
AstroMind AI - Staging Automated Smoke Test Script
Executes 10-step end-to-end integration verification against staging or local server.
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request


def run_request(url: str, method: str = "GET", headers: dict | None = None, data: dict | None = None) -> tuple[int, dict | bytes, dict]:
    headers = headers or {}
    encoded_data = None
    if data is not None:
        encoded_data = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            status = response.status
            content_type = response.headers.get("Content-Type", "")
            raw = response.read()
            resp_headers = {k.lower(): v for k, v in response.headers.items()}
            if "application/json" in content_type:
                return status, json.loads(raw.decode("utf-8")), resp_headers
            return status, raw, resp_headers
    except urllib.error.HTTPError as e:
        raw = e.read()
        resp_headers = {k.lower(): v for k, v in e.headers.items()}
        try:
            return e.code, json.loads(raw.decode("utf-8")), resp_headers
        except Exception:  # noqa: BLE001
            return e.code, raw, resp_headers


def main() -> int:
    parser = argparse.ArgumentParser(description="Run end-to-end smoke test against AstroMind server")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Base URL of AstroMind backend")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    auth_header = {"Authorization": "Bearer test-token-staging-smoke-user"}
    admin_header = {"Authorization": "Bearer test-token-staging-admin"}

    results = []
    print(f"Starting AstroMind AI Staging Smoke Test against: {base_url}\n" + "=" * 60)

    # 1. Health Probe - Liveness
    t0 = time.perf_counter()
    status, body, _ = run_request(f"{base_url}/health/live")
    d1 = (time.perf_counter() - t0) * 1000
    assert status == 200, f"Liveness probe failed with status {status}"
    assert body.get("status") == "healthy"
    results.append({"step": 1, "name": "Liveness Probe", "status": "PASS", "latency_ms": round(d1, 2)})
    print(f"[PASS] Step 1: Liveness Probe ({d1:.2f}ms)")

    # 2. Health Probe - Readiness
    t0 = time.perf_counter()
    status, body, _ = run_request(f"{base_url}/health/ready")
    d2 = (time.perf_counter() - t0) * 1000
    assert status == 200, f"Readiness probe failed with status {status}"
    assert body.get("status") == "ready"
    results.append({"step": 2, "name": "Readiness Probe", "status": "PASS", "latency_ms": round(d2, 2)})
    print(f"[PASS] Step 2: Readiness Probe ({d2:.2f}ms)")

    # 3. Telemetry & Metrics
    t0 = time.perf_counter()
    status, body, _ = run_request(f"{base_url}/api/v1/metrics", headers=admin_header)
    d3 = (time.perf_counter() - t0) * 1000
    assert status == 200, f"Metrics query failed with status {status}"
    assert body["engine"]["name"] == "pyswisseph"
    assert body["security"]["rate_limit_enabled"] is True
    results.append({"step": 3, "name": "Metrics Telemetry", "status": "PASS", "latency_ms": round(d3, 2)})
    print(f"[PASS] Step 3: Metrics Telemetry ({d3:.2f}ms)")

    # 4. Create Birth Profile
    t0 = time.perf_counter()
    profile_payload = {
        "name": "Staging Smoke Test Native",
        "birth_date": "1992-07-15",
        "birth_time": "08:45:00",
        "timezone": "Asia/Kolkata",
        "birthplace": "New Delhi, India",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "birth_time_confidence": "exact",
    }
    status, body, _ = run_request(f"{base_url}/api/v1/birth-profiles", method="POST", headers=auth_header, data=profile_payload)
    d4 = (time.perf_counter() - t0) * 1000
    assert status == 201, f"Create profile failed with status {status}: {body}"
    profile_id = body["id"]
    results.append({"step": 4, "name": "Create Birth Profile", "status": "PASS", "latency_ms": round(d4, 2)})
    print(f"[PASS] Step 4: Create Birth Profile ID: {profile_id} ({d4:.2f}ms)")

    # 5. Calculate D1 Chart
    t0 = time.perf_counter()
    chart_payload = {
        "ayanamsa": "lahiri",
        "node_mode": "mean",
    }
    status, body, hdrs = run_request(f"{base_url}/api/v1/birth-profiles/{profile_id}/charts", method="POST", headers=auth_header, data=chart_payload)
    d5 = (time.perf_counter() - t0) * 1000
    assert status == 201, f"Chart calculation failed: {body}"
    chart_id = body["id"]
    calc_res = body.get("calculation_result", {})
    assert len(calc_res.get("planets", [])) == 9
    assert len(calc_res.get("houses", [])) == 12
    assert "x-ratelimit-limit" in hdrs
    results.append({"step": 5, "name": "Calculate D1 Kundli", "status": "PASS", "latency_ms": round(d5, 2)})
    print(f"[PASS] Step 5: Calculate D1 Kundli ID: {chart_id} ({d5:.2f}ms)")

    # 6. Ashta Koota Compatibility Milan
    t0 = time.perf_counter()
    milan_payload = {
        "bride_moon_sign": 5,
        "bride_nakshatra": 10,
        "bride_pada": 2,
        "groom_moon_sign": 1,
        "groom_nakshatra": 1,
        "groom_pada": 1,
    }
    status, body, _ = run_request(f"{base_url}/api/v1/compatibility", method="POST", headers=auth_header, data=milan_payload)
    d6 = (time.perf_counter() - t0) * 1000
    assert status == 200, f"Compatibility check failed: {body}"
    assert 0 <= body["total_points"] <= 36
    assert len(body["kootas"]) == 8
    results.append({"step": 6, "name": "Ashta Koota Compatibility", "status": "PASS", "latency_ms": round(d6, 2)})
    print(f"[PASS] Step 6: Ashta Koota Compatibility score: {body['total_points']}/36 ({d6:.2f}ms)")

    # 7. Planetary Gochar Transits & Sade Sati
    t0 = time.perf_counter()
    status, body, _ = run_request(f"{base_url}/api/v1/charts/{chart_id}/transits", headers=auth_header)
    d7 = (time.perf_counter() - t0) * 1000
    assert status == 200, f"Transits calculation failed: {body}"
    assert "sade_sati" in body
    assert len(body["transits"]) >= 9
    results.append({"step": 7, "name": "Gochar Transits & Sade Sati", "status": "PASS", "latency_ms": round(d7, 2)})
    print(f"[PASS] Step 7: Gochar Transits evaluated ({d7:.2f}ms)")

    # 8. Multi-Turn Persistent Chat
    t0 = time.perf_counter()
    conv_payload = {"chart_id": chart_id, "title": "Staging Chat Consultation"}
    status, body, _ = run_request(f"{base_url}/api/v1/conversations", method="POST", headers=auth_header, data=conv_payload)
    assert status == 201, f"Conversation creation failed: {body}"
    conv_id = body["id"]

    msg_payload = {"content": "What is the dignity and house placement of Jupiter in this chart?"}
    status, msg_body, _ = run_request(f"{base_url}/api/v1/conversations/{conv_id}/messages", method="POST", headers=auth_header, data=msg_payload)
    d8 = (time.perf_counter() - t0) * 1000
    assert status in (200, 201), f"Message creation failed: {msg_body}"
    assert len(msg_body["assistant_message"]["content"]) > 10
    results.append({"step": 8, "name": "Grounded AI Consultation", "status": "PASS", "latency_ms": round(d8, 2)})
    print(f"[PASS] Step 8: Grounded AI Consultation completed ({d8:.2f}ms)")

    # 9. Server-Side PDF Report Generation
    t0 = time.perf_counter()
    report_payload = {"report_type": "natal_summary", "title": "Staging Smoke Test Report"}
    status, body, _ = run_request(f"{base_url}/api/v1/charts/{chart_id}/reports", method="POST", headers=auth_header, data=report_payload)
    d9 = (time.perf_counter() - t0) * 1000
    assert status == 201, f"Report generation failed: {body}"
    report_id = body["report_id"]
    results.append({"step": 9, "name": "Generate PDF Kundli Report", "status": "PASS", "latency_ms": round(d9, 2)})
    print(f"[PASS] Step 9: Generate PDF Kundli Report ID: {report_id} ({d9:.2f}ms)")

    # 10. Authenticated PDF Binary Streaming Download
    t0 = time.perf_counter()
    status, pdf_bytes, hdrs = run_request(f"{base_url}/api/v1/reports/{report_id}/download", headers=auth_header)
    d10 = (time.perf_counter() - t0) * 1000
    assert status == 200, f"PDF download failed: {status}"
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF"), f"Invalid PDF binary header: {pdf_bytes[:10]}"
    results.append({"step": 10, "name": "Download PDF Report", "status": "PASS", "latency_ms": round(d10, 2)})
    print(f"[PASS] Step 10: Download PDF Report ({len(pdf_bytes)} bytes in {d10:.2f}ms)")

    print("=" * 60)
    print(json.dumps({
        "status": "ALL_STEPS_PASSED",
        "total_steps": len(results),
        "steps": results,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
