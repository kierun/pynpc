# -*- coding: utf-8 -*-
"""NPC class tests."""
from pathlib import Path
from typing import Any

import pytest

from pynpc.npc import NPC, RandomChoice


@pytest.fixture(autouse=True, scope="package")
def random() -> Any:
    return NPC()


@pytest.mark.parametrize(
    ("attr", "expected"),
    [
        ("name", True),
        ("personality", True),
        ("nature", True),
        ("demeanor", True),
        ("phobia", True),
        ("idiosyncrasy", True),
        ("skill_primary", True),
        ("skill_secondary", True),
        ("skill_hobby", True),
        ("ook", False),
    ],
)
def test_variabe_existss(random, attr, expected) -> None:
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
    ],
)
def test_print(random, item) -> None:
    assert item in str(random) is not None


def test_random_choice_file_not_found() -> None:
    sut = RandomChoice(Path("/The/Thing/That/Should/Not/Be/name.txt"))
    assert sut._lst == ["no choice"]
    assert sut.get_value() == "no choice"
