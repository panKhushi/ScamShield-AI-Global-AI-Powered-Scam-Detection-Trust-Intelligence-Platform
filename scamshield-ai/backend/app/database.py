import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import Column, DateTime, String, Text, create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SQLITE_DB = BASE_DIR / "scamshield.db"


def _build_engine(database_url: str):
    engine_kwargs = {
        "pool_pre_ping": True,   # tests connection before using it, reconnects if dead
        "pool_recycle": 300,      # recycle connections every 5 minutes
    }
    if database_url.startswith("sqlite"):
        engine_kwargs["connect_args"] = {"check_same_thread": False}
    return create_engine(database_url, **engine_kwargs)

def _resolve_engine():
    configured_url = os.getenv("DATABASE_URL")
    database_url = configured_url or f"sqlite:///{DEFAULT_SQLITE_DB}"

    if database_url.startswith("sqlite"):
        return _build_engine(database_url)

    try:
        engine = _build_engine(database_url)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return engine
    except SQLAlchemyError:
        print("Configured database is unavailable. Falling back to SQLite for local development.")
        return _build_engine(f"sqlite:///{DEFAULT_SQLITE_DB}")


engine = _resolve_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def ensure_schema_compatibility() -> None:
    """Apply small, idempotent upgrades for databases created by older releases."""
    columns = {
        "review_status": Column(String, nullable=True, server_default="pending"),
        "moderator_note": Column(Text, nullable=True),
        "reviewed_by": Column(String, nullable=True),
        "reviewed_at": Column(DateTime(timezone=True), nullable=True),
    }
    existing_columns = {column["name"] for column in inspect(engine).get_columns("reports")}

    with engine.begin() as connection:
        for name, column in columns.items():
            if name in existing_columns:
                continue
            sql_type = column.type.compile(dialect=engine.dialect)
            default = " DEFAULT 'pending'" if name == "review_status" else ""
            connection.execute(text(f'ALTER TABLE reports ADD COLUMN "{name}" {sql_type}{default}'))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()