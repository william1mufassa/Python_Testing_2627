# GUDLFT – Réservation de places aux compétitions régionales

Preuve de concept (POC) Flask qui permet aux secrétaires de clubs d'utiliser
les points de leur club pour réserver des places dans les compétitions à venir.

Ce dépôt corrige les bogues de la phase 1, ajoute la phase 2 (tableau public
des points et tests de performance) et suit le guide de développement des
[spécifications fonctionnelles](Spécifications+fonctionnelles.pdf) : une
branche par sujet, approche TDD, tests unitaires / d'intégration /
fonctionnels séparés et rapports de qualité.

- Dépôt d'origine : <https://github.com/Sedrickgael/Python_Testing_2627>
- Issues de référence (projet d'origine) :
  <https://github.com/OpenClassrooms-Student-Center/Python_Testing/issues>

## 1. Fonctionnalités

- Connexion d'un secrétaire avec l'e-mail de son club (pas de mot de passe).
- Liste des compétitions avec date, places restantes et lien de réservation
  (« Competition over » pour une compétition passée, « Competition full »
  quand il n'y a plus de place).
- Achat de places : **1 point = 1 place**, avec message de confirmation
  indiquant le nombre de places achetées et nouveau solde affiché.
- Règles de réservation (message d'erreur clair et code HTTP 400 en cas de refus) :
  1. saisie : nombre entier strictement positif ;
  2. pas de réservation dans une compétition passée (déjà commencée) ;
  3. **12 places maximum par club et par compétition, en cumulé** ;
  4. pas plus de places que celles restantes (pas de surréservation) ;
  5. pas plus de places que de points disponibles.
- Tableau public des points de tous les clubs (`/pointsBoard`), en lecture
  seule et accessible sans connexion.
- Déconnexion.

## 2. Technologies

- Python 3.9 ou plus (développé et testé avec Python 3.11)
- [Flask 3](https://flask.palletsprojects.com/)
- [pytest](https://docs.pytest.org/), [coverage / pytest-cov](https://coverage.readthedocs.io/),
  [pytest-html](https://pytest-html.readthedocs.io/)
- [Locust](https://locust.io/) pour les tests de performance
- [flake8](https://flake8.pycqa.org/) et [flake8-html](https://pypi.org/project/flake8-html/)

## 3. Installation

Cloner le dépôt puis se placer dans le dossier :

```bash
git clone https://github.com/william1mufassa/Python_Testing_2627.git
cd Python_Testing_2627
```

### Windows (PowerShell ou invite de commandes)

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Pour quitter l'environnement virtuel : `deactivate`. Si vous ajoutez un
paquet, mettez à jour `requirements.txt` avec `pip freeze > requirements.txt`
(la ligne `pywin32` doit garder le marqueur `; sys_platform == "win32"` pour
que l'installation fonctionne aussi sous macOS/Linux).

## 4. Lancer l'application

Depuis le dossier du projet, environnement virtuel activé :

```bash
flask --app server run
```

Puis ouvrir <http://127.0.0.1:5000>. Les e-mails acceptés sont ceux de
`clubs.json` (par exemple `john@simplylift.co`).

Pages principales :

| URL | Méthode | Rôle |
|---|---|---|
| `/` | GET | Page de connexion |
| `/showSummary` | POST | Connexion et liste des compétitions |
| `/book/<compétition>/<club>` | GET | Formulaire de réservation |
| `/purchasePlaces` | POST | Achat de places |
| `/pointsBoard` | GET | Tableau public des points |
| `/logout` | GET | Déconnexion |

## 5. Données et choix techniques

- **Pas de base de données** : `clubs.json` et `competitions.json` sont lus
  au démarrage. Les chemins sont construits à partir de l'emplacement de
  `server.py`, l'application peut donc être lancée depuis n'importe quel dossier.
- **Modifications en mémoire uniquement** : les achats (points, places,
  cumul par club) ne sont pas réécrits dans les fichiers JSON. Un
  redémarrage du serveur remet les données à leur état initial. C'est un
  choix volontaire pour le POC : pas d'écritures concurrentes sur les
  fichiers et des tests reproductibles.
- Les points et les places sont convertis en entiers au chargement
  (`prepare_clubs`, `prepare_competitions`).
- Le cumul des 12 places est suivi dans le dictionnaire `bookings`
  (`{(compétition, club): nombre}`).
- La logique métier est isolée dans des fonctions pures de `server.py`
  (`find_club_by_email`, `parse_places`, `is_competition_past`,
  `validate_booking`, `max_bookable_places`, `apply_booking`,
  `points_board`…), testées unitairement sans serveur.
- Codes HTTP : 200 en cas de succès, 400 pour une réservation refusée,
  401 pour un e-mail inconnu, 404 pour un club ou une compétition introuvables.
- Les deux compétitions d'origine datent de 2020 et ne sont plus
  réservables ; deux compétitions de 2027 ont été ajoutées pour la démonstration.

## 6. Tests

Les tests ne dépendent pas du contenu réel des fichiers JSON : des données
contrôlées sont injectées avant chaque test (`tests/conftest.py`), avec des
dates calculées par rapport au jour courant.

```
tests/
├── conftest.py      # fixtures partagées (client Flask, données de test)
├── unit/            # fonctions pures, sans client HTTP
├── integration/     # routes Flask via le client de test
├── functional/      # parcours complets d'un secrétaire
└── performance/
    └── locustfile.py
```

Commandes (environnement virtuel activé) :

```bash
# Tous les tests
pytest

# Un seul type de tests
pytest tests/unit

# Couverture dans le terminal
pytest --cov=server --cov-report=term-missing
```

Résultats actuels : **124 tests réussis** (84 unitaires, 36 d'intégration,
4 fonctionnels, soit environ 2 tests unitaires pour 1 test d'intégration ou
fonctionnel) et **100 % de couverture** de `server.py` (objectif : 60 %).

## 7. Tests de performance (Locust)

Scénario : 6 secrétaires simultanés qui affichent l'accueil, se connectent
(liste des compétitions), ouvrent la page de réservation, achètent une place
(mise à jour des points) et consultent le tableau des points.

1. Démarrer le serveur dans un premier terminal : `flask --app server run`
2. Dans un second terminal :

```bash
locust -f tests/performance/locustfile.py --headless -u 6 -r 6 -t 1m --host http://127.0.0.1:5000 --html reports/performance/locust_report.html --csv reports/performance/locust
```

Les seuils de la spécification sont vérifiés automatiquement à la fin du test
(code de sortie 1 en cas de dépassement) : liste des compétitions ≤ 5 s,
mise à jour des points ≤ 2 s. Quand un club n'a plus de points ou a atteint
12 places, l'achat est refusé (400) : c'est le comportement attendu, et le
temps de réponse de cette requête reste mesuré.

Résultat (1 minute, 6 utilisateurs) : 315 requêtes, 0 échec ; temps maximal
de 51 ms pour la liste des compétitions et de 42 ms pour la mise à jour des
points.

## 8. Rapports

Tous les rapports sont versionnés dans `reports/` (ouvrir les fichiers
`index.html` / `.html` dans un navigateur) :

| Rapport | Emplacement | Commande |
|---|---|---|
| Tests | `reports/tests/test_report.html` | `pytest --html=reports/tests/test_report.html --self-contained-html` |
| Couverture | `reports/coverage/index.html` | `pytest --cov=server --cov-report=html:reports/coverage` |
| flake8 | `reports/flake8/index.html` | `flake8 --format=html --htmldir=reports/flake8` |
| Performance | `reports/performance/locust_report.html` | voir la section 7 |

## 9. Flake8 Report

Configuration dans `.flake8` : longueur de ligne maximale de 100 caractères,
dossiers exclus : environnements virtuels, caches et `reports`.

```bash
flake8
flake8 --format=html --htmldir=reports/flake8
```

Résultat : **0 erreur**. Rapport HTML : `reports/flake8/index.html`.

## 10. Organisation Git

Convention de nommage des branches (guide de développement, règle 3) :
`<fonctionnalite|bug|amelioration>/nom-descriptif`, sans accents. Chaque
branche traite un seul sujet, suit le cycle TDD (commit `test: … (rouge)`,
puis `fix:` ou `feat:`, puis éventuellement `refactor:`) et n'est fusionnée
dans `main` (avec `--no-ff`) qu'une fois tous les tests réussis.

| Branche | Problème traité |
|---|---|
| `main` | Code fini, source de vérité |
| `amelioration/configuration-tests` | Dépendances à jour, `.gitignore` corrigé (il ignorait `tests/`), arborescence de tests, chemins JSON indépendants du dossier courant |
| `bug/email-inconnu-plantage` | Un e-mail inconnu, ou un club/une compétition introuvables, provoquaient une erreur 500 (issue #1) |
| `bug/points-insuffisants` | Un club pouvait dépenser plus de points qu'il n'en avait (issue #2) |
| `bug/limite-places-reservation` | Plus de 12 places par compétition, surréservation, saisie invalide (issues #3, #4 et #282) |
| `bug/competitions-passees` | Réservation possible dans une compétition passée (issue #5) |
| `bug/mise-a-jour-points` | Les points n'étaient pas déduits après un achat (issue #6) |
| `fonctionnalite/tableau-points` | Tableau public des points des clubs (issue #7) |
| `amelioration/performance-et-rapports` | Tests Locust, rapports et documentation |
| `QA` | Branche de revue créée depuis `main`, jamais fusionnée dans `main` |
