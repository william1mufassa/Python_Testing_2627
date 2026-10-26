import pytest

import server
from tests.conftest import find


@pytest.mark.parametrize("email", ["nobody@club.test", ""])
def test_login_with_unknown_or_empty_email_shows_error(client, email):
    response = client.post("/showSummary", data={"email": email})

    assert response.status_code == 401
    assert b"Sorry, that email was not found." in response.data
    assert b"Please enter your secretary email" in response.data


def test_login_without_email_field_shows_error(client):
    response = client.post("/showSummary", data={})

    assert response.status_code == 401
    assert b"Sorry, that email was not found." in response.data


@pytest.mark.parametrize("url", [
    "/book/Future Open/Ghost Club",
    "/book/Ghost Cup/Alpha Club",
])
def test_booking_page_with_unknown_club_or_competition_returns_404(client, url):
    response = client.get(url)

    assert response.status_code == 404
    assert b"Something went wrong-please try again" in response.data


@pytest.mark.parametrize("form", [
    {"competition": "Ghost Cup", "club": "Alpha Club", "places": "1"},
    {"competition": "Future Open", "club": "Ghost Club", "places": "1"},
    {},
])
def test_purchase_with_unknown_club_or_competition_changes_nothing(client, form):
    response = client.post("/purchasePlaces", data=form)

    assert response.status_code == 404
    assert b"Something went wrong-please try again" in response.data
    assert find(server.competitions, "Future Open")["numberOfPlaces"] == 25
    assert find(server.clubs, "Alpha Club")["points"] == 20
