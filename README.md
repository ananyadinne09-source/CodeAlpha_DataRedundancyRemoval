# NCC Cadet Management System

A Flask web application for managing NCC (National Cadet Corps) cadet
registrations, built for a Cloud Computing internship task on **data
redundancy detection**.

## Features

- **Dashboard** — live stats (total cadets, duplicate count, data accuracy),
  quick-action shortcuts, battalion distribution chart, system status panel.
- **Register Cadet** — validated Indian mobile number and email, with
  exact-match duplicate blocking (email/phone) and an **AI Duplicate
  Assistant** that flags name-similarity matches of 75% or higher for the
  administrator to approve or discard before saving.
- **AI Duplicate Assistant** — every new registration is scanned against
  existing cadets using fuzzy name matching (`rapidfuzz`). Matches at or
  above 75% similarity are routed to a confirmation screen; if the
  administrator chooses "Include Anyway," the record is saved and flagged
  (`is_duplicate=True`, with its similarity score and the matched record),
  which is what feeds the dashboard's "Duplicate Records" count. A
  dedicated **Flagged Duplicates** page lists every flagged cadet so the
  administrator can review or clear them later.
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

### If you have an existing database

If `instance/cadets.db` already exists from a previous version of this
app, run the migration script once before starting the app, so the new
AI Duplicate Assistant columns are added without losing your existing
cadet records:

```bash
python migrate_db.py
```

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
