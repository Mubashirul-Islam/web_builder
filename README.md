# Web Builder API

Web Builder is a Django + Django REST Framework backend for:

- creating and managing websites and pages,
- uploading website/page source files,
- uploading media assets (images/videos),
- building JSON-based output for preview and live modes,
- rendering built pages from the `/render/` app.

It also includes:

- JWT authentication for protected API routes,
- real-time edit-lock events over WebSocket,
- OpenAPI schema + Swagger UI,
- dynamic server-side page content rendering from per-page API endpoints,
- optional request profiling via Silk.

## Stack

- Python 3
- Django 6.0.2
- Django REST Framework 3.16.1
- Django Channels 4.3.2 + Daphne
- PostgreSQL (Docker Compose)
- Redis (cache, channel layer, and edit-lock state)
- django-environ for environment-based settings
- djangorestframework-simplejwt for JWT auth
- drf-spectacular for API schema/docs
- django-silk for profiling (optional in development)
- Faker for development data seeding
- ruff for linting and formatting

## Project Structure

```text
config/              Django project settings and URL configuration
auth/                JWT auth endpoint routing
website/             Main app (models, serializers, views, tests, services)
render/              Page rendering endpoint for built content
media/production/    Default generated and uploaded files root
docker-compose.yaml  Local PostgreSQL and Redis services
requirements.txt     Python dependencies
```

## Routing Overview

- API base: `/api/`
- Auth base: `/auth/`
- Render base: `/render/<website_name>/<page_slug>/`
- WebSocket: `/ws/website/<website_pk>/`
- OpenAPI schema: `/api/schema/`
- Swagger UI: `/api/schema/swagger-ui/`
- Resource monitor: `/monitor/`
- Silk profiler: `/silk/`

## Data Model

### Website

- user (FK to auth.User)
- name (unique)
- description
- url (unique)
- css (.css file)
- js (.js file)
- header (.txt file)
- footer (.txt file)
- created_at, modified_at

### Page

- website (FK to Website)
- title
- slug
- meta_description
- meta_og_type
- meta_og_image
- content (.txt file)
- created_at, modified_at

### Asset

- website (FK to Website)
- file (image/video)
- type (image|video)
- alt_text
- width, height (when available)
- size
- created_at, modified_at

### Upload Path Rules

- website css/js: <website_name>/staging/static/<filename>
- website header/footer: <website_name>/staging/<filename>
- page content: <website_name>/staging/pages/<filename>
- uploaded images: <website_name>/staging/asset/images/<filename>
- uploaded videos: <website_name>/staging/asset/videos/<filename>

## Environment Configuration

Settings are loaded from .env in project root by default.
Use ENV_FILE to switch to another environment file:

```bash
ENV_FILE=.env.canary python manage.py runserver
```

### Supported Variables

```env
SECRET_KEY=django-insecure-change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DATABASE_URL=postgres://myuser:mypassword@127.0.0.1:5432/mydatabase
REDIS_URL=redis://127.0.0.1:6379/
REDIS_PORT=6379

POSTGRES_DB=mydatabase
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_PORT=5432

# Optional
MEDIA_ROOT=/absolute/path/to/media
```

If MEDIA_ROOT is not set, default is BASE_DIR/media/production.

Redis usage:

- Redis DB `1`: Django cache + edit-lock state
- Redis DB `2`: Channels layer (WebSocket pub/sub)

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

3. Ensure .env exists in project root.

4. Start PostgreSQL and Redis.

```bash
docker compose -p dev up -d
```

5. Run migrations.

```bash
python manage.py migrate
```

6. Optional: seed sample data.

```bash
python manage.py seed_db
```

7. Start the API server.

```bash
python manage.py runserver
```

If you want to run with Daphne explicitly:

```bash
daphne config.asgi:application
```

API base URL: http://127.0.0.1:8000/api/

## Authentication

This project uses JWT auth via SimpleJWT.

Obtain token pair:

```bash
curl -X POST http://127.0.0.1:8000/auth/token/ \
	-H "Content-Type: application/json" \
	-d '{"username":"<username>","password":"<password>"}'
```

Refresh access token:

```bash
curl -X POST http://127.0.0.1:8000/auth/token/refresh/ \
	-H "Content-Type: application/json" \
	-d '{"refresh":"<refresh_token>"}'
```

Use access token on protected routes:

```bash
Authorization: Bearer <access_token>
```

Permission summary:

- Public read access: website/page list and detail (`GET`)
- Auth required: create/update/delete websites/pages
- Auth required: build/upload/edit-lock routes
- Public access: render endpoint and diagnostics/docs routes

## API Endpoints

Base prefix: /api/

### Websites

- GET /api/websites/
- POST /api/websites/ (multipart/form-data)
- GET /api/websites/<id>/
- PUT /api/websites/<id>/ (multipart/form-data)
- PATCH /api/websites/<id>/
- DELETE /api/websites/<id>/
- POST /api/websites/<id>/build/?mode=preview|live
- POST /api/websites/<id>/upload/ (multipart/form-data)
- GET /api/websites/<id>/edit/
- POST /api/websites/<id>/edit/refresh/
- POST /api/websites/<id>/edit/save/
- POST /api/websites/<id>/edit/exit/

List query parameters:

- search=<name_fragment>
- ordering=created_at|modified_at (prefix with - for descending)
- limit=<n>&offset=<n>

### Pages

- GET /api/pages/
- POST /api/pages/ (multipart/form-data)
- GET /api/pages/<id>/
- PUT /api/pages/<id>/ (multipart/form-data)
- PATCH /api/pages/<id>/
- DELETE /api/pages/<id>/

List query parameters:

- search=<title_fragment>
- ordering=created_at|modified_at (prefix with - for descending)
- limit=<n>&offset=<n>

### Auth

- POST /auth/token/
- POST /auth/token/refresh/

### Diagnostics & Docs

- GET /monitor/
- GET /api/schema/
- GET /api/schema/swagger-ui/
- GET /silk/

### Render

- GET /render/<website_name>/<page_slug>/

Render behavior:

- Reads build payloads from `<website_name>/live/pages/<page_slug>.json`.
- Merges shared layout payloads from `<website_name>/live/header.json` and `<website_name>/live/footer.json`.
- If `dynamic_endpoint` is set for the page, fetches JSON data and renders page content as a Django template with `dynamic_data` context.

### WebSocket

- WS /ws/website/<website_pk>/
- Emits lock events:
	- lock_acquired with user_id and website_pk
	- lock_released with website_pk

### Notes

- Build mode is required and must be preview or live.
- A website must have at least one page before build.
- Asset upload expects two list fields with matching lengths: files and alt_texts.
- Asset upload supports only image/* and video/* content types.
- Edit-lock HTTP endpoints infer user from authenticated request (`request.user.id`).
- Lock TTL is 5 minutes and can be refreshed with the refresh endpoint.
- WebSocket lock events are emitted as `lock_acquired` and `lock_released`.
- Render endpoint serves from the `live` build output.
- Page content can use template expressions like `{{ dynamic_data.some_key }}` when `dynamic_endpoint` is configured.

## Build Output

Build artifacts are generated under:

- <MEDIA_ROOT>/<website_name>/preview/
- <MEDIA_ROOT>/<website_name>/live/

Each build writes:

- pages/<page_slug>.json
- header.json
- footer.json
- static/style.css
- static/script.js
- asset/images/<filename>
- asset/videos/<filename>

Per-page JSON payload includes:

- title and metadata (`meta_description`, `meta_og_type`, `meta_og_image`)
- `css_url` and `js_url`
- `content`
- `dynamic_endpoint`

## Management Commands

- python manage.py seed_db
- python manage.py clear_db

## API Schema

OpenAPI schema is generated by drf-spectacular:

- Schema JSON: `/api/schema/`
- Swagger UI: `/api/schema/swagger-ui/`

## Testing

Run all tests:

```bash
python manage.py test
```

Run a specific module:

```bash
python manage.py test website.tests.test_website_build_api
```

For isolated runs with separate env/media/database:

```bash
docker compose -p canary --env-file .env.canary up -d
ENV_FILE=.env.canary python manage.py test
```

## Linting and Formatting

```bash
ruff check .
ruff format
```
