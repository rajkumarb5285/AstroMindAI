import json
import logging
import re
import sys
from datetime import UTC, datetime
from typing import Any

# Regex patterns to sanitize sensitive tokens, keys, passwords, and birth details
REDACTION_PATTERNS = [
    (re.compile(r"(?i)(bearer\s+)[a-zA-Z0-9_\-\.]+"), r"\1[REDACTED_TOKEN]"),
    (re.compile(r'(?i)(api[_-]?key["\']?\s*[:=]\s*["\']?)[a-zA-Z0-9_\-\.]+'), r"\1[REDACTED_KEY]"),
    (re.compile(r'(?i)(password["\']?\s*[:=]\s*["\']?)[^"\'\s]+'), r"\1[REDACTED_PASSWORD]"),
    (re.compile(r'(?i)(secret["\']?\s*[:=]\s*["\']?)[^"\'\s]+'), r"\1[REDACTED_SECRET]"),
    (re.compile(r'(?i)(service_role_key["\']?\s*[:=]\s*["\']?)[^"\'\s]+'), r"\1[REDACTED_KEY]"),
    # Redact explicit birth dates in query strings or payloads if accidentally logged: YYYY-MM-DD
    (
        re.compile(r"\b(19\d\d|20\d\d)[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])\b"),
        "[REDACTED_DATE]",
    ),
]


def redact_sensitive_str(text: str) -> str:
    """Sanitize sensitive patterns from log strings."""
    for pattern, replacement in REDACTION_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def redact_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Recursively redact sensitive dictionary fields."""
    redacted: dict[str, Any] = {}
    sensitive_keys = {
        "password",
        "secret",
        "token",
        "api_key",
        "service_role_key",
        "authorization",
        "llm_api_key",
        "supabase_service_role_key",
        "birth_date",
        "birth_time",
    }
    for k, v in data.items():
        if k.lower() in sensitive_keys:
            redacted[k] = "[REDACTED]"
        elif isinstance(v, dict):
            redacted[k] = redact_dict(v)
        elif isinstance(v, str):
            redacted[k] = redact_sensitive_str(v)
        else:
            redacted[k] = v
    return redacted


class JSONFormatter(logging.Formatter):
    """Structured JSON formatter outputting machine-parseable, redacted log records."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": redact_sensitive_str(record.getMessage()),
        }

        # Include request_id if available on the record
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Configure the root logger with the security-compliant JSONFormatter."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root_logger.addHandler(handler)

    # Silence overly verbose external loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    return root_logger
