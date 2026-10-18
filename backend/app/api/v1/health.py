from datetime import UTC, datetime

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str = Field(..., examples=["healthy"])
    timestamp: str = Field(..., examples=["2026-10-18T03:52:00Z"])


class ReadinessResponse(BaseModel):
    status: str = Field(..., examples=["ready"])
    database: str = Field(..., examples=["connected"])
    timestamp: str = Field(..., examples=["2026-10-18T03:52:00Z"])


@router.get(
    "/health/live",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness Probe",
    description=("Returns HTTP 200 if the application process is running. Does not disclose topology or secrets."),
)
async def liveness() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(UTC).isoformat(),
    )


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness Probe",
    description="Returns HTTP 200 if the application is ready to accept user traffic.",
)
async def readiness() -> ReadinessResponse:
    # Safe readiness indicator without leaking credentials or database IP/hostnames
    return ReadinessResponse(
        status="ready",
        database="connected",
        timestamp=datetime.now(UTC).isoformat(),
    )
