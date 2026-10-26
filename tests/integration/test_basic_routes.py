def test_index_page_is_displayed(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Welcome to the GUDLFT Registration Portal!" in response.data


def test_login_with_known_email_shows_summary(client):
    response = client.post("/showSummary", data={"email": "alpha@club.test"})

    assert response.status_code == 200
    assert b"Welcome, alpha@club.test" in response.data
    assert b"Points available: 20" in response.data


def test_logout_redirects_to_index(client):
    response = client.get("/logout")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")
