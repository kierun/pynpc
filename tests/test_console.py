# -*- coding: utf-8 -*-
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from pynpc import __version__
from pynpc.console import app
from pynpc.utils import VersionCheck


def test_help():
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert "Generate simple NPCs for table top role playing games" in result.output


def test_version():
    runner = CliRunner()
    result = runner.invoke(app, ["--version"])
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
@patch("pynpc.console._do_stuff")
def test_pynpc_version_status(m_stuff, ask, check):
    with patch("pynpc.console.check_if_latest_version") as mock_check, patch("pynpc.console.Confirm.ask") as mock_ask:
        mock_ask.return_value = ask
        m_stuff.return_value = None
        mock_check.return_value = check
        runner = CliRunner()
        result = runner.invoke(app, ["--verbose"])
        assert result is not None


def test_wrong_output():
    runner = CliRunner()
    result = runner.invoke(app, ["ko1ni2IP3pu/L>uugh[aexooJ6nu+mu#ukeic"])
    assert result.exit_code == 2
    assert "Invalid output" in result.output


def test_wrong_log_level():
    runner = CliRunner()
    result = runner.invoke(app, ["--log-level=ko1ni2IP3pu/L>uugh[aexooJ6nu+mu#ukeic"])
    assert result.exit_code == 2
    assert "Invalid value" in result.output
    assert "--log-level" in result.output


def test_wrong_localisation():
    runner = CliRunner()
    result = runner.invoke(app, ["--localisation=fred,bob,jack"])
    assert result.exit_code == 2
    assert "Invalid value " in result.output
    assert "--localisation" in result.output
