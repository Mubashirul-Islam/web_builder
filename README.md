# Web Builder API

Web Builder is a Django + Django REST Framework backend for:

- creating and managing websites and pages,
- uploading website/page source files,
- uploading media assets (images/videos),
- building static output for preview and live modes.

## Stack

- Python 3
- Django 6.0.2
- Django REST Framework 3.16.1
- PostgreSQL (Docker Compose)
- django-environ for environment-based settings
- Faker for development data seeding
- ruff for linting and formatting

## Project Structure

```text
config/              Django project settings and URL configuration
website/             Main app (models, serializers, views, tests, services)
media/production/    Default generated and uploaded files root
docker-compose.yaml  Local PostgreSQL service
requirements.txt     Python dependencies
```

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

POSTGRES_DB=mydatabase
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_PORT=5432

# Optional
MEDIA_ROOT=/absolute/path/to/media
```

If MEDIA_ROOT is not set, default is BASE_DIR/media/production.

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

4. Start PostgreSQL.

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

API base URL: http://127.0.0.1:8000/api/

## API Endpoints

Base prefix: /api/

### Websites

- GET /api/websites/
- POST /api/websites/ (multipart/form-data)
- GET /api/websites/`<id>`/
- PUT /api/websites/`<id>`/ (multipart/form-data)
- PATCH /api/websites/`<id>`/
- DELETE /api/websites/`<id>`/
- POST /api/websites/`<id>`/build/?mode=preview|live
- POST /api/websites/`<id>`/upload/ (multipart/form-data)

List query parameters:

- search=<name_fragment>
- ordering=created_at|modified_at (prefix with - for descending)
- limit=`<n>`&offset=`<n>`

### Pages

- GET /api/pages/
- POST /api/pages/ (multipart/form-data)
- GET /api/pages/`<id>`/
- PUT /api/pages/`<id>`/ (multipart/form-data)
- PATCH /api/pages/`<id>`/
- DELETE /api/pages/`<id>`/

List query parameters:

- search=<title_fragment>
- ordering=created_at|modified_at (prefix with - for descending)
- limit=`<n>`&offset=`<n>`

### Notes

- Build mode is required and must be preview or live.
- A website must have at least one page before build.
- Asset upload expects two list fields with matching lengths: files and alt_texts.
- Asset upload supports only image/* and video/* content types.

## Build Output

Build artifacts are generated under:

- <MEDIA_ROOT>/<website_name>/preview/
- <MEDIA_ROOT>/<website_name>/live/

Each build writes:

- pages/<page_slug>.html
- static/style.css
- static/script.js
- asset/images/<filename>
- asset/videos/<filename>

## Management Commands

- python manage.py seed_db
- python manage.py clear_db

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
