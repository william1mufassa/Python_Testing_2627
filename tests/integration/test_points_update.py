import server
from tests.conftest import find


def purchase(client, club, competition, places):
    return client.post("/purchasePlaces", data={
        "club": club, "competition": competition, "places": str(places),
    })


def test_purchase_deducts_points_and_shows_new_balance(client):
    response = purchase(client, "Alpha Club", "Future Open", 4)

    assert response.status_code == 200
    assert b"Points available: 16" in response.data
    assert int(find(server.clubs, "Alpha Club")["points"]) == 16


def test_purchase_confirms_number_of_places_booked(client):
    response = purchase(client, "Alpha Club", "Future Open", 4)

    assert b"Great-booking complete! You booked 4 place(s)." in response.data


def test_purchase_updates_places_shown_for_the_competition(client):
    response = purchase(client, "Alpha Club", "Future Open", 4)

    assert b"Number of Places: 21" in response.data


def test_points_spent_earlier_are_no_longer_available(client):
    purchase(client, "Small Club", "Future Open", 4)
    response = purchase(client, "Small Club", "Small Cup", 1)

    assert response.status_code == 400
    assert b"You do not have enough points." in response.data


def test_summary_shows_competition_full_instead_of_booking_link(client):
    response = client.post("/showSummary", data={"email": "alpha@club.test"})

    assert b"Competition full" in response.data
    assert b"/book/Full%20Cup/Alpha%20Club" not in response.data
