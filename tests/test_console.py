# -*- coding: utf-8 -*-
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from pynpc import __version__
from pynpc.console import main
from pynpc.utils import VersionCheck


def test_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert (
        "Generate simple NPCs for table top role playing games"
        in result.output
    )


def test_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0, f"CLI output: {result.output}"
    assert __version__ in result.output


@pytest.mark.parametrize(
    ("ask", "check"),
    [
        (True, VersionCheck.LATEST),
        (True, VersionCheck.UNKNOWN),
        (True, VersionCheck.LAGGING),
        (False, VersionCheck.LAGGING),
    ],
)
def test_pynpc_version_status(ask, check):
    with patch("pynpc.console.check_if_latest_version") as mock_check, patch(
        "pynpc.console.Confirm.ask"
    ) as mock_ask:
        mock_ask.return_value = ask
        mock_check.return_value = check
        runner = CliRunner()
        result = runner.invoke(main, ["--verbose"])
        assert result is not None
