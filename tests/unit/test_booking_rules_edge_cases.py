"""Cas limites supplémentaires des règles de réservation (fonctions pures)."""
from datetime import datetime

import server


def club(points=30, name="Club"):
    return {"name": name, "email": f"{name.lower()}@club.test", "points": points}


def competition(places=25, date="2099-01-01 10:00:00", name="Cup"):
    return {"name": name, "date": date, "numberOfPlaces": places}


def test_booking_hitting_every_limit_at_once_is_accepted():
    # 12 places = cumul max = places restantes = points du club
    assert server.validate_booking(club(points=12), competition(places=12), 12) is None


def test_one_more_place_after_12_already_booked_is_refused():
    result = server.validate_booking(club(), competition(), 1, already_booked=12)

    assert result == "You cannot book more than 12 places per competition."


def test_last_allowed_place_after_11_already_booked_is_accepted():
    assert server.validate_booking(club(), competition(), 1, already_booked=11) is None


def test_past_and_full_competition_reports_past_first():
    past_and_full = competition(places=0, date="2000-01-01 10:00:00")

    assert server.validate_booking(club(), past_and_full, 1) == \
        "This competition has already taken place."


def test_club_without_points_cannot_book_in_full_competition():
    assert server.validate_booking(club(points=0), competition(places=0), 1) == \
        "Not enough places available in this competition."


def test_max_bookable_places_is_12_when_nothing_else_limits():
    assert server.max_bookable_places(club(points=100), competition(places=100)) == 12


def test_max_bookable_places_is_zero_after_12_bookings():
    assert server.max_bookable_places(club(), competition(), already_booked=12) == 0


def test_max_bookable_places_is_zero_without_points():
    assert server.max_bookable_places(club(points=0), competition()) == 0


def test_is_competition_past_uses_current_time_by_default():
    assert server.is_competition_past(competition(date="2099-01-01 10:00:00")) is False


def test_is_competition_past_with_competition_one_day_ago():
    now = datetime(2030, 5, 2, 10, 0, 0)

    assert server.is_competition_past(competition(date="2030-05-01 10:00:00"), now) is True


def test_bookings_are_tracked_separately_for_each_club():
    bookings, cup = {}, competition()

    server.apply_booking(club(name="A"), cup, 2, bookings)
    server.apply_booking(club(name="B"), cup, 3, bookings)

    assert bookings == {("Cup", "A"): 2, ("Cup", "B"): 3}


def test_bookings_are_tracked_separately_for_each_competition():
    bookings, buyer = {}, club()

    server.apply_booking(buyer, competition(name="Cup 1"), 2, bookings)
    server.apply_booking(buyer, competition(name="Cup 2"), 4, bookings)

    assert bookings == {("Cup 1", "Club"): 2, ("Cup 2", "Club"): 4}


def test_success_message_for_the_maximum_of_12_places():
    assert server.booking_success_message(12) == \
        "Great-booking complete! You booked 12 place(s)."


def test_points_board_includes_clubs_with_zero_points():
    assert server.points_board([club(points=0, name="Empty")]) == [{"name": "Empty", "points": 0}]


def test_prepare_clubs_converts_every_club():
    clubs = server.prepare_clubs([club(points="1", name="A"), club(points="2", name="B")])

    assert [c["points"] for c in clubs] == [1, 2]


def test_parse_places_accepts_large_values_rules_are_checked_later():
    assert server.parse_places("100") == 100
