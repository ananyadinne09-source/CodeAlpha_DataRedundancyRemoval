import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _resolve_database_uri():
    """
    On a cloud host (Render, Railway, etc.) the platform injects a
    DATABASE_URL environment variable pointing at a managed Postgres
    instance. Locally, no such variable exists, so we fall back to the
    SQLite file under instance/ for development.
    """
    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        # Some platforms hand out "postgres://" which SQLAlchemy 1.4+
        # no longer accepts — it must be "postgresql://".
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        return database_url

    return "sqlite:///" + os.path.join(BASE_DIR, "instance", "cadets.db")


class Config:

    SECRET_KEY = os.environ.get("SECRET_KEY", "ncc_cadet_management_system")

    SQLALCHEMY_DATABASE_URI = _resolve_database_uri()

    SQLALCHEMY_TRACK_MODIFICATIONS = False
