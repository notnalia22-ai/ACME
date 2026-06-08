from fastapi import APIRouter, Query
from pydantic import BaseModel
from uuid import UUID
from datetime import date
from decimal import Decimal
from datetime import datetime
from app.analytics.analytics_service import AnalyticsService
from app.db.repositories.analytics_result import AnalyticsResultRepository
from app.db.connection import get_session
from app.db.repositories.time_series import TimeSeriesRepository
from app.analytics.aggregations import compute_aggregations
from fastapi import HTTPException

router = APIRouter()


class AnalyticsResponse(BaseModel):
    instrument_id: UUID
    source_id: UUID
    start_date: date
    end_date: date
    count: int
    min_close: Decimal | None = None
    max_close: Decimal | None = None
    avg_close: Decimal | None = None
    total_volume: int


class SMAResponse(BaseModel):
    instrument_id: UUID
    source_id: UUID
    metric_type: str
    metric_value: Decimal
    window_days: int
    computed_at: datetime


class MetricResponse(BaseModel):
    instrument_id: UUID
    source_id: UUID
    metric_type: str
    metric_value: Decimal
    computed_at: datetime


@router.get("/{instrument_id}/{source_id}", response_model=AnalyticsResponse)
def get_analytics(
    instrument_id: UUID,
    source_id: UUID,
    start_date: date = Query(default=None),
    end_date: date = Query(default=None),
):
    """Return min/max/avg close price and total volume for an asset over a date range."""
    if start_date is None:
        start_date = date(2000, 1, 1)
    if end_date is None:
        end_date = date.today()

    session = get_session()
    repo = TimeSeriesRepository(session)
    points = repo.find_range(instrument_id, source_id, start_date, end_date)
    agg = compute_aggregations(points)

    return AnalyticsResponse(
        instrument_id=instrument_id,
        source_id=source_id,
        start_date=start_date,
        end_date=end_date,
        count=agg.count,
        min_close=agg.min_close,
        max_close=agg.max_close,
        avg_close=agg.avg_close,
        total_volume=agg.total_volume,
    )


@router.post(
    "/sma/{instrument_id}/{source_id}/{record_year}",
    response_model=SMAResponse,
)
def compute_sma(
    instrument_id: UUID,
    source_id: UUID,
    record_year: int,
):

    session = get_session()

    time_series_repo = TimeSeriesRepository(session)

    analytics_repo = AnalyticsResultRepository(session)

    service = AnalyticsService(
        time_series_repo,
        analytics_repo,
    )

    result = service.compute_sma_7(
        instrument_id=instrument_id,
        source_id=source_id,
        record_year=record_year,
    )

    if result is None:
        raise HTTPException(
            status_code=400,
            detail="Not enough data to compute SMA_7",
        )

    return SMAResponse(
        instrument_id=result.instrument_id,
        source_id=result.source_id,
        metric_type=result.metric_type,
        metric_value=result.metric_value,
        window_days=result.window_days,
        computed_at=result.computed_at,
    )


@router.post(
    "/volatility/{instrument_id}/{source_id}/{record_year}",
    response_model=MetricResponse,
)
def compute_volatility(
    instrument_id: UUID,
    source_id: UUID,
    record_year: int,
):

    session = get_session()

    service = AnalyticsService(
        TimeSeriesRepository(session),
        AnalyticsResultRepository(session),
    )

    result = service.compute_volatility(
        instrument_id,
        source_id,
        record_year,
    )

    if result is None:
        raise HTTPException(
            status_code=400,
            detail="Not enough data to compute volatility",
        )

    return MetricResponse(
        instrument_id=result.instrument_id,
        source_id=result.source_id,
        metric_type=result.metric_type,
        metric_value=result.metric_value,
        computed_at=result.computed_at,
    )


@router.post(
    "/percent-change/{instrument_id}/{source_id}/{record_year}",
    response_model=MetricResponse,
)
def compute_percent_change(
    instrument_id: UUID,
    source_id: UUID,
    record_year: int,
):

    session = get_session()

    service = AnalyticsService(
        TimeSeriesRepository(session),
        AnalyticsResultRepository(session),
    )

    result = service.compute_percent_change(
        instrument_id,
        source_id,
        record_year,
    )

    if result is None:
        raise HTTPException(
            status_code=400,
            detail="Not enough data to compute percent change",
        )

    return MetricResponse(
        instrument_id=result.instrument_id,
        source_id=result.source_id,
        metric_type=result.metric_type,
        metric_value=result.metric_value,
        computed_at=result.computed_at,
    )


@router.post(
    "/trend/{instrument_id}/{source_id}/{record_year}",
    response_model=MetricResponse,
)
def compute_trend(
    instrument_id: UUID,
    source_id: UUID,
    record_year: int,
):

    session = get_session()

    service = AnalyticsService(
        TimeSeriesRepository(session),
        AnalyticsResultRepository(session),
    )

    result = service.compute_trend(
        instrument_id,
        source_id,
        record_year,
    )

    if result is None:
        raise HTTPException(
            status_code=400,
            detail="Not enough data to compute trend",
        )

    return MetricResponse(
        instrument_id=result.instrument_id,
        source_id=result.source_id,
        metric_type=result.metric_type,
        metric_value=result.metric_value,
        computed_at=result.computed_at,
    )
