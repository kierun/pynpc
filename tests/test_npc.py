# -*- coding: utf-8 -*-
"""NPC class tests."""
from typing import Any

import pytest

from pynpc.npc import NPC


@pytest.fixture(autouse=True, scope="package")
def random() -> Any:
    return NPC()


@pytest.mark.parametrize(
    ("attr", "expected"),
    [
        ("name", True),
        ("personality", True),
        ("nature", True),
        ("demeanour", True),
        ("phobia", True),
        ("idiosyncrasy", True),
        ("skill_primary", True),
        ("skill_secondary", True),
        ("skill_hobby", True),
        ("reading_major", True),
        ("reading_minor", True),
        ("ook", False),
    ],
)
def test_variabe_exists(random, attr, expected) -> None:
    assert hasattr(random, attr) is expected


@pytest.mark.parametrize(
    ("item"),
    [
        ("Name"),
        ("Personality"),
        ("Nature"),
        ("Demeanor"),
        ("Phobia"),
        ("Idiosyncrasy"),
        ("Primary"),
        ("Secondary"),
        ("Major"),
        ("Minor"),
    ],
)
def test_print(random, item) -> None:
    assert item in str(random) is not None


def test_markdown(random) -> None:
    text = random.to_markdown()
    assert "## Skills" in text
    assert "## Personality" in text
    assert "## Life events" in text
    assert "### Major" in text
    assert "### Minor" in text
