from unittest.mock import MagicMock

from app.ingestion.pipeline import IngestionPipeline


def test_ingestion_reuses_existing_instrument_and_source():

    instrument_repo = MagicMock()
    source_repo = MagicMock()
    ts_repo = MagicMock()
    log_repo = MagicMock()
    extractor = MagicMock()

    existing_instrument = MagicMock()
    existing_instrument.instrument_id = "existing-instrument-id"

    existing_source = MagicMock()
    existing_source.source_id = "existing-source-id"

    instrument_repo.find_by_symbol.return_value = (
        existing_instrument
    )

    source_repo.find_by_name.return_value = (
        existing_source
    )

    extractor.fetch_table_data.return_value = []

    pipeline = IngestionPipeline(
        instrument_repo,
        source_repo,
        ts_repo,
        log_repo,
        extractor,
    )

    instrument = MagicMock()
    instrument.symbol = "AAPL"
    instrument.model_copy.return_value = instrument

    source = MagicMock()
    source.source_name = "ALPHAVANTAGE"
    source.model_copy.return_value = source

    pipeline.ingest(
        instrument,
        source,
        "TEST_TABLE",
    )

    instrument_repo.save.assert_not_called()
    source_repo.save.assert_not_called()
