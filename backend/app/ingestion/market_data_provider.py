import time
import requests
from typing import Iterator

from app.config import settings


class MarketDataProvider:

    def fetch_table_data(
        self,
        datatable_code: str,
        filters: dict | None = None,
    ) -> Iterator[dict]:

        filters = filters or {}

        symbol = filters.get("ticker")

        if not symbol:
            raise ValueError("ticker filter is required")

        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": settings.alphavantage_api_key,
            "outputsize": "compact",
        }

        response = requests.get(
            settings.alphavantage_base_url,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        # API rate limit / error handling
        if "Note" in data:
            raise RuntimeError(
                f"AlphaVantage rate limit exceeded: {data['Note']}"
            )

        if "Error Message" in data:
            raise RuntimeError(
                f"AlphaVantage error: {data['Error Message']}"
            )

        time_series = data.get("Time Series (Daily)")

        if not time_series:
            raise RuntimeError(
                f"No daily time series returned for {symbol}"
            )

        for date_str, values in time_series.items():

            yield {
                "date": date_str,
                "open": values.get("1. open"),
                "high": values.get("2. high"),
                "low": values.get("3. low"),
                "close": values.get("4. close"),
                "volume": values.get("5. volume"),
                "adj_close": None,
                "split_ratio": None,
                "ex-dividend": None,
            }
