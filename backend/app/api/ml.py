from datetime import datetime
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db.connection import get_session

from app.db.repositories.time_series import (
    TimeSeriesRepository,
)

from app.db.repositories.prediction_result import (
    PredictionResultRepository,
)

from app.ml.prediction_service import (
    PredictionService,
)

router = APIRouter()


class PredictionResponse(BaseModel):
    instrument_id: UUID
    source_id: UUID

    model_type: str

    predicted_value: Decimal

    explanation: str | None = None

    predicted_at: datetime


@router.post(
    "/predict/{instrument_id}/{source_id}/{record_year}",
    response_model=PredictionResponse,
)
def predict_next_close(
    instrument_id: UUID,
    source_id: UUID,
    record_year: int,
):

    session = get_session()

    service = PredictionService(
        TimeSeriesRepository(session),
        PredictionResultRepository(session),
    )

    result = service.predict_next_close(
        instrument_id,
        source_id,
        record_year,
    )

    if result is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Not enough data "
                "for prediction"
            ),
        )

    return PredictionResponse(
        instrument_id=result.instrument_id,
        source_id=result.source_id,
        model_type=result.model_type,
        predicted_value=result.predicted_value,
        explanation=result.explanation,
        predicted_at=result.predicted_at,
    )
