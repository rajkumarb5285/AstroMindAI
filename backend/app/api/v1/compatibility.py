from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.astrology.compatibility.ashta_koota import (
    CompatibilityResult,
    calculate_ashta_koota,
)
from backend.app.core.auth import UserContext, get_current_user
from backend.app.db.session import get_db
from backend.app.repositories.scoped import ChartRepository

router = APIRouter(prefix="/compatibility", tags=["Compatibility & Ashta Koota"])


class CompatibilityRequest(BaseModel):
    bride_chart_id: str | None = Field(None, description="Chart ID of the Bride")
    groom_chart_id: str | None = Field(None, description="Chart ID of the Groom")
    # Alternatively allow direct coordinates/nakshatras for testing
    bride_moon_sign: int | None = Field(None, ge=1, le=12)
    bride_nakshatra: int | None = Field(None, ge=1, le=27)
    bride_pada: int | None = Field(1, ge=1, le=4)
    groom_moon_sign: int | None = Field(None, ge=1, le=12)
    groom_nakshatra: int | None = Field(None, ge=1, le=27)
    groom_pada: int | None = Field(1, ge=1, le=4)


@router.post("", response_model=CompatibilityResult)
async def evaluate_compatibility(
    payload: CompatibilityRequest,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Computes classical 36-point Parashari Ashta Koota compatibility (Guna Milan).
    Supports either two saved chart IDs with owner authorization, or direct Moon coordinates.
    """
    chart_repo = ChartRepository(db)

    # 1. Resolve Bride Moon parameters
    if payload.bride_chart_id:
        b_chart = chart_repo.get_by_id(payload.bride_chart_id, owner_id=current_user.user_id)
        if not b_chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bride chart '{payload.bride_chart_id}' not found or access denied.",
            )
        from backend.app.api.v1.charts import reconstruct_chart_calculation_result

        b_calc = reconstruct_chart_calculation_result(b_chart).model_dump()
        b_moon = next((p for p in b_calc.get("planets", []) if p.get("planet_id") == "Moon"), None)
        if not b_moon:
            raise HTTPException(status_code=400, detail="Bride chart calculation missing Moon placement.")
        b_sign = b_moon.get("sign_number", 1)
        b_nak = b_moon.get("nakshatra_index", 1)
        b_pada = b_moon.get("pada", 1)
    else:
        if payload.bride_moon_sign is None or payload.bride_nakshatra is None:
            raise HTTPException(status_code=400, detail="Provide either bride_chart_id or bride_moon_sign & bride_nakshatra.")
        b_sign = payload.bride_moon_sign
        b_nak = payload.bride_nakshatra
        b_pada = payload.bride_pada or 1

    # 2. Resolve Groom Moon parameters
    if payload.groom_chart_id:
        g_chart = chart_repo.get_by_id(payload.groom_chart_id, owner_id=current_user.user_id)
        if not g_chart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Groom chart '{payload.groom_chart_id}' not found or access denied.",
            )
        from backend.app.api.v1.charts import reconstruct_chart_calculation_result

        g_calc = reconstruct_chart_calculation_result(g_chart).model_dump()
        g_moon = next((p for p in g_calc.get("planets", []) if p.get("planet_id") == "Moon"), None)
        if not g_moon:
            raise HTTPException(status_code=400, detail="Groom chart calculation missing Moon placement.")
        g_sign = g_moon.get("sign_number", 1)
        g_nak = g_moon.get("nakshatra_index", 1)
        g_pada = g_moon.get("pada", 1)
    else:
        if payload.groom_moon_sign is None or payload.groom_nakshatra is None:
            raise HTTPException(status_code=400, detail="Provide either groom_chart_id or groom_moon_sign & groom_nakshatra.")
        g_sign = payload.groom_moon_sign
        g_nak = payload.groom_nakshatra
        g_pada = payload.groom_pada or 1

    return calculate_ashta_koota(
        bride_moon_sign=b_sign,
        bride_nakshatra=b_nak,
        bride_pada=b_pada,
        groom_moon_sign=g_sign,
        groom_nakshatra=g_nak,
        groom_pada=g_pada,
    )
