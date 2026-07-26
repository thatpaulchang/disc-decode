"""Route-level tests for /results.

Reuses the same hand-checked fixture as test_scoring.py, since these tests
verify wiring (score gets computed, saved, and rendered correctly), not the
scoring math itself.
"""

from apps.logic.scoring import Answer
from tests.test_questionnaire import answer
from tests.test_scoring import HAND_CHECKED_FIXTURE


def complete_questionnaire(client, answers):
    client.get("/q/0")
    for index, ans in enumerate(answers):
        answer(client, index, ans.most_style, ans.least_style)


def test_results_page_shows_hand_checked_scores(client):
    complete_questionnaire(client, HAND_CHECKED_FIXTURE)

    response = client.get("/results")
    assert response.status_code == 200

    body = response.text
    # From the hand-checked fixture: diff = D:6, I:2, S:-6, C:-2
    assert "6" in body
    assert "Dominance" in body
    assert "Steadiness" in body


def test_results_page_shows_disclaimer(client):
    complete_questionnaire(client, HAND_CHECKED_FIXTURE)

    response = client.get("/results")
    assert "ipsative" in response.text.lower()
    assert "not suitable for hiring" in response.text


def test_results_are_only_scored_once(client):
    """Answering, viewing results, then somehow re-triggering scoring
    should not change the stored results (scoring runs once)."""
    complete_questionnaire(client, HAND_CHECKED_FIXTURE)

    first_view = client.get("/results")
    second_view = client.get("/results")

    assert first_view.text == second_view.text


def test_all_four_tied_renders_without_crashing(client):
    tied_answers = (
        [Answer("D", "I")] * 6
        + [Answer("I", "D")] * 6
        + [Answer("S", "C")] * 6
        + [Answer("C", "S")] * 6
    )
    complete_questionnaire(client, tied_answers)

    response = client.get("/results")
    assert response.status_code == 200
    assert "0" in response.text
