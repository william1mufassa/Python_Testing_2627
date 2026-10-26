import server
from tests.conftest import find


def purchase(client, club, competition, places):
    return client.post("/purchasePlaces", data={
        "club": club, "competition": competition, "places": str(places),
    })


def test_purchase_refused_when_club_has_not_enough_points(client):
    response = purchase(client, "Small Club", "Future Open", 5)

    assert response.status_code == 400
    assert b"You do not have enough points." in response.data
    assert b"How many places?" in response.data  # la page de réservation est réaffichée
    assert find(server.competitions, "Future Open")["numberOfPlaces"] == "25"
    assert find(server.clubs, "Small Club")["points"] == "4"


def test_purchase_accepted_when_club_spends_exactly_its_points(client):
    response = purchase(client, "Small Club", "Future Open", 4)

    assert response.status_code == 200
    assert b"Great-booking complete!" in response.data
    assert find(server.competitions, "Future Open")["numberOfPlaces"] == 21
