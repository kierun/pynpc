# -*- coding: utf-8 -*-
"""NPC class tests."""
from typing import Any
from unittest.mock import Mock, patch

import pytest

from pynpc.npc import NPC, ResourceObject


@pytest.fixture(autouse=True, scope="package")
def random() -> Any:
    with patch("pynpc.npc.Faker") as mock_faker:
        mock_fake = Mock()
        mock_fake.name_female.return_value = "Ferro Maljinn"
        mock_fake.name_male.return_value = "Logen Ninefingers"
        mock_fake.name_nonbinary.return_value = "R2D2"
        mock_faker.return_value = mock_fake
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
    assert "fred" in random._get_name("fred")
