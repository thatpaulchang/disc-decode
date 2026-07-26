from apps.logic.items import TETRADS


def answer(client, index, most, least):
    return client.post(
        f"/q/{index}",
        data={"most_style": most, "least_style": least},
        follow_redirects=False,
    )


def test_first_visit_shows_landing_page(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 200
    assert "DISC" in response.text


def test_returning_visitor_is_redirected_to_resume_point(client):
    client.get("/q/0")  # establishes a session
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/q/0"


def test_answering_a_tetrad_advances_to_the_next_one(client):
    client.get("/q/0")
    response = answer(client, 0, "D", "I")
    assert response.status_code == 303
    assert response.headers["location"] == "/q/1"


def test_refresh_mid_questionnaire_resumes_at_first_unanswered(client):
    client.get("/q/0")
    answer(client, 0, "D", "I")
    answer(client, 1, "S", "C")

    response = client.get("/", follow_redirects=False)
    assert response.headers["location"] == "/q/2"


def test_changing_an_earlier_answer_updates_not_duplicates(client):
    client.get("/q/0")
    answer(client, 0, "D", "I")
    answer(client, 1, "S", "C")

    # Go back and change tetrad 0.
    response = answer(client, 0, "S", "D")
    assert response.status_code == 303
    # Should return to the true first-unanswered tetrad (2), not duplicate.
    assert response.headers["location"] == "/q/2"


def test_same_style_for_most_and_least_is_rejected(client):
    client.get("/q/0")
    response = answer(client, 0, "D", "D")
    assert response.status_code == 400

    # Confirm nothing was written: tetrad 0 should still be the resume point.
    resume = client.get("/", follow_redirects=False)
    assert resume.headers["location"] == "/q/0"


def test_out_of_range_tetrad_index_is_a_clean_error(client):
    response = client.get("/q/50")
    assert response.status_code == 404

    response = client.get("/q/-1")
    assert response.status_code == 404


def test_posting_out_of_range_tetrad_index_is_a_clean_error(client):
    client.get("/q/0")
    response = answer(client, 50, "D", "I")
    assert response.status_code == 404


def test_posting_ahead_of_resume_point_does_not_write(client):
    client.get("/q/0")
    response = answer(client, 10, "D", "I")
    # Rejected back to the true resume point, not accepted out of order.
    assert response.status_code == 303
    assert response.headers["location"] == "/q/0"

    resume = client.get("/", follow_redirects=False)
    assert resume.headers["location"] == "/q/0"


def test_results_before_finishing_redirects_to_first_unanswered(client):
    client.get("/q/0")
    answer(client, 0, "D", "I")

    response = client.get("/results", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/q/1"


def test_completing_all_tetrads_redirects_to_results(client):
    client.get("/q/0")
    for i in range(len(TETRADS)):
        response = answer(client, i, "D", "I")

    assert response.headers["location"] == "/results"
    final = client.get("/results", follow_redirects=False)
    assert final.status_code == 200


def test_no_session_cookie_is_a_new_visitor_not_an_error(client):
    response = client.get("/q/0")
    assert response.status_code == 200
