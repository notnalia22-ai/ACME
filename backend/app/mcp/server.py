from app.db.repositories.instrument import (
    InstrumentRepository,
)
from app.db.repositories.data_source import (
    DataSourceRepository,
)
from app.db.connection import get_session
from uuid import UUID
from fastmcp import FastMCP

from datetime import date
from app.db.repositories.time_series import (
    TimeSeriesRepository,
)
from app.db.repositories.analytics_result import (
    AnalyticsResultRepository,
)

from app.db.repositories.recommendation import (
    RecommendationRepository,
)

mcp = FastMCP(
    "ACME Data Warehouse"
)


@mcp.tool()
def list_data_sources(
    offset: int = 0,
    limit: int = 20,
):
    """
    List available data sources.
    """

    repo = DataSourceRepository(
        get_session()
    )

    sources = list(
        repo.find_all()
    )

    return [
        {
            "source_id": str(
                s.source_id
            ),
            "source_name": s.source_name,
            "source_type": s.source_type,
        }
        for s in sources[
            offset:
            offset + limit
        ]
    ]


@mcp.tool()
def get_data_source_details(
    source_id: str,
):
    """
    Get details for one data source.
    """

    repo = DataSourceRepository(
        get_session()
    )

    source = repo.find_latest(
        UUID(source_id)
    )

    if source is None:
        return {
            "error":
            "Source not found"
        }

    return source.model_dump(
        mode="json"
    )


@mcp.tool()
def list_assets(
    offset: int = 0,
    limit: int = 20,
):
    """
    List available financial assets.
    """

    repo = InstrumentRepository(
        get_session()
    )

    instruments = list(
        repo.find_all()
    )

    return [
        {
            "instrument_id": str(
                i.instrument_id
            ),
            "symbol": i.symbol,
            "instrument_class": (
                i.instrument_class
            ),
            "name": i.name,
            "region": i.region,
        }
        for i in instruments[
            offset:
            offset + limit
        ]
    ]


@mcp.tool()
def get_asset_details(
    asset_id: str,
):
    """
    Get details for one asset.
    """

    repo = InstrumentRepository(
        get_session()
    )

    instrument = repo.find_latest(
        UUID(asset_id)
    )

    if instrument is None:
        return {
            "error":
            "Asset not found"
        }

    return instrument.model_dump(
        mode="json"
    )


@mcp.tool()
def get_time_series_data(
    instrument_id: str,
    source_id: str,
    start_date: str,
    end_date: str,
):
    """
    Get time-series data for an asset and source.
    Dates must be YYYY-MM-DD.
    """

    repo = TimeSeriesRepository(
        get_session()
    )

    rows = repo.find_range(
        UUID(instrument_id),
        UUID(source_id),
        date.fromisoformat(start_date),
        date.fromisoformat(end_date),
    )

    return [
        {
            "record_date": str(
                r.record_date
            ),
            "open_price": (
                str(r.open_price)
                if r.open_price is not None
                else None
            ),
            "close_price": (
                str(r.close_price)
                if r.close_price is not None
                else None
            ),
            "high_price": (
                str(r.high_price)
                if r.high_price is not None
                else None
            ),
            "low_price": (
                str(r.low_price)
                if r.low_price is not None
                else None
            ),
            "adj_close": (
                str(r.adj_close)
                if r.adj_close is not None
                else None
            ),
            "volume": r.volume,
        }
        for r in rows
    ]


@mcp.tool()
def compare_assets(
    asset1_id: str,
    asset2_id: str,
    source_id: str,
):
    """
    Compare two assets using warehouse analytics
    and recommendations.
    """

    session = get_session()

    instrument_repo = InstrumentRepository(
        session
    )

    analytics_repo = AnalyticsResultRepository(
        session
    )

    recommendation_repo = RecommendationRepository(
        session
    )

    source_uuid = UUID(
        source_id
    )

    def build_asset(
        asset_id: str,
    ):
        instrument = (
            instrument_repo.find_latest(
                UUID(asset_id)
            )
        )

        if instrument is None:
            return {
                "error":
                "Asset not found"
            }

        analytics = list(
            analytics_repo.find_all(
                (
                    UUID(asset_id),
                    source_uuid,
                )
            )
        )

        trend = next(
            (
                a.notes
                for a in analytics
                if a.metric_type
                == "TREND"
            ),
            None,
        )

        volatility = next(
            (
                float(
                    a.metric_value
                )
                for a in analytics
                if a.metric_type
                == "VOLATILITY"
                and a.metric_value
                is not None
            ),
            None,
        )

        recommendation = (
            recommendation_repo
            .find_latest(
                UUID(asset_id)
            )
        )

        return {
            "symbol":
            instrument.symbol,

            "name":
            instrument.name,

            "asset_class":
            instrument.instrument_class,

            "trend":
            trend,

            "volatility":
            volatility,

            "recommendation":
            (
                recommendation.action
                if recommendation
                else None
            ),

            "confidence":
            (
                recommendation.confidence
                if recommendation
                else None
            ),
        }

    return {
        "asset_1":
        build_asset(
            asset1_id
        ),

        "asset_2":
        build_asset(
            asset2_id
        ),
    }


if __name__ == "__main__":
    mcp.run(
        transport="stdio"
    )
