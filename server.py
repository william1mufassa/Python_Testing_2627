import json
import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, flash, url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLUBS_FILE = os.path.join(BASE_DIR, 'clubs.json')
COMPETITIONS_FILE = os.path.join(BASE_DIR, 'competitions.json')


def loadClubs(path=CLUBS_FILE):
    with open(path) as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


def loadCompetitions(path=COMPETITIONS_FILE):
    with open(path) as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions


def prepare_clubs(clubs):
    """Convertit les points (chaînes dans le JSON) en entiers."""
    for club in clubs:
        club['points'] = int(club['points'])
    return clubs


def prepare_competitions(competitions):
    """Convertit le nombre de places (chaînes dans le JSON) en entiers."""
    for competition in competitions:
        competition['numberOfPlaces'] = int(competition['numberOfPlaces'])
    return competitions


def find_club_by_email(email, clubs):
    """Renvoie le club dont l'e-mail correspond, ou None."""
    if not email:
        return None
    email = email.strip()
    return next((club for club in clubs if club['email'] == email), None)


def find_club_by_name(name, clubs):
    """Renvoie le club portant ce nom, ou None."""
    return next((club for club in clubs if club['name'] == name), None)


def find_competition_by_name(name, competitions):
    """Renvoie la compétition portant ce nom, ou None."""
    return next((comp for comp in competitions if comp['name'] == name), None)


MAX_PLACES_PER_COMPETITION = 12
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def is_competition_past(competition, now=None):
    """Vrai si la compétition a déjà commencé (date <= maintenant)."""
    now = now or datetime.now()
    return datetime.strptime(competition['date'], DATE_FORMAT) <= now


def parse_places(value):
    """Convertit la saisie en entier strictement positif, sinon renvoie None."""
    try:
        places = int(value)
    except (TypeError, ValueError):
        return None
    return places if places > 0 else None


def validate_booking(club, competition, places, already_booked=0):
    """Renvoie None si la réservation est possible, sinon le message d'erreur.

    already_booked : places déjà réservées par ce club dans cette compétition.
    Un point est dépensé par place réservée.
    """
    if is_competition_past(competition):
        return "This competition has already taken place."
    if already_booked + places > MAX_PLACES_PER_COMPETITION:
        return "You cannot book more than 12 places per competition."
    if places > competition['numberOfPlaces']:
        return "Not enough places available in this competition."
    if places > club['points']:
        return "You do not have enough points."
    return None


def max_bookable_places(club, competition, already_booked=0):
    """Nombre maximal de places que le club peut encore réserver (pour le formulaire)."""
    return max(0, min(MAX_PLACES_PER_COMPETITION - already_booked,
                      competition['numberOfPlaces'],
                      club['points']))


def apply_booking(club, competition, places, bookings):
    """Enregistre une réservation validée : 1 point dépensé par place."""
    club['points'] -= places
    competition['numberOfPlaces'] -= places
    key = (competition['name'], club['name'])
    bookings[key] = bookings.get(key, 0) + places


def points_board(clubs):
    """Nom et points de chaque club, triés par nom (sans les e-mails)."""
    rows = [{'name': club['name'], 'points': club['points']} for club in clubs]
    return sorted(rows, key=lambda row: row['name'])


def booking_success_message(places):
    return f"Great-booking complete! You booked {places} place(s)."


app = Flask(__name__)
app.secret_key = 'something_special'
app.jinja_env.globals['is_competition_past'] = is_competition_past

competitions = prepare_competitions(loadCompetitions())
clubs = prepare_clubs(loadClubs())
# Places réservées par club et par compétition : {(nom_competition, nom_club): nombre}
bookings = {}


def already_booked(club, competition):
    return bookings.get((competition['name'], club['name']), 0)


def render_booking(club, competition, status=200):
    max_places = max_bookable_places(club, competition, already_booked(club, competition))
    page = render_template('booking.html', club=club, competition=competition,
                           max_places=max_places)
    return page, status


@app.route('/')
def index():
    return render_template('index.html')


def not_found(club):
    """Page renvoyée quand le club ou la compétition demandés n'existent pas."""
    flash("Something went wrong-please try again")
    if club is None:
        return render_template('index.html'), 404
    return render_template('welcome.html', club=club, competitions=competitions), 404


@app.route('/showSummary', methods=['POST'])
def showSummary():
    club = find_club_by_email(request.form.get('email'), clubs)
    if club is None:
        flash("Sorry, that email was not found.")
        return render_template('index.html'), 401
    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = find_club_by_name(club, clubs)
    foundCompetition = find_competition_by_name(competition, competitions)
    if foundClub is None or foundCompetition is None:
        return not_found(foundClub)
    if is_competition_past(foundCompetition):
        flash("This competition has already taken place.")
        return render_template('welcome.html', club=foundClub, competitions=competitions), 400
    return render_booking(foundClub, foundCompetition)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = find_competition_by_name(request.form.get('competition'), competitions)
    club = find_club_by_name(request.form.get('club'), clubs)
    if club is None or competition is None:
        return not_found(club)
    placesRequired = parse_places(request.form.get('places'))
    if placesRequired is None:
        flash("Please enter a valid number of places.")
        return render_booking(club, competition, 400)
    error = validate_booking(club, competition, placesRequired,
                             already_booked(club, competition))
    if error:
        flash(error)
        return render_booking(club, competition, 400)
    apply_booking(club, competition, placesRequired, bookings)
    flash(booking_success_message(placesRequired))
    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/pointsBoard')
def pointsBoard():
    """Tableau public, en lecture seule, des points de tous les clubs."""
    return render_template('points.html', board=points_board(clubs))


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
