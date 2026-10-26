import server
from tests.conftest import find

NOT_ENOUGH_POINTS = "You do not have enough points."


def test_booking_is_valid_when_club_has_more_points_than_needed(clubs, competitions):
    club = find(clubs, "Alpha Club")  # 20 points
    competition = find(competitions, "Future Open")

    assert server.validate_booking(club, competition, 3) is None


def test_booking_is_valid_when_points_are_exactly_enough(clubs, competitions):
    club = find(clubs, "Small Club")  # 4 points
    competition = find(competitions, "Future Open")

    assert server.validate_booking(club, competition, 4) is None


def test_booking_is_refused_when_club_is_one_point_short(clubs, competitions):
    club = find(clubs, "Small Club")  # 4 points
    competition = find(competitions, "Future Open")

    assert server.validate_booking(club, competition, 5) == NOT_ENOUGH_POINTS


def test_booking_is_refused_when_club_has_no_points(clubs, competitions):
    club = dict(find(clubs, "Small Club"), points=0)
    competition = find(competitions, "Future Open")

    assert server.validate_booking(club, competition, 1) == NOT_ENOUGH_POINTS


def test_validation_does_not_modify_club_or_competition(clubs, competitions):
    club = find(clubs, "Small Club")
    competition = find(competitions, "Future Open")

    server.validate_booking(club, competition, 5)

    assert club["points"] == 4
    assert competition["numberOfPlaces"] == 25
