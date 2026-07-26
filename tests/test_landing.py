def test_submitting_a_name_starts_a_run(client):
    response = client.post("/", data={"display_name": "Alex"}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/q/0"


def test_submitting_blank_name_is_rejected(client):
    response = client.post("/", data={"display_name": "   "})
    assert response.status_code == 400
    assert "name" in response.text.lower()


def test_landing_page_shows_disclaimer(client):
    response = client.get("/")
    assert "ipsative" in response.text.lower()
    assert "not suitable for hiring" in response.text
