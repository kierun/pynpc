# -*- coding: utf-8 -*-
"""Name corruptor."""
from itertools import pairwise


def parse_patterns(sequences: list[list[str]]) -> list[str]:
    """Parse patterns."""
    results = []  # type: ignore[var-annotated]
    for seq in sequences:
        results.extend(pairwise(seq))
    return results


class NameCorruptor:
    """Name corruptor class."""

    def __init__(self, patterns: list[str]) -> None:
        """Initialize."""
        self.patterns = patterns
        self.cursor = len(patterns)

    def corrupt(self, name: str, size: int = 3) -> list[str]:
        """Corrupts a name."""
        names = []
        start = self.cursor
        for _ in range(size):
            starting_cursor = start
            cursor = (starting_cursor + 1) % len(self.patterns)
            while True:
                (pattern, replacement) = self.patterns[cursor]  # type: ignore[misc]
                new_name = name.replace(pattern, replacement)  # type: ignore[has-type]
                if new_name != name:
                    start = cursor
                    names.append(new_name)
                    name = new_name
                    break
                cursor = (cursor + 1) % len(self.patterns)
                if cursor == (starting_cursor - 1):
                    break
            names.append(name)
        return sorted(set(names))


if __name__ == "__main__":  # pragma: no cover
    """This is test code.

    As in, that's what we used to see if we were happy with the
    corruption. It's super academic!
    """
    from pathlib import Path

    import orjson
    from rich import print as lpr

    data = Path(Path(__file__).resolve().parent.parent, "pynpc", "data", "name-corruption-pattern.json")
    patterns = parse_patterns(orjson.loads(data.read_text()))
    x = NameCorruptor(patterns)

    names = (
        "agatha",
        "aldwin",
        "althea",
        "anselm",
        "armin",
        "bartholomew",
        "berengar",
        "clarice",
        "constance",
        "dierk",
        "eadric",
        "edward",
        "eldrida",
        "elfric",
        "erna",
        "eustace",
        "felicity",
        "finnegan",
        "giselle",
        "gerald",
        "godric",
        "gunther",
        "hadrian",
        "heloise",
        "isolde",
        "ivor",
        "jocelyn",
        "lancelot",
        "lysandra",
        "magnus",
        "melisande",
        "merrick",
        "osborn",
        "philomena",
        "reginald",
        "rowena",
        "sabine",
        "seraphina",
        "sigfrid",
        "tiberius",
        "ulf",
        "urien",
        "vespera",
        "wendel",
        "wilfred",
        "winifred",
        "xenia",
        "ysabel",
        "zephyr",
        "zinnia",
        "zuriel",
        "zygmund",
    )
    for name in names:
        lpr(f'("{name}", "{" ".join(x.corrupt(name, 4))}"),')
