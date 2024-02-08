# -*- coding: utf-8 -*-
"""Utilities."""
import enum
from typing import TYPE_CHECKING

from rich.console import Console

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Sequence

from typing import Any

import requests
import structlog

from pynpc import __version__

# https://www.nordtheme.com/docs/colors-and-palettes
COLOUR_FAIL = "#bf616a"
COLOUR_INFO = "#5e81ac"
COLOUR_NOTE = "#81a1c1"
COLOUR_SUCC = "#a3be8c"
COLOUR_WARN = "#d08770"
COLOUR_GREY = "#777777"

GITHUB_URL = "https://api.github.com/repos/kierun/pynpc/releases/latest"
rlog = structlog.get_logger("pynpc.utils")


class VersionCheck(enum.Enum):
    """Version check ENUM."""

    LATEST = enum.auto()
    LAGGING = enum.auto()
    UNKNOWN = enum.auto()


def join_with_oxford_commas(obj_list: "Sequence[Any]", conjunction: str = "and") -> str:
    """Oxford commas for lists.

    Takes a list of objects and returns their string representations,
    separated by commas and with 'and' between the penultimate and final
    items
    """
    if not obj_list:
        return ""
    size = len(obj_list)
    if size == 1:
        return f"{str(obj_list[0])}"  # noqa: RUF010
    return ", ".join(str(obj) for obj in obj_list[: size - 1]) + f", {conjunction} {obj_list[size - 1]!s}"


def check_if_latest_version() -> VersionCheck:
    """Check if there is a new version published on GitHub."""
    response = requests.get(GITHUB_URL, timeout=60)  # A minute time out.
    if response.status_code == 200:
        latest_version = response.json()["tag_name"]
        if latest_version == f"v{__version__}":
            return VersionCheck.LATEST
        return VersionCheck.LAGGING
    return VersionCheck.UNKNOWN


def wprint(text: str, level: str = "") -> None:
    """Print wrapper.

    If there is no level, we just print it with whatever markup.
    """
    console = Console()
    if level == "note":
        console.print(f"   {text}", style=COLOUR_NOTE)
    elif level == "info":
        console.print(f":thumbs_up: {text}", style=COLOUR_INFO)
    elif level == "warning":
        console.print(f":warning-emoji:  {text}", style=COLOUR_WARN)
    elif level == "success":
        console.print(f":heavy_check_mark:  {text}", style=COLOUR_SUCC)
    elif level == "failure":
        console.print(f":x: {text}", style=COLOUR_FAIL)
    else:
        console.print(f"   {text}")


if __name__ == "__main__":  # pragma: no cover
    # We do not need to test any of this… It is just an example!
    # >>> python pynpc/print.py
    TEXT = (
        "[i]I Am Malenia[/i], "
        "[b]Blade Of Miquella[/b], And "
        "[i][b]I Have Never Known Defeat.[/i][/b] "
        "[black]:skull:[/black]"
    )
    wprint(f"{TEXT}")
    wprint(f"{TEXT}", "note")
    wprint(f"{TEXT}", "info")
    wprint(f"{TEXT}", "success")
    wprint(f"{TEXT}", "warning")
    wprint(f"{TEXT}", "failure")
