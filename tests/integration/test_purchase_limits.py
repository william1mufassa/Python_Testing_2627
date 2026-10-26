import pytest

import server
from tests.conftest import find


def purchase(client, club, competition, places):
    return client.post("/purchasePlaces", data={
        "club": club, "competition": competition, "places": str(places),
    })


def assert_nothing_changed(bookings, competition="Future Open", places=25):
    assert find(server.competitions, competition)["numberOfPlaces"] == places
    assert find(server.clubs, "Rich Club")["points"] == 30
    assert bookings == {}


def test_purchase_refused_when_booking_more_than_12_places(client, bookings):
    response = purchase(client, "Rich Club", "Future Open", 13)

    assert response.status_code == 400
    assert b"You cannot book more than 12 places per competition." in response.data
    assert_nothing_changed(bookings)


def test_purchase_refused_when_cumulative_bookings_exceed_12(client, bookings):
    first = purchase(client, "Rich Club", "Future Open", 7)
    second = purchase(client, "Rich Club", "Future Open", 6)

    assert first.status_code == 200
    assert second.status_code == 400
    assert b"You cannot book more than 12 places per competition." in second.data
    assert bookings == {("Future Open", "Rich Club"): 7}
    assert find(server.competitions, "Future Open")["numberOfPlaces"] == 18


def test_purchase_refused_when_not_enough_places_left(client, bookings):
    response = purchase(client, "Rich Club", "Small Cup", 6)

    assert response.status_code == 400
    assert b"Not enough places available in this competition." in response.data
    assert_nothing_changed(bookings, "Small Cup", 5)


@pytest.mark.parametrize("places", ["", "abc", "0", "-3"])
def test_purchase_refused_when_places_is_not_a_positive_integer(client, bookings, places):
    response = purchase(client, "Rich Club", "Future Open", places)

    assert response.status_code == 400
    assert b"Please enter a valid number of places." in response.data
    assert_nothing_changed(bookings)


def test_booking_form_maximum_takes_remaining_places_into_account(client):
    response = client.get("/book/Small Cup/Rich Club")

    assert b'max="5"' in response.data
