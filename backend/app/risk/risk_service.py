from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID
import uuid

from app.models.risk_signal import RiskSignal


class RiskService:

    def __init__(
        self,
        analytics_repo,
        risk_repo,
    ):
        self._analytics = analytics_repo
        self._risk = risk_repo

    def generate_volatility_risk(
        self,
        instrument_id: UUID,
        source_id: UUID,
    ) -> RiskSignal | None:

        analytics = list(
            self._analytics.find_all(
                (instrument_id, source_id)
            )
        )

        volatility = next(
            (
                a
                for a in analytics
                if a.metric_type == "VOLATILITY"
            ),
            None,
        )

        if volatility is None:
            return None

        value = float(volatility.metric_value)

        if value < 15:
            severity = "LOW"

        elif value < 25:
            severity = "MEDIUM"

        else:
            severity = "HIGH"

        signal = RiskSignal(
            instrument_id=instrument_id,
            generated_at=datetime.now(
                timezone.utc
            ),
            signal_id=uuid.uuid4(),
            signal_type="VOLATILITY_RISK",
            severity=severity,
            value=Decimal(
                str(value)
            ),
            explanation=(
                f"Volatility level classified as "
                f"{severity}"
            ),
            result_id=volatility.result_id,
        )

        self._risk.save(signal)

        return signal
