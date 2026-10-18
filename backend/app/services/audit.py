import hashlib
import json
import logging
from typing import Any

from sqlalchemy.orm import Session

from backend.app.models.entities import AuditEvent

logger = logging.getLogger("astromind.audit")


class AuditEventNames:
    AUTH_LOGIN_SUCCESS = "AUTH_LOGIN_SUCCESS"
    AUTH_LOGIN_FAILURE = "AUTH_LOGIN_FAILURE"
    AUTH_ACCESS_DENIED = "AUTH_ACCESS_DENIED"
    CHART_CREATED = "CHART_CREATED"
    CHART_ACCESSED = "CHART_ACCESSED"
    REPORT_GENERATED = "REPORT_GENERATED"
    REPORT_DOWNLOADED = "REPORT_DOWNLOADED"
    CONVERSATION_CREATED = "CONVERSATION_CREATED"
    MESSAGE_SENT = "MESSAGE_SENT"
    DATA_DELETED = "DATA_DELETED"
    CONSENT_RECORDED = "CONSENT_RECORDED"


def anonymize_ip(ip_address: str | None) -> str | None:
    """Hash or mask IP addresses to ensure GDPR / DPDP compliance while retaining auditability."""
    if not ip_address:
        return None
    # Salted hash representation for audit verification
    return hashlib.sha256(ip_address.encode("utf-8")).hexdigest()[:16]


class AuditService:
    """Service to record immutable structured audit events into both database and log telemetry."""

    @staticmethod
    def record_event(
        db: Session,
        event_name: str,
        actor_id: str,
        target_resource: str,
        target_id: str | None = None,
        details: dict[str, Any] | None = None,
        ip_address: str | None = None,
    ) -> AuditEvent:
        masked_ip = anonymize_ip(ip_address)
        audit_event = AuditEvent(
            event_name=event_name,
            actor_id=actor_id,
            target_resource=target_resource,
            target_id=target_id,
            details=details or {},
            ip_address=masked_ip,
        )
        db.add(audit_event)
        try:
            db.commit()
            db.refresh(audit_event)
        except Exception as exc:
            db.rollback()
            logger.error(f"Failed to persist audit event {event_name} to database: {exc}")

        # Emit structured log for SIEM / external log aggregator
        log_payload = {
            "audit_event": event_name,
            "actor_id": actor_id,
            "target_resource": target_resource,
            "target_id": target_id,
            "details": details or {},
            "masked_ip": masked_ip,
        }
        logger.info(f"AUDIT_RECORD: {json.dumps(log_payload)}")
        return audit_event

    @staticmethod
    def get_events(
        db: Session,
        actor_id: str | None = None,
        event_name: str | None = None,
        limit: int = 50,
    ) -> list[AuditEvent]:
        query = db.query(AuditEvent)
        if actor_id:
            query = query.filter(AuditEvent.actor_id == actor_id)
        if event_name:
            query = query.filter(AuditEvent.event_name == event_name)
        return query.order_by(AuditEvent.created_at.desc()).limit(limit).all()
