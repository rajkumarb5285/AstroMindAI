import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

from backend.app.db.session import Base

# Universal JSON type compatible with both PostgreSQL JSONB and SQLite JSON
JSONType = JSON().with_variant(JSONB, "postgresql")


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(UTC)


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False, default="user")  # 'user', 'admin'
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    birth_profiles = relationship("BirthProfile", back_populates="owner", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="owner", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="owner", cascade="all, delete-orphan")


class BirthProfile(Base):
    __tablename__ = "birth_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    owner_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    birth_date = Column(String(10), nullable=False)  # YYYY-MM-DD
    birth_time = Column(String(8), nullable=True)  # HH:MM:SS (optional for unknown birth time)
    timezone = Column(String(100), nullable=False)  # IANA e.g. "Asia/Kolkata", "America/New_York"
    birthplace = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    birth_time_confidence = Column(String(50), nullable=False, default="exact")  # 'exact', 'approximate', 'unknown'
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    owner = relationship("Profile", back_populates="birth_profiles")
    charts = relationship("ChartCalculation", back_populates="birth_profile", cascade="all, delete-orphan")


class ChartCalculation(Base):
    __tablename__ = "chart_calculations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    owner_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    birth_profile_id = Column(
        String(36), ForeignKey("birth_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    calculation_type = Column(String(50), nullable=False, default="D1")  # 'D1', 'D9', 'transit'
    engine = Column(String(100), nullable=False)  # e.g. 'pyswisseph'
    engine_version = Column(String(50), nullable=False)
    config_version = Column(String(50), nullable=False)
    ayanamsa = Column(String(50), nullable=False, default="lahiri")
    node_mode = Column(String(50), nullable=False, default="mean")
    planetary_positions = Column(JSONType, nullable=False)  # Array of planet objects
    ascendant = Column(Float, nullable=False)  # Longitude 0-360
    houses = Column(JSONType, nullable=False)  # Array of 12 houses
    dasha_data = Column(JSONType, nullable=True)  # Vimshottari intervals
    navamsa_data = Column(JSONType, nullable=True)  # D9 positions
    calculation_timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    birth_profile = relationship("BirthProfile", back_populates="charts")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    owner_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    chart_id = Column(
        String(36),
        ForeignKey("chart_calculations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title = Column(String(255), nullable=False, default="New Consultation")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    owner = relationship("Profile", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_type = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    citations = Column(JSONType, nullable=True)  # Citations linking to knowledge sources
    tool_run_ids = Column(JSONType, nullable=True)  # Traceability of executed tools
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")
    tool_runs = relationship("ChatToolRun", back_populates="message", cascade="all, delete-orphan")


class ChatToolRun(Base):
    __tablename__ = "chat_tool_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    message_id = Column(String(36), ForeignKey("messages.id", ondelete="CASCADE"), nullable=True, index=True)
    owner_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    tool_name = Column(String(100), nullable=False)
    tool_input = Column(JSONType, nullable=False)
    tool_output = Column(JSONType, nullable=False)
    status = Column(String(50), nullable=False)  # 'success', 'error', 'denied'
    execution_time_ms = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    message = relationship("Message", back_populates="tool_runs")


class KnowledgeSource(Base):
    __tablename__ = "knowledge_sources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    source_type = Column(String(100), nullable=False)  # 'classical_text', 'commentary', 'rulebook'
    author = Column(String(255), nullable=True)
    publication_year = Column(Integer, nullable=True)
    license_type = Column(String(100), nullable=False)  # 'public_domain', 'proprietary_licensed'
    license_proof_url = Column(String(500), nullable=True)
    content_hash = Column(String(64), nullable=False, unique=True)  # SHA-256 for audit & immutability
    is_approved = Column(Boolean, default=False, nullable=False)
    reviewed_by = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    chunks = relationship("KnowledgeChunk", back_populates="source", cascade="all, delete-orphan")
    rules = relationship("AstrologyRule", back_populates="source")


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    source_id = Column(
        String(36),
        ForeignKey("knowledge_sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    metadata_tags = Column(JSONType, nullable=True)
    embedding = Column(JSONType, nullable=True)  # Stored as JSON or pgvector vector column
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    source = relationship("KnowledgeSource", back_populates="chunks")


class AstrologyRule(Base):
    __tablename__ = "astrology_rules"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    rule_id = Column(String(100), unique=True, nullable=False, index=True)
    rule_name = Column(String(255), nullable=False)
    rule_version = Column(String(50), nullable=False, default="1.0")
    category = Column(String(100), nullable=False)  # 'yoga', 'dasha', 'house_placement', 'transit'
    conditions = Column(JSONType, nullable=False)  # Structured rules criteria
    interpretation_template = Column(Text, nullable=False)
    citation_source_id = Column(String(36), ForeignKey("knowledge_sources.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    source = relationship("KnowledgeSource", back_populates="rules")


class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    owner_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    chart_id = Column(
        String(36),
        ForeignKey("chart_calculations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(255), nullable=False)
    report_type = Column(String(50), nullable=False)  # 'natal_summary', 'dasha_transit', 'compatibility'
    status = Column(String(50), nullable=False, default="pending")  # 'pending', 'completed', 'failed'
    file_path_key = Column(String(500), nullable=True)  # Private object storage key
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    owner = relationship("Profile", back_populates="reports")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(
        String(36),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    tier = Column(String(50), nullable=False, default="free")  # 'free', 'pro', 'enterprise'
    status = Column(String(50), nullable=False, default="active")  # 'active', 'canceled', 'past_due'
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class UsageEvent(Base):
    __tablename__ = "usage_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)  # 'chart_calculated', 'chat_completion', 'pdf_generated'
    tokens_used = Column(Integer, default=0, nullable=False)
    cost_usd = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class ConsentRecord(Base):
    __tablename__ = "consent_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    consent_type = Column(String(100), nullable=False)  # 'terms_of_service', 'privacy_policy', 'analytics'
    granted = Column(Boolean, nullable=False)
    granted_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    ip_hash = Column(String(64), nullable=True)  # Anonymized SHA-256 hash of IP


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    event_name = Column(String(100), nullable=False, index=True)
    actor_id = Column(String(36), nullable=False, index=True)
    target_resource = Column(String(100), nullable=False)
    target_id = Column(String(36), nullable=True)
    details = Column(JSONType, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv4/IPv6
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
