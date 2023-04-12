# -*- coding: utf-8 -*-
"""NPC class."""
from collections import namedtuple
from pathlib import Path, PosixPath
from secrets import choice
from typing import Any, cast

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


# Personality types.
#
# We know they are bullshit. However, they make a good starting
# ponit to give some NPC some direction as to what they do.
#
# https://www.truity.com/page/16-personality-types-myers-briggs
# https://en.wikipedia.org/wiki/Myers%E2%80%93Briggs_Type_Indicator
# https://www.verywellmind.com/the-myers-briggs-type-indicator-2795583
Persona = namedtuple("Persona", ["code", "title", "description"])
MYERS_BRIGGS = [
    Persona(
        "ISTJ",
        "Inspector",
        "Reserved and practical, they tend to be loyal, orderly, and traditional.",  # noqa: E501
    ),
    Persona(
        "ISTP",
        "Crafter",
        "Highly independent, they enjoy new experiences that provide first-hand learning.",  # noqa: E501
    ),
    Persona(
        "ISFJ",
        "Protector",
        "Warm-hearted and dedicated, they are always ready to protect the people they care about.",  # noqa: E501
    ),
    Persona(
        "ISFP",
        "Artist",
        "Easy-going and flexible, they tend to be reserved and artistic.",
    ),
    Persona(
        "INFJ",
        "Advocate",
        "Creative and analytical, they are one of the rarest types.",
    ),
    Persona(
        "INFP",
        "Mediator",
        "Idealistic with high values, they strive to make the world a better place.",  # noqa: E501
    ),
    Persona(
        "INTJ",
        "Architect",
        "High logical, they are both very creative and analytical.",
    ),
    Persona(
        "INTP",
        "Thinker",
        "Quiet and introverted, they are known for having a rich inner world.",
    ),
    Persona(
        "ESTP",
        "Persuader",
        "Out-going and dramatic, they enjoy spending time with others and focusing on the here-and-now.",  # noqa: E501
    ),
    Persona(
        "ESTJ",
        "Director",
        "Assertive and rule-oriented, they have high principles and a tendency to take charge.",  # noqa: E501
    ),
    Persona(
        "ESFP",
        "Performer",
        "Outgoing and spontaneous, they enjoy taking center stage.",
    ),
    Persona(
        "ESFJ",
        "Caregiver",
        "Soft-hearted and outgoing, they tend to believe the best about other people.",  # noqa: E501
    ),
    Persona(
        "ENFP",
        "Champion",
        "Charismatic and energetic, they enjoy situations where they can put their creativity to work. ",  # noqa: E501
    ),
    Persona(
        "ENFJ",
        "Giver",
        "Loyal and sensitive, they are known for being understanding and generous.",  # noqa: E501
    ),
    Persona(
        "ENTP",
        "Debater",
        "Highly inventive, they love being surrounded by ideas and tend to start many projects, but may struggle to finish them.",  # noqa: E501
    ),
    Persona(
        "ENTJ",
        "Commander",
        "Outspoken and confident, they are great at making plans and organizing projects.",  # noqa: E501
    ),
]


# Life events: A tarot card and its meaning.
Reading = namedtuple("Reading", ["card", "meaning"])

# Archetypes model: name and description
Archetype = namedtuple("Archetype", ["name", "description"])

# Idiosyncrasy model: a simple phrase.
Idiosyncrasy = namedtuple("Idiosyncrasy", ["description"])


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

    def reading(self) -> Reading:
        """Return either upwards or revesed tarot cards draw."""
        x = choice(range(0, 78))
        if choice((0, 1)):
            return Reading(
                self._cards[x]["name"], self._cards[x]["meaning_up"]
            )
        return Reading(self._cards[x]["name"], self._cards[x]["meaning_rev"])

    def generate(self) -> None:
        """Generate an NPC."""
        self.name = "Random"
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

    def get_value(self) -> Any:
        """Return a random value from the list."""
        return choice(self._lst)
