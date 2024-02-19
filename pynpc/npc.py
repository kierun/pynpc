# -*- coding: utf-8 -*-
"""NPC class."""
from pathlib import Path
from secrets import choice
from typing import Any, NamedTuple

import orjson
import structlog
from mimesis import Gender, Locale, Person
from unidecode import unidecode as transliterate  # In case we want to change module that does it.

from pynpc.name_corruptor import NameCorruptor, parse_patterns
from pynpc.skills import get_skill_value

rlog = structlog.get_logger("pynpc.npoc")


class Skill(NamedTuple):
    """Model for skills: a simple name and rank."""

    name: str
    rank: str


PHOBIA_RANKS = ["Negligable"] * 16 + ["low"] * 8 + ["mild"] * 4 + ["severe"] * 2 + ["debilitating"]


class Phobia(NamedTuple):
    """Model for phobia: a name, explanation, and serverity."""

    name: str
    severity: str
    description: str


def get_severity() -> str:
    """Get phobia severity."""
    return choice(PHOBIA_RANKS)


class Trait(NamedTuple):
    """Random properties - name and description."""

    name: str
    description: str


class Personality(NamedTuple):
    """Personality - includes code."""

    name: str
    description: str
    code: str


class Reading(NamedTuple):
    """Life events: A tarot card and its meaning."""

    card: str
    meaning: str


class Idiosyncrasy(NamedTuple):
    """Idiosyncrasy model: a simple phrase."""

    idiosyncrasy: str
    description: str = ""  # This has a default value, it will be overwritten if there is a need to.


class NPC:
    """Main NPC class."""

    def __init__(self, localisation: list[str] | None = None, what: str = "fantasy") -> None:
        """Initialise the class.

        The option `what` is special. It defines which files are used for the
        random values to chose form. The patter is the same for all.
        """
        # Meta data.
        rlog.debug(f"Creating {what} NPC")
        self._localistation: list[str] = []
        if localisation is None:
            self._localistation.append(choice(Locale.values()))
        else:
            self._localistation += localisation
        rlog.debug("NPC name localisation", locals=self._localistation)
        self._setting = what
        self._data_dir = [Path(Path(__file__).resolve().parent, "data")]
        # read resource files - everything called *.res.json in the data dir
        # expecting a 'resource' string with a name in it
        # expecting a 'values' array with objects in
        # under the resource we store the whole object, so you have to
        # access the 'values' object to get the array of data
        # this is to preserve any other values at the top level
        self._resources = {}
        self._res_files = []  # type: ignore[var-annotated]
        # find our files
        for dpath in self._data_dir:
            self._res_files = Path(dpath).glob("*.res.json")  # type: ignore[assignment]

        # read them ALL
        for file in self._res_files:
            jobj = orjson.loads(Path(file).read_text())
            # note - this permits overwriting
            # so an extra dir can override core behaviour
            self._resources[jobj["resource"]] = ResourceObject(source=jobj)

        # Name corruption.
        data = Path(Path(__file__).resolve().parent.parent, "pynpc", "data", "name-corruption-pattern.json")
        patterns = parse_patterns(orjson.loads(data.read_text()))
        self._corruptor = NameCorruptor(patterns)

        # Generates the first one.
        self.generate()

    def _get_name(self, name: str, sz: int = 3) -> str:
        """Get corruptions variations from a name."""
        rlog.debug("Generating name", name=name, sz=sz)
        try:
            first, _ = name.split(" ")
        except ValueError as e:
            rlog.error("Name is not in the expected format: 'first last'", name=name, error=e)
            first = name
        return "(" + " ".join(self._corruptor.corrupt(first, sz)) + ") "

    def reading(self) -> Reading:
        """Return either upwards or revesed tarot cards draw."""
        card = self._resources["cards"].get_value()
        if choice((0, 1)):
            return Reading(card["name"], "↑ " + card["meaning_up"])
        return Reading(card["name"], "↓ " + card["meaning_rev"])

    def generate(self) -> None:
        """Generate an NPC."""
        person = Person(choice(self._localistation))
        self.name_fem = person.full_name(gender=Gender.FEMALE)
        if self.name_fem != transliterate(self.name_fem):
            self.name_fem += " —  " + transliterate(self.name_fem)
        self.name_fem += f" →  {self._get_name(transliterate(self.name_fem), 3)}"
        self.name_mal = person.full_name(gender=Gender.MALE)
        if self.name_mal != transliterate(self.name_mal):
            self.name_mal += " —  " + transliterate(self.name_mal)
        self.name_mal += f" →  {self._get_name(transliterate(self.name_mal), 3)}"
        self.name_non = person.full_name()
        if self.name_non != transliterate(self.name_non):
            self.name_non += " —  " + transliterate(self.name_non)
        self.name_non += f" →  {self._get_name(transliterate(self.name_non), 3)}"
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
            "\n"
            "Names:\n"
            f"   ♀ {self.name_fem}\n"
            f"   ♂ {self.name_mal}\n"
            f"   ⚥ {self.name_non}\n"
            f"Skills:\n"
            f"   Primary:   {self.skill_primary}\n"
            f"   Secondary: {self.skill_secondary}\n"
            f"   Hobby:     {self.skill_hobby}\n"
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
# Fame
-  f"♀ Name: {self.name_fem}\n"
-  f"♂ Name: {self.name_mal}\n"
-  f"⚥ Name: {self.name_non}\n"

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
    """Models a list of things and can get a random item from it.

    All items in the list have the same weight. A cheap hack is to add
    the same option multiple times to get a higher probability of being
    chosen.
    """

    def __init__(self, source: Any) -> None:
        """Initialise class."""
        self._values = source["values"]
        self._name = source["resource"]
        self._raw = source

    def get_values(self, count: int = 1) -> Any:
        """Return a dictionary of choices."""
        ret = {}
        for _ in range(count):
            item = choice(self._values)
            ret[item["name"]] = item
        return ret

    def get_value(self) -> Any:
        """Return a random entry."""
        return choice(self._values)

    def get_name(self) -> Any:
        """Return the name of a random choice."""
        return choice(self._values)["name"]
