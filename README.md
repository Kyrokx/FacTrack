# FacTrack

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django)
![DRF](https://img.shields.io/badge/DRF-3.x-red?logo=django)
![Licence](https://img.shields.io/badge/Licence-MIT-green)
![Déploiement](https://img.shields.io/badge/Deploy-Render-46E3B7?logo=render)

**FacTrack** est une application SaaS Django multi-tenant de suivi des factures utilitaires au Burkina Faso, avec un focus sur :

- l'électricité SONABEL ⚡
- l'eau ONEA 💧

L'objectif est simple : centraliser les factures du foyer ou de l'organisation, suivre les paiements, comparer les consommations et exporter les données en CSV ou PDF en quelques clics.

> 📸 *Capture à ajouter*

## Démo en ligne

- 🌍 Site live : https://factrack-odmv.onrender.com
- 🔗 Dépôt GitHub : https://github.com/Kyrokx/FacTrack

## Auteur

- **Tsar Ruben**
- GitHub : [Kyrokx](https://github.com/Kyrokx)

---

## Fonctionnalités

### Multi-tenant
- 🏠 Création d'organisations (foyers / entreprises)
- 🔗 Invitation par code unique
- 👥 Gestion des membres avec rôles (owner / admin / member)
- 🔒 Isolation des données par organisation

### Tableau de bord
- 📊 3 cartes statistiques principales
- 📈 Statistiques SONABEL et ONEA séparées
- 🗓️ Filtre par année
- 📉 5 graphiques Chart.js
  - courbes de consommation SONABEL et ONEA
  - barres groupées des dépenses mensuelles
  - donut des factures payées / impayées
  - comparaison annuelle

### Gestion des factures
- 🧾 Liste paginée (15 éléments par page) avec recherche, filtre et tri
- ✏️ CRUD complet (ajouter, modifier, supprimer, basculer statut)
- 📤 Export CSV
- 📄 Export PDF avec ReportLab

### API REST
- 🔑 Authentification JWT (SimpleJWT)
- 📖 Documentation Swagger (`/api/docs/`) sécurisée
- Versioning via `/api/v1/`

---

## Stack Technique

| Technologie | Rôle |
|---|---|
| Python 3.11 | Langage principal |
| Django 5.2 | Framework backend full-stack |
| Django REST Framework | API REST |
| SimpleJWT | Authentification JWT |
| drf-spectacular | Documentation OpenAPI / Swagger |
| PostgreSQL | Base de données |
| Tailwind CSS CDN | UI responsive |
| Chart.js CDN | Graphiques interactifs |
| Lucide Icons CDN | Icônes |
| ReportLab | Génération PDF |
| Gunicorn | Serveur WSGI en production |
| WhiteNoise | Gestion des fichiers statiques |
| `python-decouple` | Gestion des variables d'environnement |
| `dj-database-url` | Configuration base de données prod |

---

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
├── accounts/
│   ├── views.py        # login, logout, signup
│   └── urls.py
├── bills/
│   ├── models.py
│   ├── views.py
│   ├── services.py     # logique métier
│   ├── utils.py
│   ├── forms.py
│   └── urls.py
├── organizations/
│   ├── models.py       # Organization, Membership
│   ├── views.py
│   ├── mixins.py
│   ├── forms.py
│   └── urls.py
├── api/
│   └── v1/
│       ├── auth/       # register, login, logout, me, token/refresh
│       ├── bills/      # CRUD factures
│       └── organizations/ # CRUD organisations + membres
└── templates/
    ├── base.html
    ├── bills/
    ├── organizations/
    └── registration/
```

---

## Modèles de données

### Bill

| Champ | Type | Description |
|---|---|---|
| `type` | `CharField` | `SONABEL` ou `ONEA` |
| `period` | `DateField` | Période de facturation |
| `deadline` | `DateField` | Date limite de paiement |
| `price_total` | `DecimalField` | Montant total en FCFA |
| `previous_index` | `IntegerField` | Ancien index |
| `new_index` | `IntegerField` | Nouvel index |
| `total_consumption` | `IntegerField` | Consommation en `kWh` ou `m³` |
| `paid` | `BooleanField` | Statut payé / impayé |
| `organization` | `ForeignKey` | Organisation propriétaire |

### Organization

| Champ | Type | Description |
|---|---|---|
| `uid` | `UUIDField` | Identifiant unique |
| `name` | `CharField` | Nom de l'organisation |
| `invite_code` | `CharField` | Code d'invitation unique |
| `created_at` | `DateTimeField` | Date de création |

### Membership

| Champ | Type | Description |
|---|---|---|
| `user` | `OneToOneField` | Utilisateur Django |
| `organization` | `ForeignKey` | Organisation |
| `role` | `CharField` | `owner` / `admin` / `member` |
| `joined_at` | `DateTimeField` | Date d'adhésion |

---

## API REST

### Auth — `/api/v1/auth/`

| Méthode | Route | Description |
|---|---|---|
| POST | `/register/` | Créer un compte |
| POST | `/login/` | Connexion (retourne access + refresh) |
| POST | `/logout/` | Déconnexion (blacklist du refresh token) |
| GET | `/me/` | Infos de l'utilisateur connecté |
| POST | `/token/refresh/` | Rafraîchir le token d'accès |

### Organizations — `/api/v1/organizations/`

| Méthode | Route | Description |
|---|---|---|
| GET | `/` | Détail de l'organisation |
| POST | `/create/` | Créer une organisation |
| POST | `/join/` | Rejoindre via code d'invitation |
| POST | `/leave/` | Quitter l'organisation |
| GET | `/members/` | Liste des membres |
| PATCH | `/members/<id>/promote/` | Promouvoir / rétrograder un membre |
| DELETE | `/members/<id>/remove/` | Supprimer un membre |

### Bills — `/api/v1/bills/`

| Méthode | Route | Description |
|---|---|---|
| GET | `/` | Liste des factures |
| POST | `/create/` | Créer une facture |
| GET | `/<id>/` | Détail d'une facture |
| PATCH | `/<id>/update/` | Modifier une facture |
| DELETE | `/<id>/delete/` | Supprimer une facture |
| POST | `/<id>/toggle/` | Basculer payé / impayé |

> La documentation complète est accessible sur `/api/docs/` (requiert un compte admin).

---

## Routes Web principales

| Route | Description |
|---|---|
| `/` | Tableau de bord |
| `/login/` | Connexion |
| `/signup/` | Inscription |
| `/logout/` | Déconnexion |
| `/setup/` | Configuration organisation |
| `/create/` | Créer une organisation |
| `/join/` | Rejoindre une organisation |
| `/add/` | Ajouter une facture |
| `/bills/` | Liste des factures |
| `/organization/settings/` | Paramètres de l'organisation |
| `/export/csv/` | Export CSV |
| `/export/pdf/` | Export PDF |

---

## Variables d'environnement

| Variable | Utilité |
|---|---|
| `DEBUG` | Mode développement / production |
| `SECRET_KEY` | Clé secrète Django |
| `DATABASE_URL` | URL PostgreSQL de production |
| `ALLOWED_HOSTS` | Hôtes autorisés |
| `DJANGO_SUPERUSER_PASSWORD` | Mot de passe du superutilisateur |

### Exemple `.env`

```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=postgresql://user:password@host:5432/dbname
DJANGO_SUPERUSER_PASSWORD=super-secret-password
```

---

## Installation locale

```bash
# 1. Cloner le dépôt
git clone https://github.com/Kyrokx/FacTrack.git
cd FacTrack

# 2. Créer et activer un environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS / Linux

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer le fichier .env

# 5. Appliquer les migrations
python manage.py migrate

# 6. Créer un superutilisateur
python manage.py createsuperuser

# 7. Lancer le serveur
python manage.py runserver
```

---

## Déploiement sur Render

### Release Command

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

### Start Command

```bash
gunicorn config.wsgi:application
```

### Variables à configurer sur Render

- `DEBUG=False`
- `SECRET_KEY`
- `ALLOWED_HOSTS`
- `DATABASE_URL`
- `DJANGO_SUPERUSER_PASSWORD`

---

## Roadmap

- [x] Application Django full-stack
- [x] Multi-tenant avec organisations et rôles
- [x] API REST avec JWT
- [x] Documentation Swagger
- [ ] Application mobile Flutter
- [ ] Notifications de deadline
- [ ] Prédiction de consommation avec ML
- [ ] Version PWA

---

## Licence

Ce projet est distribué sous licence **MIT**.
