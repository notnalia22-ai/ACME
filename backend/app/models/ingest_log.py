from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class IngestLog(BaseModel):

    source_id: UUID

    log_year: int

    ingested_at: datetime

    log_id: UUID

    instrument_id: UUID

    status: str

    record_count: int

    error_message: str | None = None

    duration_ms: int
