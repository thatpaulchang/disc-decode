from apps.logic.items import TETRADS
from tests.test_questionnaire import answer
from tests.test_scoring import HAND_CHECKED_FIXTURE


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
    assert "checked" in response.text


def test_retake_clears_answers_and_restarts_at_question_one(client):
    complete_questionnaire(client, HAND_CHECKED_FIXTURE)
    client.get("/results")  # ensure results were computed and saved

    response = client.post("/retake", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/q/0"

    # Nothing should be answered anymore.
    resume = client.get("/", follow_redirects=False)
    assert resume.headers["location"] == "/q/0"

    tetrad_page = client.get("/q/0")
    assert "checked" not in tetrad_page.text


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
