def test_points_board_is_public_and_lists_clubs(client):
    response = client.get("/pointsBoard")

    assert response.status_code == 200
    for expected in (b"Alpha Club", b"20", b"Small Club", b"4", b"Rich Club", b"30"):
        assert expected in response.data


def test_points_board_does_not_show_emails(client):
    response = client.get("/pointsBoard")

    assert b"@club.test" not in response.data


def test_points_board_is_read_only(client):
    response = client.post("/pointsBoard", data={"points": "999"})

    assert response.status_code == 405


def test_index_and_summary_link_to_points_board(client):
    index = client.get("/")
    summary = client.post("/showSummary", data={"email": "alpha@club.test"})

    assert b'href="/pointsBoard"' in index.data
    assert b'href="/pointsBoard"' in summary.data
