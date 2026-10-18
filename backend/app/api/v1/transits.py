from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.astrology.transits.engine import (
    GocharEvaluationResult,
    TransitEngine,
)
from backend.app.core.auth import UserContext, get_current_user
from backend.app.db.session import get_db
from backend.app.repositories.scoped import ChartRepository

router = APIRouter(tags=["Gochar & Planetary Transits"])


@router.get("/charts/{chart_id}/transits", response_model=GocharEvaluationResult)
async def get_chart_transits(
    chart_id: str,
    target_date: str | None = Query(
        None,
        description="ISO date string for transit calculation e.g. '2026-10-18T10:00:00Z'. Defaults to current moment.",
    ),
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Computes real-time or historical planetary Gochar transits projected onto natal Moon and Ascendant.
    Includes Sade Sati, Kantaka Shani, and Ashtama Shani status.
    """
    chart_repo = ChartRepository(db)
    chart = chart_repo.get_by_id(chart_id=chart_id, owner_id=current_user.user_id)
    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart calculation not found or access denied.",
        )

    from backend.app.api.v1.charts import reconstruct_chart_calculation_result

    natal_calc = reconstruct_chart_calculation_result(chart).model_dump()

    transit_dt = None
    if target_date:
        try:
            transit_dt = datetime.fromisoformat(target_date.replace("Z", "+00:00"))
        except ValueError as err:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid target_date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ).",
            ) from err
    else:
        transit_dt = datetime.now(UTC)

    return TransitEngine.evaluate_transits(
        natal_chart_calc=natal_calc,
        transit_dt=transit_dt,
        ayanamsa=str(chart.ayanamsa) if chart.ayanamsa else "lahiri",
    )
