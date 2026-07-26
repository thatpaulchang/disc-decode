"""Ipsative DISC scoring.

Pure functions, no database access, so they can be unit tested directly.
See docs/spec.md "Scoring" for the rules this implements.
"""

from dataclasses import dataclass

from apps.logic.items import Style

STYLES: list[Style] = ["D", "I", "S", "C"]


@dataclass(frozen=True)
class Answer:
    most_style: Style
    least_style: Style


@dataclass(frozen=True)
class Score:
    most: dict[Style, int]
    least: dict[Style, int]
    diff: dict[Style, int]
    top_styles: set[Style]
    bottom_styles: set[Style]


def score_answers(answers: list[Answer]) -> Score:
    most = dict.fromkeys(STYLES, 0)
    least = dict.fromkeys(STYLES, 0)

    for answer in answers:
        most[answer.most_style] += 1
        least[answer.least_style] += 1

    diff = {style: most[style] - least[style] for style in STYLES}

    highest = max(diff.values())
    lowest = min(diff.values())
    top_styles = {style for style, value in diff.items() if value == highest}
    bottom_styles = {style for style, value in diff.items() if value == lowest}

    return Score(
        most=most, least=least, diff=diff, top_styles=top_styles, bottom_styles=bottom_styles
    )
