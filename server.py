import json
import os

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
    if already_booked + places > MAX_PLACES_PER_COMPETITION:
        return "You cannot book more than 12 places per competition."
    if places > int(competition['numberOfPlaces']):
        return "Not enough places available in this competition."
    if places > int(club['points']):
        return "You do not have enough points."
    return None


def max_bookable_places(club, competition, already_booked=0):
    """Nombre maximal de places que le club peut encore réserver (pour le formulaire)."""
    return max(0, min(MAX_PLACES_PER_COMPETITION - already_booked,
                      int(competition['numberOfPlaces']),
                      int(club['points'])))


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()
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
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    key = (competition['name'], club['name'])
    bookings[key] = bookings.get(key, 0) + placesRequired
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
