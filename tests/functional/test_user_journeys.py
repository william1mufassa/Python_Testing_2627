"""Parcours complets d'un secrétaire, uniquement via l'interface HTTP."""
import re


def points_on_board(html, club_name):
    match = re.search(rf"<td>{club_name}</td>\s*<td>(\d+)</td>", html)
    return int(match.group(1))


def test_secretary_books_places_and_sees_updated_points_everywhere(client):
    assert points_on_board(client.get("/pointsBoard").get_data(as_text=True), "Alpha Club") == 20

    summary = client.post("/showSummary", data={"email": "alpha@club.test"})
    assert b"Points available: 20" in summary.data

    booking_page = client.get("/book/Future Open/Alpha Club")
    assert b"Places available: 25" in booking_page.data

    confirmation = client.post("/purchasePlaces", data={
        "club": "Alpha Club", "competition": "Future Open", "places": "3",
    })
    assert b"Great-booking complete! You booked 3 place(s)." in confirmation.data
    assert b"Points available: 17" in confirmation.data
    assert b"Number of Places: 22" in confirmation.data

    board = client.get("/pointsBoard").get_data(as_text=True)
    assert points_on_board(board, "Alpha Club") == 17

    logout = client.get("/logout", follow_redirects=True)
    assert b"Please enter your secretary email" in logout.data


def test_secretary_recovers_from_unknown_email_then_logs_in(client):
    wrong = client.post("/showSummary", data={"email": "typo@club.test"})
    assert wrong.status_code == 401
    assert b"Sorry, that email was not found." in wrong.data

    right = client.post("/showSummary", data={"email": "rich@club.test"})
    assert right.status_code == 200
    assert b"Points available: 30" in right.data


def test_secretary_is_stopped_by_every_booking_rule(client):
    def buy(competition, places):
        return client.post("/purchasePlaces", data={
            "club": "Rich Club", "competition": competition, "places": places,
        })

    assert b"Please enter a valid number of places." in buy("Future Open", "abc").data
    assert b"This competition has already taken place." in buy("Past Classic", "1").data
    assert b"Not enough places available" in buy("Small Cup", "6").data
    assert buy("Future Open", "10").status_code == 200
    assert b"You cannot book more than 12 places" in buy("Future Open", "3").data

    board = client.get("/pointsBoard").get_data(as_text=True)
    assert points_on_board(board, "Rich Club") == 20


def test_small_club_cannot_spend_more_points_than_it_has(client):
    refused = client.post("/purchasePlaces", data={
        "club": "Small Club", "competition": "Future Open", "places": "5",
    })
    assert b"You do not have enough points." in refused.data

    board = client.get("/pointsBoard").get_data(as_text=True)
    assert points_on_board(board, "Small Club") == 4
