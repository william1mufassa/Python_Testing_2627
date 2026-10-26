"""Tests de performance GUDLFT avec Locust.

Scénario d'un secrétaire : accueil, connexion (liste des compétitions),
page de réservation, achat d'une place (mise à jour des points) et
tableau public des points.

Seuils de la spécification, vérifiés automatiquement à la fin du test :
- liste des compétitions (POST /showSummary) : <= 5 secondes
- mise à jour des points (POST /purchasePlaces) : <= 2 secondes

Lancement (serveur Flask démarré au préalable) :
    locust -f tests/performance/locustfile.py --headless -u 6 -r 6 -t 1m \
        --host http://127.0.0.1:5000
"""
import random

from locust import HttpUser, between, events, task

CLUBS = [
    {"name": "Simply Lift", "email": "john@simplylift.co"},
    {"name": "Iron Temple", "email": "admin@irontemple.com"},
    {"name": "She Lifts", "email": "kate@shelifts.co.uk"},
]
FUTURE_COMPETITION = "Winter Challenge"

COMPETITIONS_LIST = "competitions list (POST /showSummary)"
POINTS_UPDATE = "points update (POST /purchasePlaces)"
THRESHOLDS_MS = {COMPETITIONS_LIST: 5000, POINTS_UPDATE: 2000}


class SecretaryUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.club = random.choice(CLUBS)

    @task(3)
    def view_competitions(self):
        self.client.get("/", name="index (GET /)")
        self.client.post("/showSummary", data={"email": self.club["email"]},
                         name=COMPETITIONS_LIST)

    @task(1)
    def book_one_place(self):
        self.client.get(f"/book/{FUTURE_COMPETITION}/{self.club['name']}",
                        name="booking page (GET /book)")
        # Une fois les points, la limite de 12 places ou les places épuisés,
        # l'achat est refusé (400) : c'est le comportement attendu et le temps
        # de réponse reste mesuré.
        with self.client.post("/purchasePlaces", name=POINTS_UPDATE, catch_response=True,
                              data={"club": self.club["name"],
                                    "competition": FUTURE_COMPETITION,
                                    "places": "1"}) as response:
            if response.status_code in (200, 400):
                response.success()
            else:
                response.failure(f"unexpected status {response.status_code}")

    @task(1)
    def view_points_board(self):
        self.client.get("/pointsBoard", name="points board (GET /pointsBoard)")


@events.quitting.add_listener
def check_thresholds(environment, **kwargs):
    """Fait échouer le test (code de sortie 1) si un seuil est dépassé."""
    stats = environment.stats
    for name, limit in THRESHOLDS_MS.items():
        entry = stats.get(name, "POST")
        if entry.num_requests == 0:
            print(f"[FAIL] {name} : aucune requête mesurée")
            environment.process_exit_code = 1
        elif entry.max_response_time > limit:
            print(f"[FAIL] {name} : max {entry.max_response_time:.0f} ms > {limit} ms")
            environment.process_exit_code = 1
        else:
            print(f"[OK] {name} : max {entry.max_response_time:.0f} ms <= {limit} ms")
    if stats.total.fail_ratio > 0:
        print(f"[FAIL] {stats.total.num_failures} requête(s) en échec")
        environment.process_exit_code = 1
