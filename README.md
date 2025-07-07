# Coderr Backend API

This is the backend for the **Coderr** platform.

## 📌 Features

- ✅ **Offers** (CRUD, filtering, search)
- ✅ **Orders** (CRUD, role-based: Customer, Business, Admin)
- ✅ **Reviews** (CRUD, 1 review per business per customer)
- ✅ **Base Info** (platform statistics)
- ✅ **TDD** (95%+ test coverage for all endpoints)

## ⚙️ Tech Stack

- Django 4.x
- Django REST Framework
- Pytest (TDD)
- PostgreSQL (or SQLite locally)
- Pillow for ImageField support

## 🚀 Setup (local)

Clone the repository  
git clone https://github.com/<your_username>/<repo_name>.git  
cd <repo_name>

Create and activate a virtual environment  
python -m venv env  
source env/bin/activate  # macOS/Linux  
or  
env\Scripts\activate  # Windows

Install dependencies  
pip install -r requirements.txt

Apply database migrations  
python manage.py makemigrations
* **Note for 'created_at' field:** 
If you encounter a prompt asking for a one-off default value when adding the `created_at` field to `CustomUser`, type `django.utils.timezone.now` and press Enter.
python manage.py migrate

Create a superuser (optional)  
python manage.py createsuperuser

Start the server  
python manage.py runserver

## ✅ Running Tests

with pytest  
pytest

or with Django’s test runner  
python manage.py test

## 📊 API Documentation (Swagger/OpenAPI)

The API is documented using **drf-spectacular**.

Swagger UI:  
http://127.0.0.1:8000/api/schema/swagger-ui/

## 📎 Endpoints (excerpt)

| Endpoint | Description |
|----------|-------------|
| `/api/offers/` | Offers CRUD + filtering |
| `/api/orders/` | Orders CRUD, role-based |
| `/api/reviews/` | Reviews CRUD, one per business |
| `/api/base-info/` | Platform statistics |
| `/api/order-count/{business_user_id}/` | Counts active orders |
| `/api/completed-order-count/{business_user_id}/` | Counts completed orders |

## 🗂️ Environment

- Python 3.10+
- .env (optional): for DB, secrets, etc. 

## 🧑‍💻 Author

- **Daniel Krieger**
- https://github.com/NoAltF4Dan
