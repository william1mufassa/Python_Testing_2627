from datetime import datetime

import server
from tests.conftest import find

PAST = "This competition has already taken place."


def competition_on(date):
    return {"name": "Any", "date": date, "numberOfPlaces": "10"}


def test_competition_in_the_past_is_past(competitions):
    assert server.is_competition_past(find(competitions, "Past Classic")) is True


def test_competition_in_the_future_is_not_past(competitions):
    assert server.is_competition_past(find(competitions, "Future Open")) is False


def test_competition_that_started_earlier_today_is_past(competitions):
    assert server.is_competition_past(find(competitions, "Started Today")) is True


def test_competition_starting_right_now_is_past():
    now = datetime(2030, 5, 1, 10, 0, 0)

    assert server.is_competition_past(competition_on("2030-05-01 10:00:00"), now) is True


def test_competition_starting_one_second_later_is_not_past():
    now = datetime(2030, 5, 1, 9, 59, 59)

    assert server.is_competition_past(competition_on("2030-05-01 10:00:00"), now) is False


def test_original_2020_competitions_are_past():
    now = datetime(2026, 1, 1)

    assert server.is_competition_past(competition_on("2020-03-27 10:00:00"), now) is True


def test_booking_in_past_competition_is_refused(clubs, competitions):
    club = find(clubs, "Rich Club")

    assert server.validate_booking(club, find(competitions, "Past Classic"), 1) == PAST


def test_past_competition_is_checked_before_the_12_places_limit(clubs, competitions):
    club = find(clubs, "Rich Club")

    assert server.validate_booking(club, find(competitions, "Past Classic"), 13) == PAST
