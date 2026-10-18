from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from backend.app.astrology.adapter import SwissEphAdapter
from backend.app.astrology.constants import ZODIAC_SIGNS
from backend.app.astrology.schemas import (
    CalculationMetadata,
    ChartCalculationInput,
    ChartCalculationResult,
    D9Position,
    HousePosition,
    PlanetaryPosition,
    VimshottariPeriod,
)
from backend.app.core.auth import UserContext, get_current_user
from backend.app.db.session import get_db
from backend.app.models.entities import BirthProfile, ChartCalculation
from backend.app.repositories.scoped import BirthProfileRepository, ChartRepository

router = APIRouter(tags=["Charts"])

# Reusable Ephemeris Adapter instance
astrology_adapter = SwissEphAdapter()


class ChartCreateRequest(BaseModel):
    ayanamsa: str = Field(default="lahiri", examples=["lahiri"])
    node_mode: str = Field(default="mean", examples=["mean", "true"])
    calculation_type: str = Field(default="D1", examples=["D1", "D9"])


class ChartSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    birth_profile_id: str
    calculation_type: str
    engine: str
    engine_version: str
    ayanamsa: str
    node_mode: str
    ascendant: float
    calculation_timestamp: Any


class ChartDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    birth_profile_id: str
    calculation_type: str
    engine: str
    engine_version: str
    config_version: str
    ayanamsa: str
    node_mode: str
    calculation_timestamp: str
    calculation_result: ChartCalculationResult


@router.post(
    "/birth-profiles/{profile_id}/charts",
    response_model=ChartDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Calculate and persist chart for birth profile",
)
async def create_chart_for_profile(
    profile_id: str,
    payload: ChartCreateRequest | None = None,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Execute deterministic Vedic calculations for a user-owned birth profile
    and persist the calculation in chart_calculations.
    """
    req = payload or ChartCreateRequest()

    profile_repo = BirthProfileRepository(db)
    profile = profile_repo.get_by_id(profile_id=profile_id, owner_id=current_user.user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Birth profile not found.",
        )

    # Prepare calculation input from saved birth profile with explicit primitive casting
    calc_input = ChartCalculationInput(
        birth_date=str(profile.birth_date),
        birth_time=str(profile.birth_time) if profile.birth_time else None,
        timezone=str(profile.timezone),
        latitude=float(profile.latitude),
        longitude=float(profile.longitude),
        ayanamsa=req.ayanamsa,
        node_mode=req.node_mode,
        calculation_type=req.calculation_type,
        birth_time_confidence=str(profile.birth_time_confidence),
    )

    # Perform deterministic calculation
    result: ChartCalculationResult = astrology_adapter.calculate_chart(calc_input)

    # Persist in chart_calculations
    chart_repo = ChartRepository(db)
    chart_record = chart_repo.create(
        owner_id=current_user.user_id,
        birth_profile_id=profile_id,
        chart_data={
            "calculation_type": req.calculation_type,
            "engine": result.metadata.engine,
            "engine_version": result.metadata.engine_version,
            "config_version": result.metadata.config_version,
            "ayanamsa": result.metadata.ayanamsa,
            "node_mode": result.metadata.node_mode,
            "planetary_positions": [p.model_dump() for p in result.planets],
            "ascendant": result.ascendant_longitude if result.ascendant_longitude is not None else 0.0,
            "houses": [h.model_dump() for h in result.houses],
            "dasha_data": [d.model_dump() for d in result.vimshottari_dashas],
            "navamsa_data": [d.model_dump() for d in result.navamsa],
        },
    )

    return ChartDetailResponse(
        id=str(chart_record.id),
        owner_id=str(chart_record.owner_id),
        birth_profile_id=str(chart_record.birth_profile_id),
        calculation_type=str(chart_record.calculation_type),
        engine=str(chart_record.engine),
        engine_version=str(chart_record.engine_version),
        config_version=str(chart_record.config_version),
        ayanamsa=str(chart_record.ayanamsa),
        node_mode=str(chart_record.node_mode),
        calculation_timestamp=chart_record.calculation_timestamp.isoformat(),
        calculation_result=result,
    )


def reconstruct_chart_calculation_result(chart: ChartCalculation, is_qualified: bool = True) -> ChartCalculationResult:
    """Reconstruct a typed ChartCalculationResult from persisted ChartCalculation ORM model."""
    raw_planets: list = list(chart.planetary_positions) if isinstance(chart.planetary_positions, list) else []
    planets = [PlanetaryPosition(**p) for p in raw_planets]

    raw_houses: list = list(chart.houses) if isinstance(chart.houses, list) else []
    houses = [HousePosition(**h) for h in raw_houses]

    raw_d9: list = list(chart.navamsa_data) if isinstance(chart.navamsa_data, list) else []
    d9 = [D9Position(**d) for d in raw_d9]

    raw_dashas: list = list(chart.dasha_data) if isinstance(chart.dasha_data, list) else []
    dashas = [VimshottariPeriod(**d) for d in raw_dashas]

    asc_lon = float(chart.ascendant) if is_qualified and chart.ascendant is not None else None
    asc_sign_num = int(asc_lon // 30.0) + 1 if asc_lon is not None else None
    asc_sign_name = ZODIAC_SIGNS[asc_sign_num - 1]["english"] if asc_sign_num else None

    metadata = CalculationMetadata(
        engine=str(chart.engine),
        engine_version=str(chart.engine_version),
        config_version=str(chart.config_version),
        ayanamsa=str(chart.ayanamsa),
        ayanamsa_value=23.578,
        node_mode=str(chart.node_mode),
        normalized_utc_instant=chart.calculation_timestamp.isoformat(),
        julian_day=0.0,
        calculation_timestamp=chart.calculation_timestamp.isoformat(),
        warnings=[] if is_qualified else ["Birth time is unverified. Ascendant and houses are qualified."],
    )

    return ChartCalculationResult(
        metadata=metadata,
        ascendant_longitude=asc_lon,
        ascendant_sign_number=asc_sign_num,
        ascendant_sign_name=asc_sign_name,
        ascendant_degree=asc_lon % 30.0 if asc_lon is not None else None,
        ascendant_nakshatra=None,
        ascendant_pada=None,
        planets=planets,
        houses=houses,
        navamsa=d9,
        vimshottari_dashas=dashas,
        is_birth_time_qualified=is_qualified,
    )


@router.get(
    "/charts/{chart_id}",
    response_model=ChartDetailResponse,
    summary="Get calculated chart by ID",
)
async def get_chart_by_id(
    chart_id: str,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve stored chart calculation with strict object-level authorization.
    Returns 404 if not found or if owned by another user.
    """
    chart_repo = ChartRepository(db)
    chart = chart_repo.get_by_id(chart_id=chart_id, owner_id=current_user.user_id)
    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart calculation not found.",
        )

    profile = db.query(BirthProfile).filter(BirthProfile.id == chart.birth_profile_id).first()
    is_qualified = bool(profile.birth_time_confidence != "unknown") if profile else True
    result = reconstruct_chart_calculation_result(chart, is_qualified=is_qualified)

    return ChartDetailResponse(
        id=str(chart.id),
        owner_id=str(chart.owner_id),
        birth_profile_id=str(chart.birth_profile_id),
        calculation_type=str(chart.calculation_type),
        engine=str(chart.engine),
        engine_version=str(chart.engine_version),
        config_version=str(chart.config_version),
        ayanamsa=str(chart.ayanamsa),
        node_mode=str(chart.node_mode),
        calculation_timestamp=chart.calculation_timestamp.isoformat(),
        calculation_result=result,
    )


@router.get(
    "/birth-profiles/{profile_id}/charts",
    response_model=list[ChartSummaryResponse],
    summary="List saved charts for a birth profile",
)
async def list_charts_for_profile(
    profile_id: str,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all saved calculation runs for a birth profile owned by the user."""
    profile_repo = BirthProfileRepository(db)
    profile = profile_repo.get_by_id(profile_id=profile_id, owner_id=current_user.user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Birth profile not found.",
        )

    charts = (
        db.query(ChartCalculation)
        .filter(ChartCalculation.birth_profile_id == profile_id, ChartCalculation.owner_id == current_user.user_id)
        .order_by(ChartCalculation.calculation_timestamp.desc())
        .all()
    )

    return [ChartSummaryResponse.model_validate(c) for c in charts]
