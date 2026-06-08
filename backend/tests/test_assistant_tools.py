import json
from app.assistant.tools import execute_tool
from uuid import uuid4
from app.assistant.tools import TOOL_SCHEMAS


def test_compare_assets_tool_registered():

    names = [
        tool["function"]["name"]
        for tool in TOOL_SCHEMAS
    ]

    assert "compare_assets" in names


def test_compare_assets_returns_json(mock_session):

    result = execute_tool(
        "compare_assets",
        {
            "asset1_id": str(uuid4()),
            "asset2_id": str(uuid4()),
            "source_id": str(uuid4()),
        },
        mock_session,
    )

    data = json.loads(result)

    assert isinstance(data, dict)
