# FacTrack

FacTrack is a Django web app for tracking household utility bills, with a focus on SONABEL and ONEA invoices.

The app lets you:

- add and manage bills
- track paid and unpaid status
- compare SONABEL and ONEA consumption over time
- view separate bill lists for SONABEL and ONEA
- sort each bill type independently in the bills page

## Features

- Authentication with login and logout
- Dashboard with:
  - total bill amount
  - unpaid bill count
  - unpaid amount total
  - consumption charts for SONABEL and ONEA
  - recent SONABEL and ONEA bills
- Bills list split into two sections:
  - SONABEL table
  - ONEA table
- Independent sorting for each bill type
- Add bill form
- Toggle paid / unpaid status
- Responsive UI built with Tailwind CSS via CDN
- Charts powered by Chart.js via CDN

## Tech Stack

- Python 3
- Django 5.2
- PostgreSQL in development when `DEBUG=True`
- `dj-database-url` for production database config
- `python-dotenv` and `python-decouple` for environment variables
- WhiteNoise for static file serving
- Tailwind CSS via CDN
- Chart.js via CDN

## Project Structure

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
└── bills/
    ├── admin.py
    ├── apps.py
    ├── forms.py
    ├── models.py
    ├── tests.py
    ├── views.py
    ├── migrations/
    └── templates/
        ├── base.html
        ├── bill/
        │   ├── index.html
        │   ├── bills_list.html
        │   └── add_bills.html
        └── registration/
            └── login.html
```

## Data Model

The app currently uses one model: `Bill`.

### `Bill`

- `type`: bill type, either `SONABEL` or `ONEA`
- `period`: billing period
- `deadline`: payment deadline
- `price_total`: total amount
- `previous_index`: previous meter index
- `new_index`: new meter index
- `total_consumption`: total consumption
- `paid`: paid/unpaid flag

The model default ordering is descending by `period`.

## Main Pages

### Dashboard

- URL: `/`
- Template: `bill/index.html`
- Shows totals, charts, and recent bills for each bill type

### Bills List

- URL: `/bills/`
- Template: `bill/bills_list.html`
- Shows SONABEL and ONEA in separate tables
- Each table has its own sort controls

### Add Bill

- URL: `/add/`
- Template: `bill/add_bills.html`
- Creates a new bill through a form

### Login

- URL: `/login/`
- Template: `registration/login.html`

### Logout

- URL: `/logout/`
- Uses a POST request

### Admin

- URL: `/admin/`
- Django admin is enabled for `Bill`

## URL Routes

Defined in `config/urls.py`:

- `/login/` -> Django login view
- `/logout/` -> Django logout view
- `/` -> dashboard
- `/add/` -> add bill
- `/bills/` -> bills list
- `/toggle/<int:id>/` -> toggle paid status
- `/admin/` -> Django admin

## Environment Variables

The project expects these environment variables:

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `DATABASE_URL` for production

Example `.env`:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DB_NAME=factrack
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

## Local Setup

1. Create a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Apply migrations:

```bash
python manage.py migrate
```

4. Create a superuser:

```bash
python manage.py createsuperuser
```

5. Run the development server:

```bash
python manage.py runserver
```

## Usage

1. Log in with a Django user account.
2. Add SONABEL or ONEA bills from the add page.
3. Open the dashboard to see totals and charts.
4. Open the bills page to review SONABEL and ONEA separately.
5. Use the toggle action to switch a bill between paid and unpaid.

## Implementation Notes

- Templates use Tailwind via CDN, so no local frontend build step is required.
- Dashboard charts use Chart.js via CDN.
- The bills list is split into two sections:
  - SONABEL on one side
  - ONEA on the other
- Sorting is handled separately for each bill type through query parameters.
- Authentication-protected views are decorated with `login_required`.
- `toggle_bill` flips the `paid` boolean and redirects back to the bills list.

## Notes on Deployment

- `WhiteNoise` is already configured for static files.
- Database configuration switches by `DEBUG`:
  - local development uses PostgreSQL settings from the environment
  - production uses `DATABASE_URL`

## Possible Next Improvements

- Add edit and delete actions for bills
- Add filters by paid status, date range, or amount
- Add test coverage for views and forms
- Add export to PDF or Excel
- Add pagination for the bills list

