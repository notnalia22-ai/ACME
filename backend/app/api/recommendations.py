from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db.connection import get_session

from app.db.repositories.analytics_result import (
    AnalyticsResultRepository,
)
from app.db.repositories.risk_signal import (
    RiskSignalRepository,
)
from app.db.repositories.recommendation import (
    RecommendationRepository,
)

from app.recommendation.recommendation_service import (
    RecommendationService,
)

router = APIRouter()


class RecommendationResponse(BaseModel):
    instrument_id: UUID
    action: str
    confidence: str
    explanation: str | None = None
    generated_at: datetime


@router.post(
    "/{instrument_id}/{source_id}",
    response_model=RecommendationResponse,
)
def generate_recommendation(
    instrument_id: UUID,
    source_id: UUID,
):

    session = get_session()

    service = RecommendationService(
        AnalyticsResultRepository(session),
        RiskSignalRepository(session),
        RecommendationRepository(session),
    )

    result = service.generate_recommendation(
        instrument_id,
        source_id,
    )

    if result is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Trend or risk signal "
                "not available"
            ),
        )

    return RecommendationResponse(
        instrument_id=result.instrument_id,
        action=result.action,
        confidence=result.confidence,
        explanation=result.explanation,
        generated_at=result.generated_at,
    )
