from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_session():
    return MagicMock()
