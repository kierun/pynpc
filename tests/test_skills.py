# -*- coding: utf-8 -*-
"""Test random skill values."""
from unittest.mock import patch

import pytest

from pynpc.skills import get_skill_value


@pytest.mark.parametrize(
    ("rand", "skill"),
    [
        (0, "Terrible"),
        (1, "Poor"),
        (2, "Mediocre"),
        (3, "Fair"),
        (4, "Good"),
        (5, "Great"),
        (6, "Superb"),
    ],
)
def test_normal_choice(rand, skill) -> None:
    with patch("pynpc.skills.normalvariate") as norm:
        norm.return_value = rand
        assert get_skill_value() == skill


def test_normal_choice_boundary() -> None:
    with patch("pynpc.skills.normalvariate") as norm:
        norm.side_effect = [1000, -1000, 0]
        assert get_skill_value() == "Terrible"
