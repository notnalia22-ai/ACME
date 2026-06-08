from datetime import datetime, timezone
from uuid import UUID
import uuid

from app.models.recommendation import Recommendation


class RecommendationService:

    def __init__(
        self,
        analytics_repo,
        risk_repo,
        recommendation_repo,
    ):
        self._analytics = analytics_repo
        self._risk = risk_repo
        self._recommendations = recommendation_repo

    def generate_recommendation(
        self,
        instrument_id: UUID,
        source_id: UUID,
    ) -> Recommendation | None:

        analytics = list(
            self._analytics.find_all(
                (instrument_id, source_id)
            )
        )

        trend = next(
            (
                a
                for a in analytics
                if a.metric_type == "TREND"
            ),
            None,
        )

        if trend is None:
            return None

        risk = self._risk.find_latest(
            instrument_id
        )

        if risk is None:
            return None

        trend_label = trend.notes
        risk_level = risk.severity

        if trend_label == "UPTREND":

            action = "BUY"

            confidence = (
                "HIGH"
                if risk_level == "LOW"
                else "MEDIUM"
            )

        elif trend_label == "DOWNTREND":

            action = "SELL"

            confidence = (
                "HIGH"
                if risk_level == "HIGH"
                else "MEDIUM"
            )

        else:

            action = "HOLD"

            confidence = "MEDIUM"

        recommendation = Recommendation(
            instrument_id=instrument_id,
            generated_at=datetime.now(
                timezone.utc
            ),
            recommendation_id=uuid.uuid4(),
            action=action,
            confidence=confidence,
            explanation=(
                f"{trend_label} trend with "
                f"{risk_level} risk level"
            ),
            signal_id=risk.signal_id,
        )

        self._recommendations.save(
            recommendation
        )

        return recommendation
