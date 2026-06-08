from app.mcp.server import (
    list_assets,
    get_asset_details,
    list_data_sources,
    get_data_source_details,
    get_time_series_data,
)

print("\n=== ASSETS ===")
assets = list_assets(limit=3)
print(assets)

print("\n=== SOURCES ===")
sources = list_data_sources(limit=3)
print(sources)

if assets:
    asset_id = assets[0]["instrument_id"]

    print("\n=== ASSET DETAILS ===")
    print(
        get_asset_details(
            asset_id
        )
    )

if sources:
    source_id = sources[0]["source_id"]

    print("\n=== SOURCE DETAILS ===")
    print(
        get_data_source_details(
            source_id
        )
    )
