"""Fixtures partagées.

Les tests n'utilisent jamais le contenu réel de clubs.json et
competitions.json : des données contrôlées sont injectées dans le module
server avant chaque test, puis restaurées automatiquement par monkeypatch.
"""
from copy import deepcopy
from datetime import datetime, timedelta

import pytest

import server

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def relative_date(**delta):
    """Date au format des fichiers JSON, décalée par rapport à maintenant."""
    return (datetime.now() + timedelta(**delta)).strftime(DATE_FORMAT)


# Même format que les fichiers JSON (nombres stockés en chaînes).
CLUBS = [
    {"name": "Alpha Club", "email": "alpha@club.test", "points": "20"},
    {"name": "Small Club", "email": "small@club.test", "points": "4"},
    {"name": "Rich Club", "email": "rich@club.test", "points": "30"},
]


def build_competitions():
    return [
        {"name": "Future Open", "date": relative_date(days=30), "numberOfPlaces": "25"},
        {"name": "Small Cup", "date": relative_date(days=30), "numberOfPlaces": "5"},
        {"name": "Full Cup", "date": relative_date(days=30), "numberOfPlaces": "0"},
        {"name": "Past Classic", "date": relative_date(days=-365), "numberOfPlaces": "10"},
        {"name": "Started Today", "date": relative_date(minutes=-5), "numberOfPlaces": "10"},
    ]


@pytest.fixture
def clubs():
    return deepcopy(CLUBS)


@pytest.fixture
def competitions():
    return build_competitions()


@pytest.fixture(autouse=True)
def isolated_data(monkeypatch, clubs, competitions):
    """Remplace les données globales du serveur pour chaque test."""
    monkeypatch.setattr(server, "clubs", clubs)
    monkeypatch.setattr(server, "competitions", competitions)


@pytest.fixture
def client():
    server.app.config["TESTING"] = True
    with server.app.test_client() as test_client:
        yield test_client


def find(items, name):
    return next(item for item in items if item["name"] == name)
