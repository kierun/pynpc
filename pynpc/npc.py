# -*- coding: utf-8 -*-
"""NPC class."""
import glob
from collections import namedtuple
from pathlib import Path
from secrets import choice
from typing import Any

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

# Personality - includes code
Personality = namedtuple("Personality", ["name", "description", "code"])

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
        card = self._resources["cards"].get_value()
        if choice((0, 1)):
            return Reading(card["name"], card["meaning_up"])
        return Reading(card["name"], card["meaning_rev"])

    def generate(self) -> None:
        """Generate an NPC."""
        self.name = "Random"
        _arc = self._resources["archetypes"].get_value()
        self.nature = Trait(_arc["name"], _arc["description"])
        self.demeanour = self.nature
        _pers = self._resources["personality"].get_value()
        self.personality = Personality(_pers["name"], _pers["description"], _pers["code"])
        self.idiosyncrasy = Idiosyncrasy(self._resources["idiosyncracies"].get_name())
        self.skill_primary = Skill(self._resources[f"{self._setting}-professions"].get_name(), get_skill_value())
        self.skill_secondary = Skill(self._resources[f"{self._setting}-professions"].get_name(), get_skill_value())
        self.skill_hobby = Skill(self._resources[f"{self._setting}-professions"].get_name(), get_skill_value())
        _ph = self._resources["phobias"].get_value()
        self.phobia = Phobia(_ph["name"], get_severity(), _ph["description"])
        self.reading_major = self.reading()
        self.reading_minor = self.reading()

    def __repr__(self) -> str:
        """Pretty print for class.

        This is the simple console printing. Nothing fancy.
        """
        skills = (
            f"Name: {self.name}\n"
            f"Skills:\n"
            f"   Primary:   {self.skill_primary.name}\n"
            f"   Secondary: {self.skill_secondary.name}\n"
            f"   Hobby:     {self.skill_hobby.name}\n"
            f"Personality: {self.personality}\n"
            f"Nature: {self.nature}\n"
            f"Demeanor: {self.nature}\n"
            f"Idiosyncrasy: {self.idiosyncrasy}\n"
            f"Phobia: {self.phobia.name}\n"
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

- **{self.personality.name}** [{self.personality.code}] {self.personality.description}
- **Nature** _{self.nature.name}_, {self.nature.description}
- **Demeanor** _{self.demeanour.name}_, {self.demeanour.description}
- {self.phobia.severity} {self.phobia.name}; {self.phobia.description}
- {self.idiosyncrasy.description}

## Life events

### Major: {self.reading_major.card}

{self.reading_major.meaning}

### Minor: {self.reading_minor.card}

{self.reading_minor.meaning}
"""


class ResourceObject:
    """
    Models a list of things and can get a random item from it.

    All items in the list have the same weight. A cheap hack is to add the
    same option multiple times to get a higher probability of being chosen.
    """

    def __init__(self, source: Any) -> None:
        """Initialise class."""
        self._values = source["values"]
        self._name = source["resource"]
        self._raw = source

    def get_values(self, count: int = 1) -> Any:
        """Return a dictionary of choices."""
        ret = {}
        for _ in range(0, count):
            item = choice(self._values)
            ret[item["name"]] = item
        return ret

    def get_value(self) -> Any:
        """Return a random entry."""
        return choice(self._values)

    def get_name(self) -> str:
        """Return the name of a random choice."""
        return choice(self._values)["name"]
