import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.core.config import settings
from backend.app.core.rate_limit import rate_limiter
from backend.app.services.audit import AuditEventNames, AuditService, anonymize_ip


@pytest.fixture(autouse=True)
def reset_limiter():
    rate_limiter._history.clear()
    yield
    rate_limiter._history.clear()


def test_rate_limiting_enforcement_and_headers(client: TestClient):
    """
    Verify tiered sliding window rate limiter blocks excessive requests with 429 Too Many Requests
    and provides standard RFC rate limit headers.
    """
    # Temporarily lower auth limit for rapid testing
    original_limit = settings.RATE_LIMIT_AUTH_PER_MINUTE
    settings.RATE_LIMIT_AUTH_PER_MINUTE = 3
    settings.RATE_LIMIT_ENABLED = True

    try:
        headers = {"Authorization": "Bearer test_ratelimit_user_token"}

        # First 3 requests should succeed
        for i in range(3):
            resp = client.get("/api/v1/auth/session", headers=headers)
            # Route may return 200 or 404/401 depending on route existence, but NOT 429
            assert resp.status_code != 429
            assert "X-RateLimit-Limit" in resp.headers
            assert resp.headers["X-RateLimit-Limit"] == "3"
            assert resp.headers["X-RateLimit-Remaining"] == str(2 - i)

        # 4th request must be rejected with 429
        blocked = client.get("/api/v1/auth/session", headers=headers)
        assert blocked.status_code == 429
        data = blocked.json()
        assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"
        assert "Retry-After" in blocked.headers
        assert "X-RateLimit-Reset" in blocked.headers
        assert blocked.headers["X-RateLimit-Remaining"] == "0"
    finally:
        settings.RATE_LIMIT_AUTH_PER_MINUTE = original_limit


def test_health_checks_bypass_rate_limiting(client: TestClient):
    """
    Verify infrastructure probes (/health/live, /health/ready, /) are exempt from rate limiting.
    """
    for _ in range(25):
        resp = client.get("/health/live")
        assert resp.status_code == 200


def test_audit_logging_service_and_ip_anonymization(db):
    """
    Verify AuditService records immutable events, hashes client IPs for privacy, and logs properly.
    """
    # 1. Test IP Anonymization
    raw_ip = "192.168.1.100"
    hashed_ip = anonymize_ip(raw_ip)
    assert hashed_ip is not None
    assert hashed_ip != raw_ip
    assert len(hashed_ip) == 16

    # 2. Record Event
    event = AuditService.record_event(
        db=db,
        event_name=AuditEventNames.AUTH_LOGIN_SUCCESS,
        actor_id="user_sec_audit_1",
        target_resource="profile",
        target_id="prof_123",
        details={"method": "magic_link"},
        ip_address=raw_ip,
    )
    assert event.id is not None
    assert event.event_name == AuditEventNames.AUTH_LOGIN_SUCCESS
    assert event.ip_address == hashed_ip

    # 3. Retrieve Event from DB
    retrieved = AuditService.get_events(db=db, actor_id="user_sec_audit_1")
    assert len(retrieved) >= 1
    assert retrieved[0].actor_id == "user_sec_audit_1"
    assert retrieved[0].details["method"] == "magic_link"


def test_metrics_telemetry_endpoint(client: TestClient, db):
    """
    Verify /api/v1/metrics returns server telemetry and security counters without leaking sensitive keys.
    """
    headers = {"Authorization": "Bearer test-token-metrics-admin"}
    resp = client.get("/api/v1/metrics", headers=headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == "healthy"
    assert "uptime_seconds" in data
    assert "engine" in data
    assert data["engine"]["name"] == "pyswisseph"
    assert data["security"]["rate_limit_enabled"] is True
    assert "audit_events_logged" in data["security"]

    # Verify no credentials or API keys leaked
    raw_text = resp.text.lower()
    for secret in ["postgrespassword", "dummy-key", "secret", "private_key"]:
        assert secret not in raw_text, f"Potential sensitive key '{secret}' exposed in metrics!"


def test_repository_secrets_and_gitignore():
    """
    Scan repo for forbidden secret patterns and ensure .env is gitignored.
    """
    repo_root = Path(__file__).resolve().parent.parent.parent

    # Check .gitignore contains .env
    gitignore_path = repo_root / ".gitignore"
    assert gitignore_path.exists()
    gitignore_content = gitignore_path.read_text(encoding="utf-8")
    assert ".env" in gitignore_content

    # Regex patterns for high-entropy secrets
    forbidden_patterns = [
        re.compile(r"-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----"),
        re.compile(r"(?i)aws_access_key_id\s*=\s*['\"][A-Z0-9]{20}['\"]"),
        re.compile(r"(?i)ghp_[a-zA-Z0-9]{36}"),
        re.compile(r"(?i)sk_live_[0-9a-zA-Z]{24}"),
    ]

    backend_py_files = list((repo_root / "backend" / "app").rglob("*.py"))
    for py_file in backend_py_files:
        content = py_file.read_text(encoding="utf-8")
        for pattern in forbidden_patterns:
            match = pattern.search(content)
            assert match is None, f"Forbidden secret pattern found in {py_file}!"
