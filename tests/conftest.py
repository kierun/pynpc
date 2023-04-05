# -*- coding: utf-8 -*-
"""Configuration for pytest."""
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console


@pytest.fixture(autouse=True, scope="package")
def mock_console() -> Any:
    """Mock the console."""
    with patch("pynpc.utils.Console") as mocked:
        console = MagicMock(spec=Console)
        console.print = MagicMock()
        mocked.return_value = console
        yield console
