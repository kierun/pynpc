# -*- coding: utf-8 -*-
"""NPC class tests."""
from typing import Any
from unittest.mock import Mock, patch

import pytest

from pynpc.npc import NPC, ResourceObject


@pytest.fixture(autouse=True, scope="package")
def random() -> Any:
    with patch("pynpc.npc.Person") as mock_fake:
        mock_person = Mock()
        mock_person.full_name.side_effect = ["Ferro Maljinn", "Logen Ninefingers", "R2D2"]
        mock_fake.return_value = mock_person
        return NPC()


@pytest.mark.parametrize(
    ("attr", "expected"),
    [
        ("demeanour", True),
        ("idiosyncrasy", True),
        ("name_fem", True),
        ("name_mal", True),
        ("name_non", True),
        ("nature", True),
        ("personality", True),
        ("phobia", True),
        ("reading_major", True),
        ("reading_minor", True),
        ("skill_hobby", True),
        ("skill_primary", True),
        ("skill_secondary", True),
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


@pytest.fixture(autouse=True, scope="package")
def res() -> Any:
    elem = {
        "name": "Test",
        "description": "A test value",
    }
    source = {
        "values": [elem],
        "resource": [],
    }
    return ResourceObject(source)


def test_resource_get_name(res) -> None:
    assert res.get_name() == "Test"


def test_resource_get_values(res) -> None:
    assert res.get_values() == {
        "Test": {
            "name": "Test",
            "description": "A test value",
        },
    }


def test_get_name(random) -> None:
    assert "fred" in random._get_name("fred")  # noqa: SLF001


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0, "Rev"),
        (1, "Up"),
    ],
)
def test_reading(value, expected) -> None:
    """Test reading of the card: reverse or up.

    The oddness of the mock comes from secrets.choice() is used to pick the card from the stack
    and to chose whether we pick the reversed or up meansing. As such, we need to mock two calls.
    The first one gets the fake card. The second one gets the meaning from the card.
    """
    npc = NPC()
    with patch("pynpc.npc.choice") as mock_choice:
        mock_choice.side_effect = [{"name": "Test", "meaning_up": "Up", "meaning_rev": "Rev"}, value]
        assert npc.reading() == ("Test", expected)
