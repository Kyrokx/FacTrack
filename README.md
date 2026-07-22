# FacTrack

FacTrack est une application web Django de suivi des factures d’eau et d’électricité pour un foyer au Burkina Faso.  
Elle permet d’enregistrer les factures, de visualiser les montants payés et impayés, et de suivre la consommation au fil du temps.

## Fonctionnalités

- Authentification utilisateur avec connexion / déconnexion
- Tableau de bord avec :
  - total des factures
  - total des factures impayées
  - montant total impayé
  - graphiques de consommation
- Liste complète des factures
- Ajout d’une nouvelle facture
- Bascule du statut payé / impayé
- Interface responsive avec Tailwind CSS via CDN

## Technologies utilisées

- Python 3
- Django 5.2
- SQLite
- Tailwind CSS via CDN
- Chart.js via CDN
- `python-dotenv` pour la configuration via fichier `.env`

## Structure du projet

```text
factrack/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
└── bills/
    ├── models.py
    ├── views.py
    ├── forms.py
    ├── admin.py
    ├── templates/
    │   ├── base.html
    │   ├── bill/
    │   │   ├── index.html
    │   │   ├── bills_list.html
    │   │   └── add_bills.html
    │   └── registration/
    │       └── login.html
    └── migrations/
```

## Modèle de données

L’application repose sur un modèle principal : `Bill`.

### Champs du modèle `Bill`

- `type` : type de facture (`SONABEL` ou `ONEA`)
- `period` : période de la facture
- `deadline` : date limite de paiement
- `price_total` : montant total
- `previous_index` : ancien index
- `new_index` : nouvel index
- `total_consumption` : consommation totale
- `paid` : statut payé / impayé

Les factures sont triées par défaut par ordre décroissant de période.

## Pages disponibles

### 1. Connexion

- URL : `/login/`
- Permet à l’utilisateur de se connecter pour accéder à l’application.

### 2. Tableau de bord

- URL : `/`
- Affiche les statistiques générales et les graphiques de consommation.

### 3. Liste des factures

- URL : `/bills/`
- Affiche toutes les factures dans un tableau responsive.

### 4. Ajouter une facture

- URL : `/add/`
- Permet de créer une nouvelle facture via un formulaire.

### 5. Déconnexion

- URL : `/logout/`
- Action effectuée par formulaire `POST` avec protection CSRF.

## Configuration

Le projet utilise un fichier `.env` pour charger certaines variables sensibles.

### Variables d’environnement attendues

- `SECRET_KEY`
- `DEBUG`

Exemple :

```env
SECRET_KEY=your-secret-key
DEBUG=True
```

## Installation

### 1. Créer et activer un environnement virtuel

```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Appliquer les migrations

```bash
python manage.py migrate
```

### 4. Créer un superutilisateur

```bash
python manage.py createsuperuser
```

### 5. Lancer le serveur

```bash
python manage.py runserver
```

## Utilisation

1. Connectez-vous avec un compte utilisateur.
2. Ajoutez une facture via la page dédiée.
3. Consultez le tableau de bord pour suivre les montants et la consommation.
4. Ouvrez la liste des factures pour modifier leur statut payé / impayé.

## Administration Django

L’interface d’administration Django est activée pour le modèle `Bill`.

- URL : `/admin/`

## Remarques techniques

- Les templates utilisent Tailwind CSS via CDN, sans compilation locale.
- Les graphiques sont rendus avec Chart.js via CDN.
- Les pages sont pensées pour être lisibles sur mobile, tablette et desktop.
- Les actions sensibles comme la déconnexion et le basculement payé / impayé utilisent des formulaires `POST`.

## Améliorations possibles

- Ajouter des tests automatisés
- Permettre l’édition et la suppression des factures
- Ajouter des filtres par type, période ou statut
- Ajouter l’export PDF ou Excel
- Améliorer la gestion multi-utilisateurs

