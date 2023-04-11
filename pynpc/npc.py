# -*- coding: utf-8 -*-
"""NPC class."""
from collections import namedtuple
from pathlib import Path, PosixPath
from secrets import choice
from typing import cast

import orjson
import structlog

from pynpc.skills import get_skill_value

rlog = structlog.get_logger("pynpc.npoc")

Skill = namedtuple("Skill", ["name", "rank"])
Phobia = namedtuple("Phobia", ["name", "rank"])

# We know they are bullshit. However, they make a good starting
# ponit to give some NPC some direction as to what they do.
#
# https://www.truity.com/page/16-personality-types-myers-briggs
# https://en.wikipedia.org/wiki/Myers%E2%80%93Briggs_Type_Indicator
MYERS_BRIGGS = [
    "[INFP] Healer",
    "[INTJ] Mastermind",
    "[INFJ] Councelor",
    "[INTP] Architect",
    "[ENFP] Champion",
    "[ENTJ] Commander",
    "[ENTP] Visionary",
    "[ENFJ] Teacher",
    "[ISFJ] Protector",
    "[ISFP] Composer",
    "[ISTJ] Inspector",
    "[ISTP] Carftperson",
    "[ESFJ] Provider",
    "[ESFP] Performer",
    "[ESTJ] Supervisor",
    "[ESTP] Dynamo",
]


PHOBIA_RANKS = (
    ["Negligable"] * 16
    + ["low"] * 8
    + ["mild"] * 4
    + ["severe"] * 2
    + ["debilitating"]
)


def get_severity() -> str:
    """Get phobia severity."""
    return choice(PHOBIA_RANKS)


class NPC:
    """Main NPC class."""

    def __init__(self, what: str = "fantasy") -> None:
        """Initialise the class.

        The option `what` is special. It defines which files are used for the
        random values to chose form. The patter is the same for all.

        """
        # Meta data.
        rlog.debug(f"Creating {what} NPC")
        self._data_dir = Path(Path(__file__).resolve().parent, "data")
        self._jobs = RandomChoice(
            Path(self._data_dir, f"{what}-professions.txt")
        )
        self._personalities = RandomChoice(source=MYERS_BRIGGS)
        self._phobias = RandomChoice(Path(self._data_dir, "phobia.txt"))
        self._idiosyncrasies = RandomChoice(
            Path(self._data_dir, "idiosyncrasies.txt")
        )
        self._archetypes = RandomChoice(Path(self._data_dir, "archetypes.txt"))
        self._cards = orjson.loads(
            Path(self._data_dir, "cards.json").read_text()
        )["cards"]
        # Generates the first one.
        self.generate()

    def reading(self) -> str:
        """Return either upwards or revesed tarot cards draw."""
        x = choice(range(0, 78))
        if choice((0, 1)):
            return f"{self._cards[x]['name']} - {self._cards[x]['meaning_up']}"
        return f"{self._cards[x]['name']} - {self._cards[x]['meaning_rev']}"

    def generate(self) -> None:
        """Generate an NPC."""
        self.name = "Random"
        self.nature = self._archetypes.get_value()
        self.demeanor = self._archetypes.get_value()
        self.personality = self._personalities.get_value()
        self.idiosyncrasy = self._idiosyncrasies.get_value()
        self.skill_primary = Skill(self._jobs.get_value(), get_skill_value())
        self.skill_secondary = Skill(self._jobs.get_value(), get_skill_value())
        self.skill_hobby = Skill(self._jobs.get_value(), get_skill_value())
        self.phobia = Phobia(self._phobias.get_value(), get_severity())
        self.reading_major = self.reading()
        self.reading_minor = self.reading()

    def __repr__(self) -> str:
        """Pretty print for class.

        This is the simple console printing. Nothing fancy.
        """
        skills = (
            f"Name: {self.name}\n"
            f"Skills:\n"
            f"   Primary:   {self.skill_primary}\n"
            f"   Secondary: {self.skill_secondary}\n"
            f"   Hobby:     {self.skill_hobby}\n"
            f"Personality: {self.personality}\n"
            f"Nature: {self.nature}\n"
            f"Demeanor: {self.demeanor}\n"
            f"Idiosyncrasy: {self.idiosyncrasy}\n"
            f"Phobia: {self.phobia}\n"
            f"Life events:\n"
            f"  Major: {self.reading_major}\n"
            f"  Minor: {self.reading_minor}\n"
        )
        data = f"{skills}"
        return f"NPC({data})"


class RandomChoice:
    """Models a list of things and can get a random item from it.

    All items in the list have the same weight. A cheap hack is to add the
    same option multiple times to get a higher probability of being chosen.
    """

    def __init__(self, source: list[str] | Path) -> None:
        """Initialise class.

        The `source` can be a file (aka Path) or a list of strings.
        """
        self._lst = []
        if type(source) is PosixPath:
            src = cast(Path, source)
            if src.is_file():
                with Path.open(source) as f:
                    self._lst = f.read().splitlines()
            else:
                rlog.warning(f"There is no such file: {source}")
                self._lst = ["no choice"]
            rlog.debug(f"Choice from {source} created")
        else:
            self._lst = cast(list[str], source)

    def get_value(self) -> str:
        """Return a random value from the list."""
        return choice(self._lst)
