import server


def make_club(points=20):
    return {"name": "Club", "email": "club@club.test", "points": points}


def make_competition(places=25):
    return {"name": "Cup", "date": "2030-01-01 10:00:00", "numberOfPlaces": places}


def test_prepare_clubs_converts_points_to_integers():
    clubs = server.prepare_clubs([make_club(points="13")])

    assert clubs == [make_club(points=13)]


def test_prepare_clubs_keeps_integer_points():
    assert server.prepare_clubs([make_club(points=4)])[0]["points"] == 4


def test_prepare_competitions_converts_places_to_integers():
    competitions = server.prepare_competitions([make_competition(places="25")])

    assert competitions == [make_competition(places=25)]


def test_prepare_competitions_keeps_integer_places():
    assert server.prepare_competitions([make_competition(places=0)])[0]["numberOfPlaces"] == 0


def test_apply_booking_deducts_one_point_per_place():
    club, competition = make_club(points=20), make_competition()

    server.apply_booking(club, competition, 3, {})

    assert club["points"] == 17


def test_apply_booking_deducts_places_from_competition():
    club, competition = make_club(), make_competition(places=25)

    server.apply_booking(club, competition, 3, {})

    assert competition["numberOfPlaces"] == 22


def test_apply_booking_records_places_booked_by_the_club():
    club, competition, bookings = make_club(), make_competition(), {}

    server.apply_booking(club, competition, 3, bookings)
    server.apply_booking(club, competition, 2, bookings)

    assert bookings == {("Cup", "Club"): 5}


def test_apply_booking_can_spend_all_points_and_places():
    club, competition = make_club(points=5), make_competition(places=5)

    server.apply_booking(club, competition, 5, {})

    assert club["points"] == 0
    assert competition["numberOfPlaces"] == 0


def test_success_message_contains_number_of_places():
    assert server.booking_success_message(4) == "Great-booking complete! You booked 4 place(s)."


def test_success_message_for_a_single_place():
    assert server.booking_success_message(1) == "Great-booking complete! You booked 1 place(s)."
