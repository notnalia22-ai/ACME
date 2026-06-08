from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class Recommendation(BaseModel):
    instrument_id: UUID
    generated_at: datetime
    recommendation_id: UUID

    action: str
    confidence: str

    explanation: str | None = None

    signal_id: UUID | None = None
