# BookSo 📚🌻

Bookstore api using django

---

## Development

First of all. Be Sure to clone the **.env.example**, rename it to **.env** and fill it with real data

1. Build docker database

   ```
   docker compose up --build
   ```

2. create and activate a _venv_ using

   ```
   python -m venv venv
   ```

   ```
   source env/bin/activate
   ```

3. Install project dependencies

   ```
   pip install -r requirements.txt
   ```

4. Run the migrations

   ```
   python manage.py migrate
   ```

5. Seed the database

   ```
   python manage.py loaddata fixtures/*
   ```

6. Create your development user

   ```
   python manage.py createsuperuser
   ```

7. Execute the dev server with

   ```
   python manage.py runserver
   ```

---

### Django Admin

The admin will be available at [localhost:8000/](http://localhost:8000/admin/)

### Rest API

The api will be available at [localhost:8000/bff/](http://localhost:8000/bff/)

---

## Modeling and Features

Access the [ER Diagram](https://dbdiagram.io/d/BookSo-68913b30dd90d1786567c155)
