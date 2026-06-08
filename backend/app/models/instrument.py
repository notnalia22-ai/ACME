from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class FinancialInstrument(BaseModel):
    instrument_id: UUID
    exchange_id: UUID | None = None

    symbol: str
    instrument_class: str
    name: str

    region: str
    currency: str

    description: str | None = None

    created_at: datetime


class InstrumentSummary(BaseModel):
    instrument_id: UUID

    symbol: str
    instrument_class: str
    name: str

    region: str
