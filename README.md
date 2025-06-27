# Coderr Backend API

Dies ist das Backend für die Plattform **Coderr**.

## 📌 Features

- ✅ **Offers** (CRUD, Filter, Suche)
- ✅ **Orders** (CRUD, rollenbasiert: Customer, Business, Admin)
- ✅ **Reviews** (CRUD, 1 Review pro Business pro Customer)
- ✅ **Base Info** (Plattformstatistik)
- ✅ **TDD** (Tests für alle Endpunkte)

## ⚙️ Tech Stack

- Django 4.x
- Django REST Framework
- Pytest (TDD)
- PostgreSQL (oder SQLite lokal)
- Pillow für ImageField

## 🚀 Setup (local)

Repo klonen  
git clone https://github.com/<dein_username>/<repo_name>.git  
cd <repo_name>

Virtuelle Umgebung erstellen & aktivieren  
python -m venv env  
source env/bin/activate  # macOS/Linux  
oder  
env\Scripts\activate  # Windows

Abhängigkeiten installieren  
pip install -r requirements.txt

Datenbank Migrationen durchführen  
python manage.py migrate

Superuser erstellen (optional)  
python manage.py createsuperuser

Server starten  
python manage.py runserver

## ✅ Tests ausführen

mit pytest  
pytest

oder Django-Standard  
python manage.py test

## 📊 API Dokumentation (Swagger/OpenAPI)

Die API ist dokumentiert mit **drf-spectacular**.

Swagger-UI:  
http://127.0.0.1:8000/api/schema/swagger-ui/

## 📎 Endpunkte (Auszug)

| Endpoint | Beschreibung |
|----------|---------------|
| `/api/offers/` | Offers CRUD + Filter |
| `/api/orders/` | Orders CRUD, rollenbasiert |
| `/api/reviews/` | Reviews CRUD, 1 pro Business |
| `/api/base-info/` | Plattformstatistik |
| `/api/order-count/{business_user_id}/` | Zählt laufende Bestellungen |
| `/api/completed-order-count/{business_user_id}/` | Zählt abgeschlossene Bestellungen |

## 🗂️ Environment

- Python 3.10+
- `.env` (optional): für DB, Secrets, usw.

## 🧑‍💻 Author

- **Daniel Krieger**
- https://github.com/NoAltF4Dan
