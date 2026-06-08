from typing import Iterable
from uuid import UUID

from app.db.repositories.base import (
    CassandraRepository,
    WarehouseRepository,
)
from app.models.prediction_result import (
    PredictionResult,
)


class PredictionResultRepository(
    CassandraRepository,
    WarehouseRepository[PredictionResult, UUID],
):

    def __init__(self, session):
        super().__init__(session)

        self._insert = session.prepare(
            """
            INSERT INTO prediction_results
            (
                instrument_id,
                source_id,
                predicted_at,
                prediction_id,
                model_type,
                predicted_value,
                explanation
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
        )

        self._select_latest = session.prepare(
            """
            SELECT *
            FROM prediction_results
            WHERE instrument_id = ?
            AND source_id = ?
            LIMIT 1
            """
        )

        self._select_all = session.prepare(
            """
            SELECT *
            FROM prediction_results
            WHERE instrument_id = ?
            AND source_id = ?
            """
        )

    def save(
        self,
        entity: PredictionResult,
    ) -> PredictionResult:

        self._execute(
            self._insert,
            [
                entity.instrument_id,
                entity.source_id,
                entity.predicted_at,
                entity.prediction_id,
                entity.model_type,
                entity.predicted_value,
                entity.explanation,
            ],
        )

        return entity

    def delete(self, key: UUID) -> None:
        pass

    def delete_all(
        self,
        partition_key: UUID,
    ) -> None:
        pass

    def find_latest(
        self,
        partition_key,
    ) -> PredictionResult | None:

        instrument_id, source_id = partition_key

        row = self._fetch_one(
            self._select_latest,
            [
                instrument_id,
                source_id,
            ],
        )

        return (
            self._row_to_model(row)
            if row
            else None
        )

    def find_all(
        self,
        partition_key,
    ) -> Iterable[PredictionResult]:

        instrument_id, source_id = partition_key

        rows = self._fetch_all(
            self._select_all,
            [
                instrument_id,
                source_id,
            ],
        )

        return [
            self._row_to_model(r)
            for r in rows
        ]

    @staticmethod
    def _row_to_model(
        row,
    ) -> PredictionResult:

        return PredictionResult(
            instrument_id=row.instrument_id,
            source_id=row.source_id,
            prediction_id=row.prediction_id,
            predicted_at=row.predicted_at,
            model_type=row.model_type,
            predicted_value=row.predicted_value,
            explanation=getattr(
                row,
                "explanation",
                None,
            ),
        )
