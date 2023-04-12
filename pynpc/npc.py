# -*- coding: utf-8 -*-
"""NPC class."""
from collections import namedtuple
from pathlib import Path, PosixPath
from secrets import choice
from typing import Any, cast

import glob
import orjson
import structlog

from pynpc.skills import get_skill_value

rlog = structlog.get_logger("pynpc.npoc")

# Model for skills: a simple name and rank.
Skill = namedtuple("Skill", ["name", "rank"])

# Model for phobia: a name, explanation, and serverity.
Phobia = namedtuple("Phobia", ["name", "severity", "description"])
PHOBIA_RANKS = ["Negligable"] * 16 + ["low"] * 8 + ["mild"] * 4 + ["severe"] * 2 + ["debilitating"]


def get_severity() -> str:
    """Get phobia severity."""
    return choice(PHOBIA_RANKS)


# random properties - name and description
Trait = namedtuple("Trait", ["name", "description"])

# Life events: A tarot card and its meaning.
Reading = namedtuple("Reading", ["card", "meaning"])

# Idiosyncrasy model: a simple phrase.
Idiosyncrasy = namedtuple("Idiosyncrasy", ["description"])


class NPC:
    """Main NPC class."""

    # TODO:  Accept extra data dirs as arg
    def __init__(self, what: str = "fantasy") -> None:
        """Initialise the class.

        The option `what` is special. It defines which files are used for the
        random values to chose form. The patter is the same for all.

        """
        # Meta data.
        rlog.debug(f"Creating {what} NPC")
        self._setting = what
        self._data_dir = [Path(Path(__file__).resolve().parent, "data")]
        # TODO: append extra data dirs here

        # read resource files - everything called *.res.json in the data dir
        # expecting a 'resource' string with a name in it
        # expecting a 'values' array with objects in
        # under the resource we store the whole object, so you have to
        # access the 'values' object to get the array of data
        # this is to preserve any other values at the top level
        self._resources = {}
        self._res_files = []
        # find our files
        for dpath in self._data_dir:
            self._res_files = glob.glob(f"{dpath}/*.res.json")

        # read them ALL
        for file in self._res_files:
            jobj = orjson.loads(Path(file).read_text())
            # note - this permits overwriting
            # so an extra dir can override core behaviour
            self._resources[jobj["resource"]] = ResourceObject(source=jobj)

        # Generates the first one.
        self.generate()

    def reading(self) -> Reading:
        """Return either upwards or revesed tarot cards draw."""
        card = self._resources["cards"].get_values()
        key = next(iter(card))  # This is not intuitive at all!
        if choice((0, 1)):
            return Reading(card[key], card[key]["meaning_up"])
        return Reading(card[key], card[key]["meaning_rev"])

    def generate(self) -> None:
        """Generate an NPC."""
        self.name = "Random"
        self.nature = self._resources["archetypes"].get_values()
        self.demeanour = self.nature
        self.personality = self._resources["personality"].get_values()
        self.idiosyncracy = self._resources["idiosyncracies"].get_values(count=2)
        self.skill_primary = self._resources[f"{self._setting}-professions"].get_values()
        self.skill_secondary = self._resources[f"{self._setting}-professions"].get_values()
        self.skill_hobby = self._resources[f"{self._setting}-professions"].get_values()
        self.phobia = self._resources["phobias"].get_values()
        self.reading_major = self.reading()
        self.reading_minor = self.reading()

    def __repr__(self) -> str:
        """Pretty print for class.

        This is the simple console printing. Nothing fancy.
        """
        skills = (
            f"Name: {self.name}\n"
            f"Skills:\n"
            f"   Primary:   {next(iter(self.skill_primary.values()))}\n"
            f"   Secondary: {next(iter(self.skill_secondary.values()))}\n"
            f"   Hobby:     {next(iter(self.skill_hobby.values()))}\n"
            f"Personality: {next(iter(self.personality.values()))}\n"
            f"Nature: {next(iter(self.nature.values()))}\n"
            f"Demeanor: {next(iter(self.nature.values()))}\n"
            f"Idiosyncrasy: {next(iter(self.idiosyncracy.values()))}\n"
            f"Phobia: {next(iter(self.phobia.values()))}\n"
            f"Life events:\n"
            f"  Major: {self.reading_major}\n"
            f"  Minor: {self.reading_minor}\n"
        )
        data = f"{skills}"
        return f"NPC({data})"

    def to_markdown(self) -> str:
        """Print NPC in markdown."""
        return f"""
# {self.name}

## Skills

| **Abilities** |   **Name**    | **Rank** |
| --- | --- | --- |
| **Primary**   | {self.skill_primary.name}   | {self.skill_primary.rank} |
| **Secondary** | {self.skill_secondary.name} | {self.skill_secondary.rank} |
| **Hobby**     | {self.skill_hobby.name}     | {self.skill_hobby.rank} |

## Personality

- **{self.personality.title}** [{self.personality.code}] {self.personality.description}
- **Nature** _{self.nature.name}_, {self.nature.description}
- **Demeanor** _{self.demeanor.name}_, {self.demeanor.description}
- {self.phobia.severity} {self.phobia.name}; {self.phobia.description}
- {self.idiosyncracy.description}

## Life events

### Major: {self.reading_major.card}

{self.reading_major.meaning}

### Minor: {self.reading_minor.card}

{self.reading_minor.meaning}
"""  # noqa: E501


class ResourceObject:
    """
    Models a list of things and can get a random item from it.

    All items in the list have the same weight. A cheap hack is to add the
    same option multiple times to get a higher probability of being chosen.
    """

    def __init__(self, source: Any) -> None:
        """Initialise class."""
        self.values = source["values"]
        self.name = source["resource"]
        self.raw = source

    def get_values(self, count: int = 1) -> Any:
        """Return a dictionary of choices."""
        ret = {}
        for _ in range(0, count):
            item = choice(self.values)
            ret[item["name"]] = item
        return ret
