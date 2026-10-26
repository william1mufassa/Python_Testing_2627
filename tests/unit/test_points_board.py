import server


def test_points_board_lists_every_club_with_its_points(clubs):
    board = server.points_board(clubs)

    assert {"name": "Alpha Club", "points": 20} in board
    assert {"name": "Small Club", "points": 4} in board
    assert {"name": "Rich Club", "points": 30} in board
    assert len(board) == 3


def test_points_board_is_sorted_by_club_name(clubs):
    names = [row["name"] for row in server.points_board(clubs)]

    assert names == ["Alpha Club", "Rich Club", "Small Club"]


def test_points_board_does_not_expose_emails(clubs):
    assert all("email" not in row for row in server.points_board(clubs))


def test_points_board_of_no_clubs_is_empty():
    assert server.points_board([]) == []


def test_points_board_does_not_modify_clubs(clubs):
    before = [dict(club) for club in clubs]

    server.points_board(clubs)

    assert clubs == before
