"""Questionnaire content for the DISC questionnaire.

All statements here are ORIGINAL to this project. They are not copied,
adapted, or paraphrased from any commercial DISC instrument. The DISC model
itself (Marston, 1928) is public domain; the item wording of published
instruments is not. Do not replace these with items from anywhere else.

Design notes, so future edits don't quietly break the instrument:

* Each tetrad contains exactly one statement per style: D, I, S, and C.
* Statements within a tetrad are written to be roughly equal in social
  desirability. This matters: if one option reads as obviously "better,"
  nearly everyone picks it and that tetrad stops discriminating.
* Display order is varied and baked in, so no respondent sees D-I-S-C
  repeating down the page. It is deliberately static rather than shuffled at
  runtime, so a page refresh never reorders the options under someone.
* Statements are first-person, present tense, and behavioral -- what someone
  does, not what they are.
"""

from typing import Literal

Style = Literal["D", "I", "S", "C"]

STYLE_NAMES: dict[Style, str] = {
    "D": "Dominance",
    "I": "Influence",
    "S": "Steadiness",
    "C": "Conscientiousness",
}

# Each tetrad is a list of (style, statement) pairs in display order.
TETRADS: list[list[tuple[Style, str]]] = [
    [
        ("D", "I make the call and move on."),
        ("S", "I make sure everyone is on board first."),
        ("C", "I want the details right before deciding."),
        ("I", "I get people excited about the idea."),
    ],
    [
        ("C", "I check the facts before I speak."),
        ("I", "I talk my way through problems."),
        ("D", "I push hard when I want something."),
        ("S", "I wait for the right moment."),
    ],
    [
        ("S", "I like knowing what to expect."),
        ("D", "I like being in charge."),
        ("I", "I like being around people."),
        ("C", "I like getting it exactly right."),
    ],
    [
        ("I", "I would rather keep things upbeat."),
        ("C", "I would rather be precise than quick."),
        ("D", "I say what I think, plainly."),
        ("S", "I would rather not make waves."),
    ],
    [
        ("D", "I take risks to get results."),
        ("C", "I test it before I trust it."),
        ("S", "I stick with what is working."),
        ("I", "I trust my read on people."),
    ],
    [
        ("S", "Sudden changes unsettle me."),
        ("I", "Silence in a room bothers me."),
        ("C", "Sloppy work bothers me."),
        ("D", "Slow decisions frustrate me."),
    ],
    [
        ("C", "I keep things accurate."),
        ("D", "I set the pace."),
        ("S", "I keep things steady."),
        ("I", "I lift the mood."),
    ],
    [
        ("I", "I would rather talk it out than write it down."),
        ("S", "I would rather help than compete."),
        ("D", "I would rather lead than follow."),
        ("C", "I would rather plan than improvise."),
    ],
    [
        ("S", "I focus on the team holding together."),
        ("C", "I focus on doing it properly."),
        ("I", "I focus on the people."),
        ("D", "I focus on the outcome."),
    ],
    [
        ("D", "I make decisions quickly."),
        ("S", "I take my time warming up to people."),
        ("I", "I make friends quickly."),
        ("C", "I take my time analyzing."),
    ],
    [
        ("C", "I examine an idea for holes."),
        ("I", "I sell an idea to the room."),
        ("D", "I challenge an idea in the room."),
        ("S", "I support the idea the room lands on."),
    ],
    [
        ("I", "I like an audience."),
        ("D", "I like a challenge."),
        ("C", "I like a clear standard."),
        ("S", "I like a routine."),
    ],
    [
        ("S", "I get uncomfortable with conflict."),
        ("C", "I get uneasy when things are vague."),
        ("D", "I get impatient with long discussions."),
        ("I", "I get restless doing detailed work alone."),
    ],
    [
        ("D", "I take responsibility when nobody else will."),
        ("C", "I find the error nobody else caught."),
        ("I", "I break the tension with a joke."),
        ("S", "I stay late to help a colleague."),
    ],
    [
        ("I", "I want to be liked."),
        ("S", "I want things to be calm."),
        ("D", "I want to win."),
        ("C", "I want things to be correct."),
    ],
    [
        ("C", "I would describe myself as careful."),
        ("D", "I would describe myself as direct."),
        ("S", "I would describe myself as patient."),
        ("I", "I would describe myself as outgoing."),
    ],
    [
        ("S", "I let it go to keep the peace."),
        ("D", "I push back when I disagree."),
        ("C", "I lay out the evidence for my position."),
        ("I", "I keep talking until we find common ground."),
    ],
    [
        ("D", "I would rather act than wait."),
        ("S", "I would rather finish what we started."),
        ("I", "I would rather include people than decide alone."),
        ("C", "I would rather double-check than assume."),
    ],
    [
        ("I", "I am comfortable in front of a group."),
        ("C", "I am comfortable working through detail."),
        ("S", "I am comfortable letting others lead."),
        ("D", "I am comfortable making unpopular calls."),
    ],
    [
        ("C", "I build a thorough plan."),
        ("S", "I build long relationships."),
        ("D", "I set ambitious targets."),
        ("I", "I build a wide network."),
    ],
    [
        ("S", "I listen more than I talk."),
        ("I", "I think out loud."),
        ("C", "I think it through before I speak."),
        ("D", "I move fast and correct later."),
    ],
    [
        ("D", "I take control when things stall."),
        ("C", "I look for the cause when things stall."),
        ("I", "I bring energy when things stall."),
        ("S", "I keep going steadily when things stall."),
    ],
    [
        ("I", "I give people the benefit of the doubt."),
        ("D", "I hold people to what they committed to."),
        ("S", "I give people time to come around."),
        ("C", "I hold work to a clear standard."),
    ],
    [
        ("S", "Under pressure I go quiet."),
        ("C", "Under pressure I get critical."),
        ("D", "Under pressure I get blunt."),
        ("I", "Under pressure I get talkative."),
    ],
]

# Shown on the results page. Also original text.
STYLE_DESCRIPTIONS: dict[Style, str] = {
    "D": (
        "Direct and decisive. You tend to move first and adjust later, you are "
        "comfortable making a call before everyone agrees, and you would rather "
        "be told the problem than be managed around it. At your best you create "
        "momentum when others are stuck. Under pressure you can come across as "
        "blunt, and you may decide before you have heard everyone out."
    ),
    "I": (
        "Outgoing and persuasive. You think out loud, build networks easily, and "
        "bring energy into a room that has gone flat. You work through problems "
        "by talking about them with people. At your best you get others genuinely "
        "invested. Under pressure you may talk more than you listen, or move on "
        "before the detail is nailed down."
    ),
    "S": (
        "Steady and supportive. You value consistency, follow through on what you "
        "started, and pay attention to whether people are actually all right. You "
        "warm up gradually and stay loyal once you do. At your best you hold a "
        "group together. Under pressure you may go quiet, absorb more than you "
        "should, or avoid a conflict worth having."
    ),
    "C": (
        "Careful and analytical. You want the facts before you commit, you notice "
        "the error everyone else read past, and you would rather be right than "
        "fast. At your best you protect the group from expensive mistakes. Under "
        "pressure you may over-analyze, hold work back longer than needed, or turn "
        "critical."
    ),
}


def validate_content() -> None:
    """Sanity checks on the questionnaire content itself.

    Call this from a test. It catches the mistakes that are easy to make when
    editing the tetrads by hand and hard to notice afterwards.
    """
    styles = {"D", "I", "S", "C"}
    for index, tetrad in enumerate(TETRADS):
        found = [style for style, _ in tetrad]
        if sorted(found) != sorted(styles):
            raise ValueError(
                f"Tetrad {index} must contain exactly one statement per style, got {found}"
            )
        texts = [text for _, text in tetrad]
        if len(set(texts)) != 4:
            raise ValueError(f"Tetrad {index} has duplicate statements")

    all_texts = [text for tetrad in TETRADS for _, text in tetrad]
    if len(set(all_texts)) != len(all_texts):
        raise ValueError("A statement is repeated across tetrads")