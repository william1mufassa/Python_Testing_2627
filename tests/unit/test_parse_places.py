import pytest

import server


@pytest.mark.parametrize("value, expected", [("1", 1), ("12", 12), (" 7 ", 7)])
def test_parse_places_accepts_strictly_positive_integers(value, expected):
    assert server.parse_places(value) == expected


@pytest.mark.parametrize("value", ["0", "-3", "", "   ", "abc", "1.5", "2e1", None])
def test_parse_places_rejects_invalid_values(value):
    assert server.parse_places(value) is None
