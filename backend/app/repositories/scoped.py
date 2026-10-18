from sqlalchemy.orm import Session

from backend.app.models.entities import (
    BirthProfile,
    ChartCalculation,
    Conversation,
    Message,
    Report,
)


class ScopedRepository:
    """
    Base repository enforcing object-level authorization (BOLA / IDOR defense).
    Every single query explicitly requires and filters on the authenticated owner_id.
    """

    def __init__(self, db: Session):
        self.db = db


class BirthProfileRepository(ScopedRepository):
    def get_by_id(self, profile_id: str, owner_id: str) -> BirthProfile | None:
        """Fetch profile strictly scoped to the authenticated owner."""
        return (
            self.db.query(BirthProfile).filter(BirthProfile.id == profile_id, BirthProfile.owner_id == owner_id).first()
        )

    def list_by_owner(self, owner_id: str, skip: int = 0, limit: int = 50) -> list[BirthProfile]:
        return (
            self.db.query(BirthProfile)
            .filter(BirthProfile.owner_id == owner_id)
            .order_by(BirthProfile.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, owner_id: str, data: dict) -> BirthProfile:
        # Guarantee owner_id is set from trusted server context, never from client input
        profile = BirthProfile(
            owner_id=owner_id,
            name=data["name"],
            birth_date=data["birth_date"],
            birth_time=data.get("birth_time"),
            timezone=data["timezone"],
            birthplace=data["birthplace"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            birth_time_confidence=data.get("birth_time_confidence", "exact"),
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update(self, profile_id: str, owner_id: str, data: dict) -> BirthProfile | None:
        profile = self.get_by_id(profile_id, owner_id)
        if not profile:
            return None

        # Disallow tampering with id or owner_id
        forbidden_fields = {"id", "owner_id", "created_at"}
        for key, value in data.items():
            if key not in forbidden_fields and hasattr(profile, key):
                setattr(profile, key, value)

        self.db.commit()
        self.db.refresh(profile)
        return profile

    def delete(self, profile_id: str, owner_id: str) -> bool:
        profile = self.get_by_id(profile_id, owner_id)
        if not profile:
            return False
        self.db.delete(profile)
        self.db.commit()
        return True


class ChartRepository(ScopedRepository):
    def get_by_id(self, chart_id: str, owner_id: str) -> ChartCalculation | None:
        return (
            self.db.query(ChartCalculation)
            .filter(ChartCalculation.id == chart_id, ChartCalculation.owner_id == owner_id)
            .first()
        )

    def list_by_owner(self, owner_id: str, skip: int = 0, limit: int = 50) -> list[ChartCalculation]:
        return (
            self.db.query(ChartCalculation)
            .filter(ChartCalculation.owner_id == owner_id)
            .order_by(ChartCalculation.calculation_timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, owner_id: str, birth_profile_id: str, chart_data: dict) -> ChartCalculation:
        # Verify birth profile belongs to this owner first
        profile = (
            self.db.query(BirthProfile)
            .filter(BirthProfile.id == birth_profile_id, BirthProfile.owner_id == owner_id)
            .first()
        )
        if not profile:
            raise PermissionError("Access denied: Birth profile does not belong to authenticated user.")

        chart = ChartCalculation(
            owner_id=owner_id,
            birth_profile_id=birth_profile_id,
            calculation_type=chart_data.get("calculation_type", "D1"),
            engine=chart_data.get("engine", "pyswisseph"),
            engine_version=chart_data.get("engine_version", "2.10.3"),
            config_version=chart_data.get("config_version", "vedic-v1"),
            ayanamsa=chart_data.get("ayanamsa", "lahiri"),
            node_mode=chart_data.get("node_mode", "mean"),
            planetary_positions=chart_data.get("planetary_positions", []),
            ascendant=chart_data.get("ascendant", 0.0),
            houses=chart_data.get("houses", []),
            dasha_data=chart_data.get("dasha_data"),
            navamsa_data=chart_data.get("navamsa_data"),
        )
        self.db.add(chart)
        self.db.commit()
        self.db.refresh(chart)
        return chart

    def delete(self, chart_id: str, owner_id: str) -> bool:
        chart = self.get_by_id(chart_id, owner_id)
        if not chart:
            return False
        self.db.delete(chart)
        self.db.commit()
        return True


class ConversationRepository(ScopedRepository):
    def get_by_id(self, conversation_id: str, owner_id: str) -> Conversation | None:
        return (
            self.db.query(Conversation)
            .filter(Conversation.id == conversation_id, Conversation.owner_id == owner_id)
            .first()
        )

    def create(self, owner_id: str, title: str = "New Consultation", chart_id: str | None = None) -> Conversation:
        conv = Conversation(owner_id=owner_id, title=title, chart_id=chart_id)
        self.db.add(conv)
        self.db.commit()
        self.db.refresh(conv)
        return conv

    def add_message(self, conversation_id: str, owner_id: str, sender_type: str, content: str) -> Message | None:
        conv = self.get_by_id(conversation_id, owner_id)
        if not conv:
            return None

        msg = Message(
            conversation_id=conversation_id,
            owner_id=owner_id,
            sender_type=sender_type,
            content=content,
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def delete(self, conversation_id: str, owner_id: str) -> bool:
        conv = self.get_by_id(conversation_id, owner_id)
        if not conv:
            return False
        self.db.delete(conv)
        self.db.commit()
        return True


class ReportRepository(ScopedRepository):
    def get_by_id(self, report_id: str, owner_id: str) -> Report | None:
        return self.db.query(Report).filter(Report.id == report_id, Report.owner_id == owner_id).first()

    def create(self, owner_id: str, chart_id: str, title: str, report_type: str) -> Report:
        report = Report(
            owner_id=owner_id,
            chart_id=chart_id,
            title=title,
            report_type=report_type,
            status="pending",
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def delete(self, report_id: str, owner_id: str) -> bool:
        report = self.get_by_id(report_id, owner_id)
        if not report:
            return False
        self.db.delete(report)
        self.db.commit()
        return True
