from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class PredictionResult(BaseModel):
    instrument_id: UUID
    source_id: UUID

    prediction_id: UUID

    predicted_at: datetime

    model_type: str

    predicted_value: Decimal

    explanation: str | None = None
