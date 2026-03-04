import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_db, require_permission
from src.core.permissions import Permission
from src.models.user import User
from src.schemas.report import (
    BoardReportResponse,
    ShiftSummaryResponse,
    WeeklyDigestResponse,
)
from src.services import report_service, pdf_service

router = APIRouter()


@router.get("/shift", response_model=list[ShiftSummaryResponse])
async def get_shift_reports(
    date: str | None = None,
    unit: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.REPORTS_VIEW)),
):
    """Get shift summary reports, optionally filtered by date and unit."""
    reports = await report_service.get_shift_summaries(db, date=date, unit=unit)
    return [ShiftSummaryResponse.model_validate(r) for r in reports]


@router.get("/weekly", response_model=WeeklyDigestResponse)
async def get_weekly_digest(
    unit: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.REPORTS_VIEW)),
):
    """Get the weekly digest report for a unit."""
    digest = await report_service.get_weekly_digest(db, unit=unit)
    return WeeklyDigestResponse.model_validate(digest)


@router.get("/board", response_model=BoardReportResponse)
async def get_board_report(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.REPORTS_BOARD)),
):
    """Get the board-level facility report."""
    report = await report_service.get_board_report(db)
    return BoardReportResponse.model_validate(report)


@router.get("/export/incident/{incident_id}")
async def export_incident_pdf(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.INCIDENTS_EXPORT)),
):
    """Export a single incident as a PDF document."""
    content = await pdf_service.generate_incident_pdf(db, incident_id)
    if not content:
        raise HTTPException(status_code=404, detail="Incident not found")
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=incident_{incident_id}.pdf"
        },
    )


@router.get("/export/board")
async def export_board_pdf(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.REPORTS_BOARD)),
):
    """Export the board report as a PDF document."""
    content = await pdf_service.generate_board_pdf(db)
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=board_report.pdf"},
    )


@router.get("/export/shift/{shift_id}")
async def export_shift_pdf(
    shift_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission(Permission.REPORTS_VIEW)),
):
    """Export a shift summary as a PDF document."""
    content = await pdf_service.generate_shift_pdf(db, shift_id)
    if not content:
        raise HTTPException(status_code=404, detail="Shift report not found")
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=shift_{shift_id}.pdf"
        },
    )
