# Web Builder API

`web_builder` is a Django + Django REST Framework backend for creating websites and pages, managing uploaded assets (`.css`, `.js`, `.txt`), and building static output for `preview` and `live` modes.

## Stack

- Python 3
- Django 6.0.2
- Django REST Framework 3.16.1
- PostgreSQL (Docker Compose)
- `django-environ` for `.env`-based settings
- `Faker` for seeding development data
- `ruff` for linting

## Project Structure

```text
config/              Django project config (settings, urls, wsgi/asgi)
website/             Main app (models, serializers, views, tests, services)
media/               Default upload root
media_canary/        Canary upload root
storage/             Built static website output (preview/live)
docker-compose.yaml  PostgreSQL service
requirements.txt     Python dependencies
```

## Data Model

### `Website`

- `user` (FK to `auth.User`, required)
- `name` (unique, required)
- `description` (optional, defaults to empty)
- `url` (unique, required)
- `css` (`.css`, required)
- `js` (`.js`, required)
- `header` (`.txt`, required)
- `footer` (`.txt`, required)
- `created_at`, `modified_at`

### `Page`

- `website` (FK to `Website`, required)
- `title` (required)
- `slug` (required)
- `meta_description` (optional text)
- `meta_og_type` (optional text)
- `meta_og_image` (optional URL)
- `content` (`.txt`, required)
- `created_at`, `modified_at`

Uploaded file paths:

- Website assets: `<website_name>/<filename>`
- Page assets: `<website_name>/<page_slug>/<filename>`

## Environment Configuration

By default, settings are loaded from `.env` in project root. Override the file with `ENV_FILE`:

```bash
ENV_FILE=.env.canary python manage.py runserver
```

### Supported Variables

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

3. Ensure `.env` exists in project root.

4. Start PostgreSQL.

```bash
docker compose -p dev up -d
```

5. Run migrations.

```bash
python manage.py migrate
```

6. Optional: seed development data.

```bash
python manage.py seed_db
```

7. Start the API server.

```bash
python manage.py runserver
```

Local API base URL: `http://127.0.0.1:8000/api/`

## Canary / Isolated Test Setup

Use a separate env file and database/media roots to isolate test data:

```bash
docker compose -p canary --env-file .env.canary up -d
ENV_FILE=.env.canary python manage.py test
```

## API Endpoints

Base prefix: `/api/`

### Websites

- `GET /api/websites/` list websites
- `POST /api/websites/` create website (`multipart/form-data`)
- `GET /api/websites/<id>/` retrieve website
- `PUT /api/websites/<id>/` full update (`multipart/form-data`)
- `PATCH /api/websites/<id>/` partial update
- `DELETE /api/websites/<id>/` delete
- `POST /api/websites/<id>/build/?mode=preview|live` build website output

Query params on `GET /api/websites/`:

- `search=<name-fragment>`
- `ordering=created_at|modified_at` (prefix with `-` for descending)
- `limit=<n>&offset=<n>` (enables limit/offset pagination)

### Pages

- `GET /api/pages/` list pages
- `POST /api/pages/` create page (`multipart/form-data`)
- `GET /api/pages/<id>/` retrieve page
- `PUT /api/pages/<id>/` full update (`multipart/form-data`)
- `PATCH /api/pages/<id>/` partial update
- `DELETE /api/pages/<id>/` delete
- `GET /api/websites/<website_id>/pages/` list pages for a website
- `POST /api/websites/<website_id>/pages/` create page for a website

Query params on `GET /api/pages/`:

- `search=<title-fragment>`
- `ordering=created_at|modified_at` (prefix with `-` for descending)
- `limit=<n>&offset=<n>` (enables limit/offset pagination)

## Build Output

Website builds generate static output under:

- `storage/preview/<website_name>/`
- `storage/live/<website_name>/`

Each build writes:

- `<page_slug>.html` for each page
- `static/style.css`
- `static/script.js`

## Management Commands

- `python manage.py seed_db`: create sample users, websites, and pages
- `python manage.py clear_db`: remove users, websites, and pages

## Testing

Run all tests:

```bash
python manage.py test
```

Run a specific module:

```bash
python manage.py test website.tests.test_website_build_api
```

## Linting

```bash
ruff check .
```
