from decimal import Decimal
from app.analytics.aggregations import (
    calculate_sma,
    calculate_volatility,
    calculate_percent_change,
    calculate_trend,
)
from uuid import UUID
from datetime import datetime, timezone
import uuid

from app.models.analytics_result import AnalyticsResult


class AnalyticsService:

    def __init__(
        self,
        time_series_repo,
        analytics_repo,
    ):
        self._time_series = time_series_repo
        self._analytics = analytics_repo

    def compute_sma_7(
        self,
        instrument_id: UUID,
        source_id: UUID,
        record_year: int,
    ) -> AnalyticsResult | None:

        rows = self._time_series.find_all(
            (instrument_id, source_id, record_year)
        )

        rows = list(rows)

        if len(rows) < 7:
            return None

        # newest first because of clustering order
        latest_rows = rows[:7]

        closes = [
            float(r.close_price)
            for r in latest_rows
            if r.close_price is not None
        ]

        if len(closes) < 7:
            return None

        sma_value = Decimal(str(calculate_sma(closes)))

        result = AnalyticsResult(
            instrument_id=instrument_id,
            source_id=source_id,
            result_id=uuid.uuid4(),
            computed_at=datetime.now(timezone.utc),
            metric_type="SMA_7",
            metric_value=sma_value,
            window_days=7,
            notes="7-day simple moving average",
        )

        self._analytics.save(result)

        return result

    def compute_volatility(
        self,
        instrument_id: UUID,
        source_id: UUID,
        record_year: int,
    ) -> AnalyticsResult | None:

        rows = list(
            self._time_series.find_all(
                (instrument_id, source_id, record_year)
            )
        )

        closes = [
            float(r.close_price)
            for r in rows
            if r.close_price is not None
        ]

        if len(closes) < 2:
            return None

        volatility = Decimal(
            str(
                calculate_volatility(
                    closes
                )
            )
        )

        result = AnalyticsResult(
            instrument_id=instrument_id,
            source_id=source_id,
            result_id=uuid.uuid4(),
            computed_at=datetime.now(
                timezone.utc
            ),
            metric_type="VOLATILITY",
            metric_value=volatility,
            window_days=None,
            notes="Price volatility",
        )

        self._analytics.save(result)

        return result

    def compute_percent_change(
        self,
        instrument_id: UUID,
        source_id: UUID,
        record_year: int,
    ) -> AnalyticsResult | None:

        rows = list(
            self._time_series.find_all(
                (instrument_id, source_id, record_year)
            )
        )

        closes = [
            float(r.close_price)
            for r in rows
            if r.close_price is not None
        ]

        if len(closes) < 2:
            return None

        percent_change = Decimal(
            str(
                calculate_percent_change(
                    closes[-1],
                    closes[0],
                )
            )
        )

        result = AnalyticsResult(
            instrument_id=instrument_id,
            source_id=source_id,
            result_id=uuid.uuid4(),
            computed_at=datetime.now(
                timezone.utc
            ),
            metric_type="PERCENT_CHANGE",
            metric_value=percent_change,
            window_days=None,
            notes="Percentage change",
        )

        self._analytics.save(result)

        return result

    def compute_trend(
        self,
        instrument_id: UUID,
        source_id: UUID,
        record_year: int,
    ) -> AnalyticsResult | None:

        rows = list(
            self._time_series.find_all(
                (instrument_id, source_id, record_year)
            )
        )

        closes = [
            float(r.close_price)
            for r in rows
            if r.close_price is not None
        ]

        if len(closes) < 2:
            return None

        percent_change = calculate_percent_change(
            closes[-1],
            closes[0],
        )

        trend_value, trend_label = calculate_trend(
            percent_change
        )

        result = AnalyticsResult(
            instrument_id=instrument_id,
            source_id=source_id,
            result_id=uuid.uuid4(),
            computed_at=datetime.now(
                timezone.utc
            ),
            metric_type="TREND",
            metric_value=Decimal(
                str(trend_value)
            ),
            window_days=None,
            notes=trend_label,
        )

        self._analytics.save(result)

        return result
