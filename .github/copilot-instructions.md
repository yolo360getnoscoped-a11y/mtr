# Copilot / AI Agent Instructions

Purpose: give an AI coding agent the minimal, actionable context to be productive in this Django project.

1) Project overview
- Framework: Django (project root: `checkin_project/`).
- Apps: `accounts`, `academic`, `attendance`, `teacher` (see [checkin_project/settings.py](checkin_project/settings.py)).
- DB: PostgreSQL (configured via environment variables in `.env` using python-decouple).

2) Big-picture architecture
- Single Django project with multiple apps separating responsibilities:
  - `accounts` handles the custom `AUTH_USER_MODEL` and profiles.
  - `academic` models courses, sections, semesters and enrollments.
  - `attendance` creates attendance sessions, QR codes and attendance records.
  - `teacher` contains teacher views/routing.
- Templates live in `templates/` and per-app subfolders. Static assets in `static/`.
- Custom middleware: `checkin_project.middleware.StaticFilesCacheMiddleware` — affects static response headers.

3) Key files to inspect when changing behavior
- Settings & env: [checkin_project/settings.py](checkin_project/settings.py) and `.env.example` at project root.
- Custom user model: `accounts/models.py` (AUTH_USER_MODEL configured in settings).
- Attendance flow: `attendance/models.py`, `attendance/views.py`, and QR helpers.
- Academic domain: `academic/models.py` and `academic/views.py` (course/section/enrollment logic).
- Admin and management scripts: root scripts like `add_students_from_list.py`, `manage.py` for common tasks.
- Docs and setup notes: `README.md` (root) and `docs/README.md` — follow these for reproducible setup.

4) Developer workflows (exact commands)
- Create venv and activate (Windows):
  ```powershell
  python -m venv venv
  venv\Scripts\activate
  pip install -r requirements.txt
  ```
- Copy `.env.example` → `.env` and set `DB_*`, `SECRET_KEY`, `DEBUG`.
- Run migrations and create superuser:
  ```bash
  python manage.py migrate
  python manage.py createsuperuser
  ```
- Run server locally:
  ```bash
  python manage.py runserver
  ```
- Tests: use Django test runner:
  ```bash
  python manage.py test
  ```

5) Project-specific conventions & gotchas
- Locale: `LANGUAGE_CODE='th-th'` and `TIME_ZONE='Asia/Bangkok'` — tests/dev may assume Thai text and formats.
- Database: PostgreSQL is expected in CI/dev; settings use `decouple.config` to read env vars.
- Many helper scripts live at repository root (e.g., `add_students_*.py`) — these are used to seed/update student data and should be inspected before bulk operations.
- Static files: `STATICFILES_DIRS` + `STATIC_ROOT`; project uses a custom middleware that sets cache headers — changes can affect serving static assets in development.

6) Integration points & dependencies
- External: PostgreSQL, optional ngrok for remote testing (CSRF_TRUSTED_ORIGINS contains ngrok hosts).
- Libraries: `qrcode`, `openpyxl` (see `requirements.txt` and `docs/TEST_EXCEL_IMPORT.md`).

7) How to approach common tasks (examples)
- Add a new field to enrollment models: update `academic/models.py` → create migration (`makemigrations`) → run `migrate` → update related views and templates in `academic/views.py` and `templates/academic/`.
- Debug QR/attendance issues: trace from `attendance/views.py` where QR is created, inspect `attendance/models.py` for `AttendanceSession` and `AttendanceRecord`, and check `templates/attendance/` for frontend expectations.

8) Where to look for documentation & context
- Quick start: [README.md](README.md)
- Detailed setup and test instructions: [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) and [docs/TEST_EXCEL_IMPORT.md](docs/TEST_EXCEL_IMPORT.md)
- Audit notes: [docs/AUDIT_REPORT.md](docs/AUDIT_REPORT.md)

If any section is unclear or you'd like more samples (e.g., common refactors, test harness examples, or specific file walkthroughs), tell me which area to expand.
