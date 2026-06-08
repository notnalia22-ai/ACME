from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from uuid import UUID

from app.models.time_series import TimeSeriesPoint


# Generic financial market field mapping
_FIELD_MAP: dict[str, str | None] = {
    "date": None,
    "open": "open_price",
    "high": "high_price",
    "low": "low_price",
    "close": "close_price",
    "adj_close": "adj_close",
    "volume": "volume",
    "dividends": "ex_dividend",
    "stock_splits": "split_ratio",
    "ticker": None,
}


def _to_decimal(value) -> Decimal | None:
    if value is None or value == "":
        return None

    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _to_int(value) -> int | None:
    if value is None or value == "":
        return None

    try:
        return int(float(str(value)))
    except (ValueError, TypeError):
        return None


class MarketTransformer:
    """
    Transforms normalized market provider rows
    into warehouse TimeSeriesPoint objects.
    """

    def transform(
        self,
        row: dict,
        instrument_id: UUID,
        source_id: UUID,
        ingested_at: datetime,
    ) -> TimeSeriesPoint:

        if "date" not in row:
            raise ValueError(f"Missing required 'date' field: {row}")

        try:
            record_date = date.fromisoformat(str(row["date"]))
        except Exception:
            raise ValueError(f"Invalid date format: {row['date']}")

        extra = {
            k: str(v)
            for k, v in row.items()
            if k not in _FIELD_MAP
        }

        return TimeSeriesPoint(
            instrument_id=instrument_id,
            source_id=source_id,

            record_year=record_date.year,
            record_date=record_date,

            system_date=ingested_at,
            ingested_at=ingested_at,

            open_price=_to_decimal(row.get("open")),
            close_price=_to_decimal(row.get("close")),
            high_price=_to_decimal(row.get("high")),
            low_price=_to_decimal(row.get("low")),

            adj_close=_to_decimal(row.get("adj_close")),

            volume=_to_int(row.get("volume")),

            ex_dividend=_to_decimal(row.get("dividends")),

            split_ratio=_to_decimal(row.get("stock_splits")),

            extra_indicators=extra,
        )
