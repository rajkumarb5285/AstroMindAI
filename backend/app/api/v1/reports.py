from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.astrology.rules.engine import AstrologyRuleEngine
from backend.app.astrology.transits.engine import TransitEngine
from backend.app.core.auth import UserContext, get_current_user
from backend.app.db.session import get_db
from backend.app.reports.generator import PDFReportGenerator
from backend.app.reports.storage import report_storage
from backend.app.repositories.scoped import BirthProfileRepository, ChartRepository, ReportRepository

router = APIRouter(tags=["Reports & PDF Generation"])


class ReportJobResponse(BaseModel):
    report_id: str
    chart_id: str
    title: str
    status: str
    download_url: str
    s3_url: str | None = None


class ReportCreateRequest(BaseModel):
    title: str | None = Field(None, max_length=200)


@router.post("/charts/{chart_id}/reports", response_model=ReportJobResponse, status_code=status.HTTP_201_CREATED)
async def generate_chart_report_job(
    chart_id: str,
    payload: ReportCreateRequest | None = None,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    title = payload.title if payload else None
    """
    Generates a deterministic PDF Kundli Report containing ephemeris longitudes,
    classical Parashari yogas, Gochar transits, and Vimshottari dashas.
    Persists to AWS S3 (if configured) and local cache.
    """
    chart_repo = ChartRepository(db)
    chart = chart_repo.get_by_id(chart_id=chart_id, owner_id=current_user.user_id)
    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart calculation not found or access denied.",
        )

    profile_repo = BirthProfileRepository(db)
    profile = profile_repo.get_by_id(str(chart.birth_profile_id), owner_id=current_user.user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Associated birth profile not found.")

    from backend.app.api.v1.charts import reconstruct_chart_calculation_result

    calc_res = reconstruct_chart_calculation_result(chart).model_dump()

    # Deterministic rules & transits
    rules_res = AstrologyRuleEngine.evaluate(calc_res)
    transits_res = TransitEngine.evaluate_transits(
        natal_chart_calc=calc_res,
        ayanamsa=str(chart.ayanamsa) if chart.ayanamsa else "lahiri",
    )

    report_title = title or f"Kundli Report — {profile.name}"
    rep_repo = ReportRepository(db)
    report = rep_repo.create(
        owner_id=current_user.user_id,
        chart_id=chart_id,
        title=report_title,
        report_type="natal_summary",
    )

    # Generate PDF bytes
    profile_dict = {
        "name": profile.name,
        "birth_date": profile.birth_date,
        "birth_time": profile.birth_time,
        "timezone": profile.timezone,
        "birthplace": profile.birthplace,
        "latitude": profile.latitude,
        "longitude": profile.longitude,
    }

    pdf_bytes = PDFReportGenerator.generate_chart_report(
        profile_data=profile_dict,
        chart_calc_data=calc_res,
        rules_data=dict(rules_res),
        transits_data=dict(transits_res),
        report_id=str(report.id),
    )

    # Save to S3 and/or local cache via ReportStorageService
    storage_key = report_storage.save_report(
        report_id=str(report.id),
        pdf_bytes=pdf_bytes,
        chart_id=chart_id,
    )

    report.file_path_key = storage_key  # type: ignore[assignment]
    report.status = "completed"  # type: ignore[assignment]
    db.commit()

    presigned_url = report_storage.generate_presigned_download_url(
        s3_key=storage_key,
        filename=f"astromind_kundli_{str(report.id)[:8]}.pdf",
    )

    return ReportJobResponse(
        report_id=str(report.id),
        chart_id=chart_id,
        title=report_title,
        status="completed",
        download_url=f"/api/v1/reports/{report.id}/download",
        s3_url=presigned_url,
    )


@router.get("/reports/{report_id}/download")
async def download_report_pdf(
    report_id: str,
    current_user: UserContext = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Downloads the generated PDF report with strict object-level authorization.
    Streams directly from S3 or local cache. Rejects unauthorized downloads with HTTP 404.
    """
    rep_repo = ReportRepository(db)
    report = rep_repo.get_by_id(report_id, owner_id=current_user.user_id)
    if not report or not report.file_path_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found or access denied.",
        )

    try:
        content = report_storage.get_report_bytes(
            storage_key=str(report.file_path_key),
            report_id=str(report.id),
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Report file has expired or was removed.") from None

    filename = f"astromind_kundli_{str(report.id)[:8]}.pdf"
    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(content)),
        },
    )
