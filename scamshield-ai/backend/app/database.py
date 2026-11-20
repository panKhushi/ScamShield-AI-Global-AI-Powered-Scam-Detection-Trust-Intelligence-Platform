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
    inspector = inspect(engine)

    with engine.begin() as connection:
        for table in Base.metadata.sorted_tables:
            table_name = table.name
            if table_name not in inspector.get_table_names():
                continue

            existing_columns = {
                column["name"]
                for column in inspector.get_columns(table_name)
            }

            for column in table.columns:
                if column.name in existing_columns or column.primary_key:
                    continue

                sql_type = column.type.compile(dialect=engine.dialect)
                nullable = "NULL" if column.nullable else "NOT NULL"
                default = ""

                if column.server_default is not None:
                    default_arg = str(column.server_default.arg)
                    if "now" in default_arg.lower():
                        default = " DEFAULT CURRENT_TIMESTAMP"
                    elif "'pending'" in default_arg:
                        default = " DEFAULT 'pending'"

                if engine.dialect.name == "sqlite":
                    connection.execute(
                        text(
                            f'ALTER TABLE "{table_name}" '
                            f'ADD COLUMN "{column.name}" {sql_type} {nullable}{default}'
                        )
                    )
                else:
                    connection.execute(
                        text(
                            f'ALTER TABLE "{table_name}" '
                            f'ADD COLUMN IF NOT EXISTS "{column.name}" '
                            f'{sql_type}{default}'
                        )
                    )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()