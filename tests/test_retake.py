from apps.db import get_connection
from apps.logic.items import TETRADS
from apps.repo import get_results
from tests.test_questionnaire import answer
from tests.test_scoring import HAND_CHECKED_FIXTURE


def only_respondent_id():
    """Each test uses a fresh, isolated database (see conftest.py) in which
    complete_questionnaire creates exactly one respondent -- so it's safe to
    just grab that one row's id to assert on the database directly."""
    conn = get_connection()
    try:
        row = conn.execute("SELECT id FROM respondents").fetchone()
    finally:
        conn.close()
    return row["id"]


def complete_questionnaire(client, answers):
    client.get("/q/0")
    for index, ans in enumerate(answers):
        answer(client, index, ans.most_style, ans.least_style)


def test_completed_respondent_can_still_view_a_tetrad_to_edit_it(client):
    complete_questionnaire(client, HAND_CHECKED_FIXTURE)

    response = client.get("/q/0")
    assert response.status_code == 200
    # HAND_CHECKED_FIXTURE's tetrad 0 is Answer("D", "C") -- both radios
    # for the previously saved answer should be pre-selected.
    assert 'name="most_style" value="D" required\n        checked' in response.text
    assert 'name="least_style" value="C" required\n        checked' in response.text


def test_retake_clears_answers_and_restarts_at_question_one(client):
    complete_questionnaire(client, HAND_CHECKED_FIXTURE)
    client.get("/results")  # ensure results were computed and saved
    respondent_id = only_respondent_id()
    assert get_results(respondent_id) is not None

    response = client.post("/retake", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/q/0"

    # Nothing should be answered anymore.
    resume = client.get("/", follow_redirects=False)
    assert resume.headers["location"] == "/q/0"

    tetrad_page = client.get("/q/0")
    assert "checked" not in tetrad_page.text

    # The persisted results row must be gone too, not just the answers.
    assert get_results(respondent_id) is None


def test_retake_lets_a_respondent_complete_a_fresh_run(client):
    complete_questionnaire(client, HAND_CHECKED_FIXTURE)
    client.post("/retake")

    for i in range(len(TETRADS)):
        response = answer(client, i, "I", "D")

    assert response.headers["location"] == "/results"
    final = client.get("/results")
    assert final.status_code == 200
    assert "Influence" in final.text


def test_retake_with_no_session_redirects_to_start(client):
    response = client.post("/retake", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/q/0"


def test_reviewing_question_one_and_clicking_next_goes_to_question_two(client):
    """Regression test: after finishing the questionnaire, reviewing an
    early answer and clicking Next used to jump straight to /results
    instead of the next question, because the "where to go next" logic
    only knew "first unanswered tetrad" -- and there isn't one once
    everything's done."""
    complete_questionnaire(client, HAND_CHECKED_FIXTURE)

    client.get("/q/0")
    response = answer(
        client, 0, HAND_CHECKED_FIXTURE[0].most_style, HAND_CHECKED_FIXTURE[0].least_style
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/q/1"


def test_reviewing_the_last_question_and_clicking_next_goes_to_results(client):
    complete_questionnaire(client, HAND_CHECKED_FIXTURE)

    last_index = len(HAND_CHECKED_FIXTURE) - 1
    client.get(f"/q/{last_index}")
    last_answer = HAND_CHECKED_FIXTURE[last_index]
    response = answer(client, last_index, last_answer.most_style, last_answer.least_style)

    assert response.status_code == 303
    assert response.headers["location"] == "/results"
