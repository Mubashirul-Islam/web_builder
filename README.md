# Web Builder API

`web_builder` is a Django + Django REST Framework backend for managing websites and their pages, including uploaded asset files (`.css`, `.js`, `.html`).

## Stack

- Python 3
- Django 6.0.2
- Django REST Framework 3.16.1
- PostgreSQL (via Docker Compose)
- `django-environ` for environment-based configuration
- `ruff` for linting

## Project Structure

```text
config/              Django project config (settings, urls, wsgi/asgi)
website/             Main app (models, serializers, views, API tests)
media/               Default uploaded files root
media_canary/        Canary uploaded files root
docker-compose.yaml  PostgreSQL service
requirements.txt     Python dependencies
```

## Data Model

### `Website`

- `user` (FK to `auth.User`, required)
- `name` (unique, required)
- `description` (optional)
- `url` (unique, required)
- `css` (`.css`, required)
- `js` (`.js`, required)
- `header` (`.html`, required)
- `footer` (`.html`, required)
- `created_at`, `modified_at`

### `Page`

- `website` (FK to `Website`, required)
- `title` (required)
- `slug` (required)
- `content` (`.html`, required)
- `created_at`, `modified_at`

Uploaded files are stored under folders derived from the website name when available.

## Environment Configuration

The app reads environment variables from `.env` by default.
You can switch env files with `ENV_FILE`, for example: `ENV_FILE=.env.canary`.

### Required / Supported Variables

```env
SECRET_KEY=django-insecure-change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DATABASE_URL=postgres://myuser:mypassword@127.0.0.1:5432/mydatabase

POSTGRES_DB=mydatabase
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_PORT=5432

# Optional
MEDIA_ROOT=/absolute/path/to/media
```

## Local Setup

1. Create and activate a virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Ensure `.env` exists in project root (see configuration above).

4. Start PostgreSQL.

```bash
docker compose -p dev up -d
```

5. Run migrations.

```bash
python manage.py migrate
```

6. Start the development server.

```bash
python manage.py runserver
```

API base URL (local): `http://127.0.0.1:8000/api/`

## Canary / Isolated Test Setup

Use `.env.canary` with a separate database and media path to avoid polluting local dev data.

```bash
docker compose -p canary --env-file .env.canary up -d
ENV_FILE=.env.canary python manage.py test
```

You can also run the app in canary mode:

```bash
ENV_FILE=.env.canary python manage.py runserver
```

## API Endpoints

Base prefix: `/api/`

### Websites

- `GET /api/websites/` list websites
- `POST /api/websites/` create website (multipart form)
- `GET /api/websites/<id>/` retrieve website
- `PUT /api/websites/<id>/` full update (multipart form)
- `PATCH /api/websites/<id>/` partial update
- `DELETE /api/websites/<id>/` delete

Query params on list endpoint:

- `search=<name-fragment>`
- `ordering=created_at|modified_at` (prefix with `-` for descending)
- `limit=<n>&offset=<n>` (limit/offset pagination)

### Pages

- `GET /api/pages/` list pages
- `POST /api/pages/` create page (multipart form)
- `GET /api/pages/<id>/` retrieve page
- `PUT /api/pages/<id>/` full update (multipart form)
- `PATCH /api/pages/<id>/` partial update
- `DELETE /api/pages/<id>/` delete

Query params on list endpoint:

- `search=<title-fragment>`
- `ordering=created_at|modified_at` (prefix with `-` for descending)
- `limit=<n>&offset=<n>` (limit/offset pagination)

## Testing

Run all tests:

```bash
python manage.py test
```
