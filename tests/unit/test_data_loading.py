import json
import os

import server


def write_json(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")
    return str(path)


def test_load_clubs_reads_the_given_file(tmp_path):
    clubs = [{"name": "A", "email": "a@a.test", "points": "3"}]
    path = write_json(tmp_path / "clubs.json", {"clubs": clubs})

    assert server.loadClubs(path) == clubs


def test_load_competitions_reads_the_given_file(tmp_path):
    competitions = [{"name": "C", "date": "2030-01-01 10:00:00", "numberOfPlaces": "8"}]
    path = write_json(tmp_path / "competitions.json", {"competitions": competitions})

    assert server.loadCompetitions(path) == competitions


def test_data_files_are_located_next_to_server_module():
    server_dir = os.path.dirname(os.path.abspath(server.__file__))

    assert server.CLUBS_FILE == os.path.join(server_dir, "clubs.json")
    assert server.COMPETITIONS_FILE == os.path.join(server_dir, "competitions.json")


def test_default_loading_does_not_depend_on_working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    assert isinstance(server.loadClubs(), list)
    assert isinstance(server.loadCompetitions(), list)
