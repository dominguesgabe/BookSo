# BookSo 📚🌻

Bookstore api using django

---

## Development

First of all. Be Sure to clone the **.env.example** and fill it with real data

1. Build docker environment

```
docker compose up --build
```

2. Run the migrations

```
docker compose run django-web python manage.py migrate
```

3. Create your development user

```
docker compose run django-web python manage.py createsuperuser
```

### Django Admin

The admin will be available at [localhost:8000/](http://localhost:8000/admin)
