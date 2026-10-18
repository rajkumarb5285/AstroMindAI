import pytest

from backend.app.core.config import Settings
from backend.app.core.logging import redact_dict, redact_sensitive_str


def test_cors_wildcard_prohibition():
    with pytest.raises(ValueError, match="strictly prohibited"):
        Settings(CORS_ALLOWED_ORIGINS="http://localhost:3000, *")


def test_log_sanitizer_redacts_tokens_and_secrets():
    log_text = "User authenticated with Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xyz and api_key='sk-proj-123456789'"
    sanitized = redact_sensitive_str(log_text)
    assert "Bearer [REDACTED_TOKEN]" in sanitized
    assert "[REDACTED_KEY]" in sanitized
    assert "sk-proj-123456789" not in sanitized


def test_log_sanitizer_redacts_dict():
    payload = {
        "user_id": "usr-123",
        "email": "user@example.com",
        "password": "supersecretpassword",
        "api_key": "secret-key-xyz",
        "nested": {"token": "token-abc"},
    }
    redacted = redact_dict(payload)
    assert redacted["password"] == "[REDACTED]"
    assert redacted["api_key"] == "[REDACTED]"
    assert redacted["nested"]["token"] == "[REDACTED]"
    assert redacted["user_id"] == "usr-123"
