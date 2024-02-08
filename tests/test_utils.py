# -*- coding: utf-8 -*-
"""Utilities."""
from pathlib import Path

import pytest
import requests_mock

from pynpc import __version__
from pynpc.utils import GITHUB_URL, VersionCheck, check_if_latest_version, join_with_oxford_commas, wprint

TXT = "I Am Malenia, Blade Of Miquella, And I Have Never Known Defeat."
TXT_FMT = (
    "[i]I Am Malenia[/i], "
    "[b][red]Blade Of Miquella[/red][/b], And "
    "[i][b]I Have [blue]Never[/blue] Known Defeat.[/i][/b]"
    ":skull:"
)


@pytest.mark.parametrize(
    ("items", "text"),
    [
        (None, ""),
        (("",), ""),
        (("apples",), "apples"),
        (("apples", "oranges"), "apples, and oranges"),
        (("apples", "oranges", "pears"), "apples, oranges, and pears"),
        ("abc", "a, b, and c"),
        ((1, 2, 3), "1, 2, and 3"),
        (
            (
                Path(),
                Path(),
                Path(),
            ),
            "., ., and .",
        ),
    ],
)
def test_join_with_oxford_commas(items: tuple, text: str) -> None:
    assert join_with_oxford_commas(items) == text


def test_join_with_oxford_commas_conjunction() -> None:
    assert join_with_oxford_commas((1, 2, 3), conjunction="or") == "1, 2, or 3"


@pytest.mark.parametrize(
    ("payload", "status", "expected"),
    [
        ({}, 500, VersionCheck.UNKNOWN),
        ({}, 404, VersionCheck.UNKNOWN),
        ({"tag_name": "v0.0.0"}, 200, VersionCheck.LAGGING),
        ({"tag_name": f"v{__version__}"}, 200, VersionCheck.LATEST),
    ],
)
def test_check_if_latest_version(payload: dict, status: int, expected: VersionCheck) -> None:
    with requests_mock.Mocker() as mocked:
        mocked.get(GITHUB_URL, json=payload, status_code=status)
        assert check_if_latest_version() == expected


@pytest.mark.parametrize(
    ("level", "extra", "text"),
    [
        (None, None, TXT),
        ("note", None, TXT),
        ("info", ":thumbs_up:", TXT),
        ("warning", ":warning-emoji:", TXT),
        ("success", ":heavy_check_mark:", TXT),
        ("failure", ":x:", TXT),
        (None, None, TXT_FMT),
        ("note", None, TXT_FMT),
        ("info", ":thumbs_up:", TXT_FMT),
        ("warning", ":warning-emoji:", TXT_FMT),
        ("success", ":heavy_check_mark:", TXT_FMT),
        ("failure", ":x:", TXT_FMT),
    ],
)
def test_wprint(level, extra, text, mock_console):
    wprint(text, level)
    assert mock_console.print.called
    assert text in mock_console.print.call_args.args[0]
    if extra is not None:
        assert extra in mock_console.print.call_args.args[0]
