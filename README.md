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

## 3) Start PostgreSQL with Docker

```bash
docker compose up -d
```

## 4) Apply migrations

```bash
python manage.py migrate
```

## 5) Restore data

```bash
python manage.py loaddata data.json
```

## 6) Run development server

```bash
python manage.py runserver
```

## 7) Superuser credentials

- Username: admin
- Password: admin

