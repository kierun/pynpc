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
            self._res_files.append(glob.glob(f"{dpath}/*.res.json"))

        # read them ALL
        for file in self._res_files:
            jobj = orjson.loads(Path(file).read_text())
            # note - this permits overwriting
            # so an extra dir can override core behaviour
            self._resources[jobj["resource"]] = jobj

        self._personalities = RandomChoice(source=self._resources["personality"])
        self._jobs = RandomChoice(source=self._resources[f"{self._setting}-professions"])
        self._phobias = RandomChoice(self._resources["phobias"])
        self._idiosyncrasies = RandomChoice(self._resources["idiosyncracies"])
        # changed the format of this to better match the other resources
        self._cards = RandomChoice(self._resources["cards"])
        # Generates the first one.
        self.generate()

    def reading(self) -> Reading:
        """Return either upwards or revesed tarot cards draw."""
        x = choice(range(0, len(self._cards["values"]))
        if choice((0, 1)):
            return Reading(
                self._cards["values"][x]["name"], self._cards[x]["meaning_up"]
            )
        return Reading(self._cards["values"][x]["name"], self._cards[x]["meaning_rev"])

    def generate(self) -> None:
        """Generate an NPC."""
        self.name = "Random"
        _gen = {}
        _gen["archetype"] = self._resources["archetypes"].get_value()
        _gen["personality"] = self._resources["personality"].get_value()
        _gen["idiosyncracies"] = self._resources["idiosyncracies"].get_value()
        _gen["profession"] = self._resources[f"{self._setting}-professions"].get_value()
        self._generated = _gen

        _tmp = self._archetypes.get_value().split(" - ")
        self.nature = Archetype(_tmp[0], _tmp[1])
        _tmp = self._archetypes.get_value().split(" - ")
        self.demeanor = Archetype(_tmp[0], _tmp[1])
        self.personality = self._personalities.get_value()
        self.idiosyncrasy = Idiosyncrasy(self._idiosyncrasies.get_value())
        self.skill_primary = Skill(self._jobs.get_value(), get_skill_value())
        self.skill_secondary = Skill(self._jobs.get_value(), get_skill_value())
        self.skill_hobby = Skill(self._jobs.get_value(), get_skill_value())
        _tmp = self._phobias.get_value().split(" - ")
        self.phobia = Phobia(_tmp[0], get_severity(), _tmp[1])
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
- {self.idiosyncrasy.description}

## Life events

### Major: {self.reading_major.card}

{self.reading_major.meaning}

### Minor: {self.reading_minor.card}

{self.reading_minor.meaning}
"""  # noqa: E501


class RandomChoice:
    """Models a list of things and can get a random item from it.

    All items in the list have the same weight. A cheap hack is to add the
    same option multiple times to get a higher probability of being chosen.
    """

    def __init__(self, source: list[Any] | Path) -> None:
        """Initialise class.

        The `source` can be a file (aka Path) or a list of strings.
        """
        self._lst = []
        if type(source) is PosixPath:
            # TODO:  get rid of this
            src = cast(Path, source)
            if src.is_file():
                with Path.open(source) as f:
                    self._lst = f.read().splitlines()
            else:
                rlog.warning(f"There is no such file: {source}")
                self._lst = ["no choice"]
            rlog.debug(f"Choice from {source} created")
        else:
            # it's an array of objects - just yoink the name for now
            self._lst = [dic['name'] for dic in source["values"]]

    def get_value(self) -> Any:
        """Return a random value from the list."""
        return choice(self._lst)
