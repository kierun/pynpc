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

    def corrupt_once(self, name: str) -> str:
        """Corrupts a name."""
        starting_cursor = self.cursor
        cursor = (starting_cursor + 1) % len(self.patterns)
        while cursor != starting_cursor:
            # grab a pattern like ("d", "t")
            (pattern, replacement) = self.patterns[cursor]  # type: ignore[misc]

            # replace it - eg "david".replace("d", "t") => "tavit"
            new_name = name.replace(pattern, replacement)  # type: ignore[has-type]
            if new_name != name:
                # if the name changed, we're done
                self.cursor = cursor
                # todo -- put 'relax' back in
                return new_name

            # if not, keep going with the next pattern
            cursor = (cursor + 1) % len(self.patterns)

        # if we get here, we didn't find any patterns that worked
        return name
