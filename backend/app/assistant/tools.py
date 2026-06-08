import json
from datetime import date
from uuid import UUID

from app.db.repositories.instrument import InstrumentRepository
from app.db.repositories.data_source import DataSourceRepository
from app.db.repositories.time_series import TimeSeriesRepository
from app.analytics.aggregations import compute_aggregations
from app.db.repositories.analytics_result import (
    AnalyticsResultRepository,
)

from app.db.repositories.recommendation import (
    RecommendationRepository,
)

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "list_instruments",
            "description": "Use this when the user asks what assets are available, wants to browse stocks, list instruments, see available securities, or identify asset IDs before performing another operation.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_instrument",
            "description": "Use this when the user asks for details about a specific asset, stock, or instrument. Returns metadata such as symbol, name, region, and currency.",
            "parameters": {
                "type": "object",
                "properties": {
                    "instrument_id": {
                        "type": "string",
                        "description": "UUID of the instrument",
                    }
                },
                "required": ["instrument_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_sources",
            "description": "Use this when the user asks which data providers are available, what sources exist in the warehouse, or wants to identify source IDs before retrieving data.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_time_series",
            "description": "Use this when the user asks for historical prices, market history, price movements, OHLCV data, trading activity, or performance over a specific date range.",
            "parameters": {
                "type": "object",
                "properties": {
                    "instrument_id": {
                        "type": "string",
                        "description": "UUID of the instrument",
                    },
                    "source_id": {
                        "type": "string",
                        "description": "UUID of the data source",
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format",
                    },
                },
                "required": ["instrument_id", "source_id", "start_date", "end_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_analytics",
            "description": "Use this when the user asks for summaries, statistics, trends, averages, minimums, maximums, trading volume, or performance metrics over a date range instead of raw time-series data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "instrument_id": {
                        "type": "string",
                        "description": "UUID of the instrument",
                    },
                    "source_id": {
                        "type": "string",
                        "description": "UUID of the data source",
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format",
                    },
                },
                "required": ["instrument_id", "source_id", "start_date", "end_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_assets",
            "description": "Use this when the user asks to compare two assets, stocks, or securities. Returns trends, volatility, recommendations, confidence levels, and key analytics for both assets.",
            "parameters": {
                "type": "object",
                "properties": {
                    "asset1_id": {
                        "type": "string",
                        "description": "UUID of the first asset"
                    },
                    "asset2_id": {
                        "type": "string",
                        "description": "UUID of the second asset"
                    },
                    "source_id": {
                        "type": "string",
                        "description": "UUID of the data source"
                    }
                },
                "required": [
                    "asset1_id",
                    "asset2_id",
                    "source_id"
                ]
            }
        }
    }
]


def execute_tool(name: str, args: dict, session) -> str:
    """Execute a named tool with the given args. Returns a JSON string result."""
    try:
        if name == "list_instruments":
            repo = InstrumentRepository(session)
            instruments = list(repo.find_all())
            return json.dumps([
                {
                    "instrument_id": str(i.instrument_id),
                    "symbol": i.symbol,
                    "name": i.name,
                    "class": i.instrument_class,
                    "region": i.region,
                }
                for i in instruments
            ])

        elif name == "get_instrument":
            repo = InstrumentRepository(session)
            instrument = repo.find_latest(UUID(args["instrument_id"]))
            if instrument is None:
                return json.dumps({"error": "Instrument not found"})
            return json.dumps({
                "instrument_id": str(instrument.instrument_id),
                "symbol": instrument.symbol,
                "name": instrument.name,
                "class": instrument.instrument_class,
                "region": instrument.region,
                "currency": instrument.currency,
            })

        elif name == "list_sources":
            repo = DataSourceRepository(session)
            sources = list(repo.find_all())
            return json.dumps([
                {
                    "source_id": str(s.source_id),
                    "name": s.source_name,
                    "type": s.source_type,
                }
                for s in sources
            ])

        elif name == "get_time_series":
            repo = TimeSeriesRepository(session)
            # The date inputs are validated here so the repositories stay query-focused.
            points = repo.find_range(
                UUID(args["instrument_id"]),
                UUID(args["source_id"]),
                date.fromisoformat(args["start_date"]),
                date.fromisoformat(args["end_date"]),
            )
            return json.dumps([
                {
                    "date": str(p.record_date),
                    "open": str(p.open_price) if p.open_price is not None else None,
                    "close": str(p.close_price) if p.close_price is not None else None,
                    "high": str(p.high_price) if p.high_price is not None else None,
                    "low": str(p.low_price) if p.low_price is not None else None,
                    "volume": p.volume,
                }
                for p in points
            ])

        elif name == "get_analytics":
            # Reuse the time-series repository and compute aggregates in-process.
            repo = TimeSeriesRepository(session)
            points = repo.find_range(
                UUID(args["instrument_id"]),
                UUID(args["source_id"]),
                date.fromisoformat(args["start_date"]),
                date.fromisoformat(args["end_date"]),
            )
            agg = compute_aggregations(points)
            return json.dumps({
                "count": agg.count,
                "min_close": str(agg.min_close) if agg.min_close is not None else None,
                "max_close": str(agg.max_close) if agg.max_close is not None else None,
                "avg_close": str(agg.avg_close) if agg.avg_close is not None else None,
                "total_volume": agg.total_volume,
            })

        elif name == "compare_assets":

            instrument_repo = InstrumentRepository(session)
            analytics_repo = AnalyticsResultRepository(session)
            recommendation_repo = RecommendationRepository(session)

            source_id = UUID(args["source_id"])
            asset1_id = UUID(args["asset1_id"])
            asset2_id = UUID(args["asset2_id"])

            assets = []

            for asset_id in [asset1_id, asset2_id]:

                instrument = instrument_repo.find_latest(asset_id)

                if instrument is None:
                    assets.append({"error": "Asset not found"})
                    continue

                analytics = list(
                    analytics_repo.find_all(
                        (asset_id, source_id)
                    )
                )

                trend = next(
                    (
                        a.notes
                        for a in analytics
                        if a.metric_type == "TREND"
                    ),
                    None,
                )

                volatility = next(
                    (
                        float(a.metric_value)
                        for a in analytics
                        if a.metric_type == "VOLATILITY"
                        and a.metric_value is not None
                    ),
                    None,
                )

                recommendation = recommendation_repo.find_latest(asset_id)

                assets.append({
                    "symbol": instrument.symbol,
                    "name": instrument.name,
                    "asset_class": instrument.instrument_class,
                    "trend": trend,
                    "volatility": volatility,
                    "recommendation": (
                        recommendation.action
                        if recommendation
                        else None
                    ),
                    "confidence": (
                        recommendation.confidence
                        if recommendation
                        else None
                    ),
                })

            return json.dumps({
                "asset_1": assets[0],
                "asset_2": assets[1],
            })

        else:
            return json.dumps({"error": f"Unknown tool: {name}"})

    except Exception as e:
        return json.dumps({"error": str(e)})
