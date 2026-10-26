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


def validate_booking(club, competition, places):
    """Renvoie None si la réservation est possible, sinon le message d'erreur.

    Un point est dépensé par place réservée.
    """
    if places > int(club['points']):
        return "You do not have enough points."
    return None


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()


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
    return render_template('booking.html', club=foundClub, competition=foundCompetition)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = find_competition_by_name(request.form.get('competition'), competitions)
    club = find_club_by_name(request.form.get('club'), clubs)
    if club is None or competition is None:
        return not_found(club)
    placesRequired = int(request.form['places'])
    error = validate_booking(club, competition, placesRequired)
    if error:
        flash(error)
        return render_template('booking.html', club=club, competition=competition), 400
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
