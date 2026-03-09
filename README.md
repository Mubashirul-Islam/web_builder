# Project Run Instructions

## 1) Setup virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

## 2) Install dependencies

```bash
pip install -r requirements.txt
```

## 3) Create `.env`

Create a `.env` file in the project root with:

```env
SECRET_KEY=django-insecure-kogg65f+!f=zohl_bv=ff5_1^v%aqw$_!^4y=k$46*t)8gt7d)
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DATABASE_URL=postgres://myuser:mypassword@127.0.0.1:5432/mydatabase

POSTGRES_DB=mydatabase
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_PORT=5432
```

## 4) Start PostgreSQL with Docker

```bash
docker compose up -d
```

## 5) Apply migrations

```bash
python manage.py migrate
```

## 6) Restore data

```bash
python manage.py loaddata data.json
```

## 7) Run development server

```bash
python manage.py runserver
```

## 8) Superuser credentials

- Username: admin
- Password: admin

## 9) Canary testing with isolated DB and media

Use `.env.canary` to keep canary runs isolated from default local data.

```bash
docker compose --env-file .env.canary up -d
ENV_FILE=.env.canary python manage.py test
```

Canary values should use a different `DATABASE_URL` and `MEDIA_ROOT` than `.env`.
