from fastapi import FastAPI

from app.api import (
    instruments,
    time_series,
    analytics,
    ingestion,
    risk,
    recommendations,
    ml,
    data_sources,
    chat,
)

app = FastAPI(
    title="ACME Ltd. Data Warehouse",
    description="Financial data warehouse API for ACME Ltd.",
    version="1.0.0",
)

# Health check


@app.get("/health")
def health():
    return {"status": "ok"}


# Register API routers
app.include_router(
    instruments.router,
    prefix="/instruments",
    tags=["Instruments"],
)

app.include_router(
    time_series.router,
    prefix="/timeseries",
    tags=["Time Series"],
)

app.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Analytics"],
)

app.include_router(
    ingestion.router,
    prefix="/ingestion",
    tags=["Ingestion"],
)

app.include_router(
    risk.router,
    prefix="/risk",
    tags=["Risk"],
)

app.include_router(
    recommendations.router,
    prefix="/recommendations",
    tags=["Recommendations"],
)

app.include_router(
    ml.router,
    prefix="/ml",
    tags=["Machine Learning"],
)

app.include_router(
    data_sources.router,
    prefix="/sources",
    tags=["Sources"],
)

app.include_router(
    chat.router,
    prefix="/chat",
    tags=["Assistant"],
)
