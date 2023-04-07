# -*- coding: utf-8 -*-
"""Random skill values."""
from random import normalvariate

# List of skill levels, based on Fudge. It should be good enough to translate
# to any system.
SKILLS = ["Terrible", "Poor", "Mediocre", "Fair", "Good", "Great", "Superb"]


def _normal_choice(
    lst: list[str],
) -> str:
    """Return an element from a list based on a normal distribution."""
    mean = (len(lst) - 1) / 2  # Middle of list.
    stddev = len(lst) / (len(lst) + 1)  # Should be large enough…
    while True:
        index = abs(int(normalvariate(mean, stddev) + 0.5))
        if 0 <= index < len(lst):
            return lst[index]


def get_skill_value() -> str:
    """Get a skill value."""
    return _normal_choice(SKILLS)


# List of professions.
PROFESSIONS = [
    "Agitator",
    "Alchemist",
    "Artisan",
    "Beggar",
    "Boatman",
    "Bodyguard",
    "Bounty Hunter",
    "Cleric",
    "Coachman",
    "Druid",
    "Engineer",
    "Entertainer",
    "Farmer",
    "Fighter",
    "Fisherman",
    "Gambler",
    "Gamekeeper",
    "Herbalist",
    "Herdsman",
    "Hunter",
    "Jailer",
    "Jester",
    "Labourer",
    "Marine",
    "Mercenary",
    "Militiaman",
    "Miner",
    "Minstrel",
    "Noble",
    "Outlaw",
    "Outrider",
    "Pedlar",
    "Pharmacist",
    "Physician",
    "Pilot",
    "Pit Fighter",
    "Prospector",
    "Rustler",
    "Scribe",
    "Seaman",
    "Seer",
    "Servant",
    "Shaman",
    "Smuggler",
    "Soldier",
    "Squire",
    "Student",
    "Thief",
    "Trader",
    "Trapper",
    "Watchman",
    "Wizard",
    "Woodsman",
]
