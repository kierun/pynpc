# -*- coding: utf-8 -*-
"""NPC class."""
from collections import namedtuple
from secrets import choice

import structlog

from pynpc.skills import PROFESSIONS, get_skill_value

rlog = structlog.get_logger("pynpc.npoc")

Skill = namedtuple("Skill", ["name", "rank"])


class NPC:
    """Main NPC class."""

    def __init__(self) -> None:
        """Initialise the class."""
        self._jobs = RandomChoice(PROFESSIONS)
        self.skill_primary = Skill(self._jobs.get_value(), get_skill_value())
        self.skill_secondary = Skill(self._jobs.get_value(), get_skill_value())
        self.skill_hobby = Skill(self._jobs.get_value(), get_skill_value())
        rlog.debug("Create NPC")

    def __repr__(self) -> str:
        """Pretty print for class.

        This is the simple console printing. Nothing fancy.
        """
        skills = (
            f"Skills:\n"
            f"   Primary:   {self.skill_primary}\n"
            f"   Secondary: {self.skill_secondary}\n"
            f"   Hobby:     {self.skill_hobby}\n"
        )
        data = f"{skills}"
        return f"NPC({data})"


class RandomChoice:
    """Models a list of things and can get a random item from it."""

    def __init__(self, lst: list[str] | None = None) -> None:
        """Initialise class."""
        if lst is None:
            # This should load from file or something.
            lst = ["BAD"]
        self._list = lst
        rlog.debug("Choice created")

    def get_value(self) -> str:
        """Return a random value from the list."""
        return choice(self._list)
