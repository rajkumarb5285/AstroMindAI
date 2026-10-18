from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.ai.orchestrator import AIInterpretationOrchestrator, InterpretationResponse
from backend.app.astrology.rules.engine import AstrologyRuleEngine, ChartRuleEvaluationResult
from backend.app.core.auth import UserContext, get_current_user
from backend.app.db.session import get_db
from backend.app.knowledge.store import global_knowledge_store
from backend.app.repositories.scoped import ChartRepository

router = APIRouter(tags=["AI & Astrology Rules"])


class InterpretRequest(BaseModel):
    question: str = Field(
        ..., min_length=3, max_length=500, examples=["What do the classical texts say about my career and yogas?"]
    )


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=200, examples=["Gaja Kesari Yoga effects"])
    top_k: int = Field(3, ge=1, le=5)


class KnowledgeSearchResponse(BaseModel):
    query: str
    results_count: int
    results: list[dict[str, Any]]


@router.get("/charts/{chart_id}/rules", response_model=ChartRuleEvaluationResult)
async def evaluate_chart_rules(
    chart_id: str,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Deterministically evaluates classical Parashari rules on a verified natal chart.
    Includes dignities (exaltation/debilitation), combustion, Parashari aspects, and classical yogas.
    """
    chart_repo = ChartRepository(db)
    chart = chart_repo.get_by_id(chart_id=chart_id, owner_id=current_user.user_id)
    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart calculation not found.",
        )

    from backend.app.api.v1.charts import reconstruct_chart_calculation_result

    calc_res = reconstruct_chart_calculation_result(chart).model_dump()
    return AstrologyRuleEngine.evaluate(calc_res)


@router.post("/knowledge/search", response_model=KnowledgeSearchResponse)
async def search_classical_knowledge(
    payload: KnowledgeSearchRequest,
    current_user: UserContext = Depends(get_current_user),
):
    """
    Searches allowlisted classical Vedic texts (BPHS, Phaladeepika, Saravali).
    Returns verified citation snippets.
    """
    results = global_knowledge_store.search(payload.query, top_k=payload.top_k)
    return KnowledgeSearchResponse(
        query=payload.query,
        results_count=len(results),
        results=[dict(r) for r in results],
    )


@router.post("/charts/{chart_id}/interpret", response_model=InterpretationResponse)
async def interpret_chart(
    chart_id: str,
    payload: InterpretRequest,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generates a classical, source-grounded astrological interpretation for an authorized chart.
    Strictly isolated and bounded against prompt injection.
    """
    chart_repo = ChartRepository(db)
    chart = chart_repo.get_by_id(chart_id=chart_id, owner_id=current_user.user_id)
    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart calculation not found.",
        )

    orchestrator = AIInterpretationOrchestrator(db=db, user_context=current_user)
    try:
        return orchestrator.interpret(chart_id=chart_id, question=payload.question)
    except PermissionError as pe:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(pe),
        ) from pe
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Interpretation failed: {e}",
        ) from e
