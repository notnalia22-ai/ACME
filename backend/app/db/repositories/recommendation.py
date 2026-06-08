from typing import Iterable
from uuid import UUID

from app.db.repositories.base import (
    CassandraRepository,
    WarehouseRepository,
)
from app.models.recommendation import Recommendation


class RecommendationRepository(
    CassandraRepository,
    WarehouseRepository[Recommendation, UUID],
):

    def __init__(self, session):
        super().__init__(session)

        self._insert = session.prepare(
            """
            INSERT INTO recommendations
              (
                instrument_id,
                generated_at,
                recommendation_id,
                action,
                confidence,
                explanation,
                signal_id
              )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
        )

        self._select_latest = session.prepare(
            """
            SELECT *
            FROM recommendations
            WHERE instrument_id = ?
            LIMIT 1
            """
        )

        self._select_all = session.prepare(
            """
            SELECT *
            FROM recommendations
            WHERE instrument_id = ?
            """
        )

    def save(
        self,
        entity: Recommendation,
    ) -> Recommendation:

        self._execute(
            self._insert,
            [
                entity.instrument_id,
                entity.generated_at,
                entity.recommendation_id,
                entity.action,
                entity.confidence,
                entity.explanation,
                entity.signal_id,
            ],
        )

        return entity

    def delete(
        self,
        key: UUID,
    ) -> None:
        pass

    def delete_all(
        self,
        partition_key: UUID,
    ) -> None:
        pass

    def find_latest(
        self,
        partition_key: UUID,
    ) -> Recommendation | None:

        row = self._fetch_one(
            self._select_latest,
            [partition_key],
        )

        return (
            self._row_to_model(row)
            if row
            else None
        )

    def find_all(
        self,
        partition_key: UUID,
    ) -> Iterable[Recommendation]:

        rows = self._fetch_all(
            self._select_all,
            [partition_key],
        )

        return [
            self._row_to_model(r)
            for r in rows
        ]

    @staticmethod
    def _row_to_model(
        row,
    ) -> Recommendation:

        return Recommendation(
            instrument_id=row.instrument_id,
            generated_at=row.generated_at,
            recommendation_id=row.recommendation_id,
            action=row.action,
            confidence=row.confidence,
            explanation=getattr(
                row,
                "explanation",
                None,
            ),
            signal_id=getattr(
                row,
                "signal_id",
                None,
            ),
        )
