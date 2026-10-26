import pytest

import server
from tests.conftest import find

PAST = b"This competition has already taken place."


@pytest.mark.parametrize("competition", ["Past Classic", "Started Today"])
def test_booking_page_refused_for_competition_already_started(client, competition):
    response = client.get(f"/book/{competition}/Rich Club")

    assert response.status_code == 400
    assert PAST in response.data
    assert b"How many places?" not in response.data


def test_purchase_refused_for_past_competition(client, bookings):
    response = client.post("/purchasePlaces", data={
        "club": "Rich Club", "competition": "Past Classic", "places": "1",
    })

    assert response.status_code == 400
    assert PAST in response.data
    assert find(server.competitions, "Past Classic")["numberOfPlaces"] == "10"
    assert find(server.clubs, "Rich Club")["points"] == "30"
    assert bookings == {}


def test_summary_hides_booking_link_for_past_competitions(client):
    response = client.post("/showSummary", data={"email": "rich@club.test"})

    assert b"Past Classic" in response.data  # toujours visible
    assert b"/book/Past%20Classic/Rich%20Club" not in response.data
    assert b"/book/Future%20Open/Rich%20Club" in response.data
