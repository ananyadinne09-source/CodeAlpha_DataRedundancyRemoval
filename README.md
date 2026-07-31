# NCC Cadet Management System

A Flask web application for managing NCC (National Cadet Corps) cadet
registrations, built for a Cloud Computing internship task on **data
redundancy detection**.

## Features

- **Dashboard** — live stats (total cadets, duplicate count, data accuracy),
  quick-action shortcuts, battalion distribution chart, system status panel.
- **Register Cadet** — validated Indian mobile number and email, with
  exact-match duplicate blocking (email/phone) and fuzzy name-similarity
  duplicate warnings (via `rapidfuzz`) before a record is saved.
- **Cadet Database** — searchable, sortable table of all cadets with
  edit/delete actions.
- **Reports** — printable summary with charts (Chart.js) and a CSV export.
- **Army-themed UI** — animated tactical background, olive/khaki/brass
  color palette, responsive sidebar navigation with a collapsible menu on
  mobile.

## Tech Stack

- Backend: Flask, Flask-SQLAlchemy, SQLite
- Duplicate name matching: RapidFuzz (`token_sort_ratio`)
- Frontend: Bootstrap 5, Bootstrap Icons, Chart.js, custom CSS/JS

## Running locally

```bash
python -m venv venv
source venv/bin/activate      # venv\Scripts\activate on Windows
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

## Project Structure

```
app.py                  Flask routes / application logic
models.py                SQLAlchemy Record model
config.py                App configuration (DB URI, secret key)
templates/                Jinja2 templates (base layout + pages)
static/css/style.css      Army-themed stylesheet + animated background
static/js/script.js       Sidebar toggle, animated counters, alert auto-dismiss
instance/cadets.db        SQLite database (auto-created on first run)
```
