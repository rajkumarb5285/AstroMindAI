import os
import platform
import time
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.core.auth import UserContext, get_current_user
from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.models.entities import AuditEvent

router = APIRouter(tags=["Monitoring & Metrics"])

START_TIME = time.time()


@router.get("/metrics")
def get_system_metrics(
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
) -> dict[str, Any]:
    """
    Returns server telemetry, uptime, engine configuration, and security event counters.
    Requires authenticated user.
    """
    uptime_seconds = int(time.time() - START_TIME)

    # Count audit events if accessible
    try:
        audit_events_count = db.query(func.count(AuditEvent.id)).scalar() or 0
    except Exception:
        audit_events_count = 0

    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "uptime_seconds": uptime_seconds,
        "environment": settings.APP_ENV,
        "system": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "pid": os.getpid(),
        },
        "engine": {
            "name": settings.ASTROLOGY_ENGINE,
            "version": settings.ASTROLOGY_ENGINE_VERSION,
            "config_version": settings.ASTROLOGY_CONFIG_VERSION,
            "ayanamsa": settings.ASTROLOGY_AYANAMSA,
            "node_mode": settings.ASTROLOGY_NODE_MODE,
        },
        "security": {
            "rate_limit_enabled": settings.RATE_LIMIT_ENABLED,
            "rate_limits": {
                "auth_per_min": settings.RATE_LIMIT_AUTH_PER_MINUTE,
                "calc_per_min": settings.RATE_LIMIT_CALCULATION_PER_MINUTE,
                "ai_per_min": settings.RATE_LIMIT_AI_PER_MINUTE,
                "reports_per_min": settings.RATE_LIMIT_REPORTS_PER_MINUTE,
                "default_per_min": settings.RATE_LIMIT_DEFAULT_PER_MINUTE,
            },
            "audit_events_logged": audit_events_count,
        },
    }
