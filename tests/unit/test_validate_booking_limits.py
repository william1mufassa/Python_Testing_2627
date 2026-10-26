import server
from tests.conftest import find

LIMIT_12 = "You cannot book more than 12 places per competition."
NOT_ENOUGH_PLACES = "Not enough places available in this competition."


def rich_club(clubs):
    return find(clubs, "Rich Club")  # 30 points : jamais bloqué par les points ici


def test_booking_exactly_12_places_is_accepted(clubs, competitions):
    competition = find(competitions, "Future Open")  # 25 places

    assert server.validate_booking(rich_club(clubs), competition, 12) is None


def test_booking_13_places_is_refused(clubs, competitions):
    competition = find(competitions, "Future Open")

    assert server.validate_booking(rich_club(clubs), competition, 13) == LIMIT_12


def test_booking_is_refused_when_cumulative_total_exceeds_12(clubs, competitions):
    competition = find(competitions, "Future Open")

    result = server.validate_booking(rich_club(clubs), competition, 6, already_booked=7)

    assert result == LIMIT_12


def test_booking_is_accepted_when_cumulative_total_reaches_12(clubs, competitions):
    competition = find(competitions, "Future Open")

    result = server.validate_booking(rich_club(clubs), competition, 5, already_booked=7)

    assert result is None


def test_booking_all_remaining_places_is_accepted(clubs, competitions):
    competition = find(competitions, "Small Cup")  # 5 places

    assert server.validate_booking(rich_club(clubs), competition, 5) is None


def test_booking_more_than_remaining_places_is_refused(clubs, competitions):
    competition = find(competitions, "Small Cup")

    assert server.validate_booking(rich_club(clubs), competition, 6) == NOT_ENOUGH_PLACES


def test_booking_in_full_competition_is_refused(clubs, competitions):
    competition = find(competitions, "Full Cup")  # 0 place

    assert server.validate_booking(rich_club(clubs), competition, 1) == NOT_ENOUGH_PLACES


def test_limit_of_12_is_checked_before_remaining_places_and_points(clubs, competitions):
    club = find(clubs, "Small Club")  # 4 points
    competition = find(competitions, "Small Cup")  # 5 places

    assert server.validate_booking(club, competition, 13) == LIMIT_12


def test_remaining_places_are_checked_before_points(clubs, competitions):
    club = find(clubs, "Small Club")  # 4 points
    competition = find(competitions, "Small Cup")  # 5 places

    assert server.validate_booking(club, competition, 6) == NOT_ENOUGH_PLACES


def test_max_bookable_places_is_limited_by_the_12_places_rule(clubs, competitions):
    competition = find(competitions, "Future Open")

    assert server.max_bookable_places(rich_club(clubs), competition, already_booked=3) == 9


def test_max_bookable_places_is_limited_by_remaining_places(clubs, competitions):
    competition = find(competitions, "Small Cup")

    assert server.max_bookable_places(rich_club(clubs), competition) == 5


def test_max_bookable_places_is_limited_by_points(clubs, competitions):
    competition = find(competitions, "Future Open")

    assert server.max_bookable_places(find(clubs, "Small Club"), competition) == 4


def test_max_bookable_places_is_never_negative(clubs, competitions):
    competition = find(competitions, "Full Cup")

    assert server.max_bookable_places(rich_club(clubs), competition, already_booked=12) == 0
