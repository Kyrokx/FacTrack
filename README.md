# FacTrack

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django)
![Licence](https://img.shields.io/badge/Licence-MIT-green)
![Déploiement](https://img.shields.io/badge/Deploy-Render-46E3B7?logo=render)

**FacTrack** est une application Django de suivi des factures utilitaires pour les familles au Burkina Faso, avec un focus sur :

- l'électricité SONABEL ⚡
- l'eau ONEA 💧

L'objectif est simple : centraliser les factures du foyer, suivre les paiements, comparer les consommations et exporter les données en CSV ou PDF en quelques clics.

> 📸 *Capture à ajouter*

## Démo en ligne

- 🌍 Site live : https://factrack-odmv.onrender.com
- 🔗 Dépôt GitHub : https://github.com/Kyrokx/FacTrack

## Auteur

- **Tsar Ruben**
- GitHub : [Kyrokx](https://github.com/Kyrokx)

## Fonctionnalités

- 🔐 Authentification avec login/logout
- 📊 Tableau de bord complet
  - 3 cartes statistiques principales
  - statistiques SONABEL et ONEA
  - filtre par année
  - 5 graphiques Chart.js
    - courbes de consommation SONABEL et ONEA
    - barres groupées des dépenses mensuelles
    - donut des factures payées / impayées
    - comparaison annuelle
- 🧾 Liste des factures avec
  - pagination 15 éléments par page
  - recherche textuelle
  - filtre par type
  - tri par colonne
- ✏️ CRUD complet
  - ajouter une facture
  - modifier une facture
  - supprimer une facture
  - changer le statut payé / impayé
- 📤 Export CSV
- 📄 Export PDF avec ReportLab
- 🛡️ Protection CSRF sur les actions POST
- 🔎 `get_object_or_404` pour les objets unitaires
- 🎨 Interface responsive avec Tailwind CSS CDN
- 🧩 Icônes Lucide via CDN
- 🚀 Déploiement Render avec CI/CD automatique sur `main`

> 📸 *Capture à ajouter*

## Stack Technique

| Technologie | Rôle |
|---|---|
| Python 3.11 | Langage principal |
| Django 5.2 | Framework backend full-stack |
| PostgreSQL | Base de données |
| Tailwind CSS CDN | UI responsive |
| Chart.js CDN | Graphiques interactifs |
| Lucide Icons CDN | Icônes |
| ReportLab | Génération PDF |
| Gunicorn | Serveur WSGI en production |
| WhiteNoise | Gestion des fichiers statiques |
| `python-decouple` | Gestion des variables d'environnement |
| `dj-database-url` | Configuration base de données prod |

## Structure du projet

```text
factrack/
├── manage.py
├── requirements.txt
├── Procfile
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── bills/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py
│   ├── migrations/
│   └── templates/
│       ├── base.html
│       ├── bill/
│       │   ├── index.html
│       │   ├── bills_list.html
│       │   ├── add_bills.html
│       │   └── edit_bill.html
│       └── registration/
│           └── login.html
└── templates/
    ├── 404.html
    └── 500.html
```

## Modèle de données

L'application repose principalement sur le modèle `Bill`.

| Champ | Type | Description |
|---|---|---|
| `type` | `CharField` | Type de facture : `SONABEL` ou `ONEA` |
| `period` | `DateField` | Période de facturation |
| `deadline` | `DateField` | Date limite de paiement |
| `price_total` | `DecimalField` | Montant total en FCFA |
| `previous_index` | `IntegerField` | Ancien index |
| `new_index` | `IntegerField` | Nouvel index |
| `total_consumption` | `IntegerField` | Consommation totale en `kWh` ou `m³` |
| `paid` | `BooleanField` | Statut payé / impayé |

### Logique métier

- SONABEL utilise les consommations en `kWh`
- ONEA utilise les consommations en `m³`
- les factures sont ordonnées par période
- les exports et filtres s’appliquent côté serveur

## Routes principales

| Route | Nom | Description |
|---|---|---|
| `/` | `home` | Tableau de bord |
| `/login/` | `login` | Connexion |
| `/logout/` | `logout` | Déconnexion |
| `/add/` | `add_bills` | Ajouter une facture |
| `/bills/` | `bills_list` | Liste paginée et filtrable |
| `/edit/<id>/` | `edit_bill` | Modifier une facture |
| `/delete/<id>/` | `delete_bill` | Supprimer une facture |
| `/toggle/<id>/` | `toggle_bill` | Basculer payé / impayé |
| `/export/csv/` | `export_csv` | Export CSV |
| `/export/pdf/` | `export_pdf` | Export PDF |
| `/admin/` | `admin` | Administration Django |

> 📸 *Capture à ajouter*

## Variables d’environnement

Le projet utilise les variables suivantes :

| Variable | Utilité |
|---|---|
| `DEBUG` | Mode développement / production |
| `SECRET_KEY` | Clé secrète Django |
| `DB_NAME` | Nom de la base PostgreSQL |
| `DB_USER` | Utilisateur PostgreSQL |
| `DB_PASSWORD` | Mot de passe PostgreSQL |
| `DB_HOST` | Hôte PostgreSQL |
| `DB_PORT` | Port PostgreSQL |
| `DATABASE_URL` | URL PostgreSQL de production |
| `DJANGO_SUPERUSER_PASSWORD` | Mot de passe du superutilisateur |
| `ALLOWED_HOSTS` | Hôtes autorisés |

### Exemple de fichier `.env`

```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost
DB_NAME=factrack
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DATABASE_URL=postgresql://user:password@host:5432/dbname
DJANGO_SUPERUSER_PASSWORD=super-secret-password
```

## Installation locale

### 1. Cloner le dépôt

```bash
git clone https://github.com/Kyrokx/FacTrack.git
cd FacTrack
```

### 2. Créer et activer un environnement virtuel

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer le fichier `.env`

Créez un fichier `.env` à la racine du projet et renseignez les variables nécessaires.

### 5. Appliquer les migrations

```bash
python manage.py migrate
```

### 6. Créer un superutilisateur

```bash
python manage.py createsuperuser
```

### 7. Lancer le serveur de développement

```bash
python manage.py runserver
```

L’application sera accessible sur :

```text
http://127.0.0.1:8000/
```

## Déploiement sur Render

FacTrack est déployé sur **Render** avec auto-déploiement depuis la branche `main`.

### Commande de build

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

### Commande de démarrage

```bash
gunicorn config.wsgi:application
```

### Étapes de déploiement

1. Créer une nouvelle application Web sur Render
2. Connecter le dépôt GitHub `Kyrokx/FacTrack`
3. Configurer une base PostgreSQL Render dans la même région, idéalement **Frankfurt**
4. Ajouter les variables d’environnement dans le dashboard Render
5. Définir la commande de build
6. Définir la commande de démarrage
7. Activer le déploiement automatique sur push vers `main`

### Variables à configurer sur Render

- `DEBUG=False`
- `SECRET_KEY`
- `ALLOWED_HOSTS`
- `DATABASE_URL`
- `DJANGO_SUPERUSER_PASSWORD`

> 📸 *Capture à ajouter*

## CI/CD

Le projet est configuré pour un flux simple :

- chaque push sur `main` déclenche un nouveau déploiement Render
- les fichiers statiques sont collectés automatiquement
- la base de données est migrée lors du build

## Utilisation

1. Se connecter avec un compte Django
2. Ajouter une facture SONABEL ou ONEA
3. Consulter les statistiques du tableau de bord
4. Filtrer les factures par année
5. Rechercher et trier la liste des factures
6. Modifier, supprimer ou basculer le statut d’une facture
7. Exporter les données en CSV ou PDF

## Roadmap

- 🔌 API REST avec Django REST Framework
- 📱 Application mobile Flutter
- 🧱 Mode SaaS multi-tenant
- 🤖 Prédiction de consommation avec ML
- 🔔 Alertes de paiement
- 📲 Version PWA

## Contribution

Les contributions sont les bienvenues.

1. Fork le projet
2. Créer une branche de fonctionnalité
3. Commiter les changements
4. Ouvrir une Pull Request

## Licence

Ce projet est distribué sous licence **MIT**.

