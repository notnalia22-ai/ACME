from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID
import uuid

import numpy as np

from app.models.prediction_result import (
    PredictionResult,
)


class PredictionService:

    def __init__(
        self,
        time_series_repo,
        prediction_repo,
    ):
        self._time_series = time_series_repo
        self._predictions = prediction_repo

    def predict_next_close(
        self,
        instrument_id: UUID,
        source_id: UUID,
        record_year: int,
    ) -> PredictionResult | None:

        rows = list(
            self._time_series.find_all(
                (
                    instrument_id,
                    source_id,
                    record_year,
                )
            )
        )

        closes = [
            float(r.close_price)
            for r in reversed(rows)
            if r.close_price is not None
        ]

        if len(closes) < 10:
            return None

        split_idx = int(
            len(closes) * 0.8
        )

        train = closes[:split_idx]

        test = closes[split_idx:]

        x_train = np.arange(
            len(train)
        )

        y_train = np.array(
            train
        )

        slope, intercept = np.polyfit(
            x_train,
            y_train,
            1,
        )

        x_test = np.arange(
            len(train),
            len(closes),
        )

        predictions = (
            slope * x_test
            + intercept
        )

        mae = np.mean(
            np.abs(
                predictions
                - np.array(test)
            )
        )

        # retrain on full dataset
        x = np.arange(
            len(closes)
        )

        y = np.array(
            closes
        )

        slope, intercept = np.polyfit(
            x,
            y,
            1,
        )

        next_day = len(closes)

        predicted_close = (
            slope * next_day
            + intercept
        )

        result = PredictionResult(
            instrument_id=instrument_id,
            source_id=source_id,
            prediction_id=uuid.uuid4(),
            predicted_at=datetime.now(
                timezone.utc
            ),
            model_type="LINEAR_REGRESSION",
            predicted_value=Decimal(
                str(
                    round(
                        predicted_close,
                        4,
                    )
                )
            ),
            explanation=(
                f"Linear regression "
                f"(MAE={round(mae, 4)})"
            ),
        )

        self._predictions.save(
            result
        )

        return result
