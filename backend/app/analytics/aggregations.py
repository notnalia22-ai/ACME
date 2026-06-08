from decimal import Decimal
from typing import Iterable
from app.models.time_series import TimeSeriesPoint
import statistics


class AggregationResult:
    def __init__(self):
        self.count: int = 0
        self.min_close: Decimal | None = None
        self.max_close: Decimal | None = None
        self.avg_close: Decimal | None = None
        self.total_volume: int = 0


def calculate_sma(values: list[float]) -> float:

    if not values:
        raise ValueError("values cannot be empty")

    return round(sum(values) / len(values), 4)


def compute_aggregations(points: Iterable[TimeSeriesPoint]) -> AggregationResult:
    result = AggregationResult()
    close_values: list[Decimal] = []
    total_volume = 0

    for point in points:
        result.count += 1
        if point.close_price is not None:
            close_values.append(point.close_price)
        if point.volume is not None:
            total_volume += point.volume

    if close_values:
        result.min_close = min(close_values)
        result.max_close = max(close_values)
        result.avg_close = sum(close_values) / len(close_values)

    result.total_volume = total_volume
    return result


def calculate_volatility(values: list[float]) -> float:

    if len(values) < 2:
        raise ValueError(
            "at least two values are required"
        )

    return round(
        statistics.stdev(values),
        4,
    )


def calculate_percent_change(
    first_value: float,
    last_value: float,
) -> float:

    if first_value == 0:
        raise ValueError(
            "first value cannot be zero"
        )

    return round(
        ((last_value - first_value) / first_value) * 100,
        4,
    )


def calculate_trend(
    percent_change: float,
) -> tuple[int, str]:

    if percent_change > 5:
        return 1, "UPTREND"

    if percent_change < -5:
        return -1, "DOWNTREND"

    return 0, "SIDEWAYS"
