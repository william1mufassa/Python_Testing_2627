import server


def test_find_club_by_email_returns_matching_club(clubs):
    club = server.find_club_by_email("small@club.test", clubs)

    assert club["name"] == "Small Club"


def test_find_club_by_email_returns_none_for_unknown_email(clubs):
    assert server.find_club_by_email("nobody@club.test", clubs) is None


def test_find_club_by_email_returns_none_for_empty_email(clubs):
    assert server.find_club_by_email("", clubs) is None


def test_find_club_by_email_returns_none_when_email_is_missing(clubs):
    assert server.find_club_by_email(None, clubs) is None


def test_find_club_by_email_ignores_surrounding_spaces(clubs):
    club = server.find_club_by_email("  alpha@club.test ", clubs)

    assert club["name"] == "Alpha Club"


def test_find_club_by_email_returns_none_when_no_clubs():
    assert server.find_club_by_email("alpha@club.test", []) is None


def test_find_club_by_name_returns_matching_club(clubs):
    assert server.find_club_by_name("Rich Club", clubs)["email"] == "rich@club.test"


def test_find_club_by_name_returns_none_for_unknown_name(clubs):
    assert server.find_club_by_name("Ghost Club", clubs) is None


def test_find_club_by_name_returns_none_for_missing_name(clubs):
    assert server.find_club_by_name(None, clubs) is None


def test_find_competition_by_name_returns_matching_competition(competitions):
    competition = server.find_competition_by_name("Small Cup", competitions)

    assert competition["numberOfPlaces"] == "5"


def test_find_competition_by_name_returns_none_for_unknown_name(competitions):
    assert server.find_competition_by_name("Ghost Cup", competitions) is None


def test_find_competition_by_name_returns_none_for_missing_name(competitions):
    assert server.find_competition_by_name(None, competitions) is None
