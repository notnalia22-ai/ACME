from datetime import datetime
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db.connection import get_session
from app.db.repositories.analytics_result import AnalyticsResultRepository
from app.db.repositories.risk_signal import RiskSignalRepository
from app.risk.risk_service import RiskService

router = APIRouter()


class RiskResponse(BaseModel):
    instrument_id: UUID
    signal_type: str
    severity: str
    value: Decimal | None = None
    explanation: str | None = None
    generated_at: datetime


@router.post(
    "/volatility/{instrument_id}/{source_id}",
    response_model=RiskResponse,
)
def generate_volatility_risk(
    instrument_id: UUID,
    source_id: UUID,
):

    session = get_session()

    analytics_repo = AnalyticsResultRepository(session)
    risk_repo = RiskSignalRepository(session)

    service = RiskService(
        analytics_repo,
        risk_repo,
    )

    result = service.generate_volatility_risk(
        instrument_id,
        source_id,
    )

    if result is None:
        raise HTTPException(
            status_code=400,
            detail="No volatility metric found",
        )

    return RiskResponse(
        instrument_id=result.instrument_id,
        signal_type=result.signal_type,
        severity=result.severity,
        value=result.value,
        explanation=result.explanation,
        generated_at=result.generated_at,
    )
