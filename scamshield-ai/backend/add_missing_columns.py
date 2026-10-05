#!/usr/bin/env python
"""
Schema migration script: safely add missing columns to existing tables.

This script inspects the actual database schema and compares it to the
SQLAlchemy model definitions. For any missing columns, it runs ALTER TABLE
statements to add them without dropping data.

Usage:
    python add_missing_columns.py

Supported databases:
    - PostgreSQL (with proper psycopg2 error handling)
    - SQLite (with SQLite-compatible ALTER TABLE syntax)
"""

import sys
from sqlalchemy import inspect, text, Integer, String, JSON, DateTime
from sqlalchemy.exc import SQLAlchemyError
from app.database import engine, Base
from app.db_models import HistoricalEvent, HistoricalRecord, Report, ScanRecord

# Map SQLAlchemy column types to database-specific SQL types
def get_sql_type(column):
    """Convert SQLAlchemy column type to SQL type string."""
    type_name = str(column.type)
    
    if "VARCHAR" in type_name:
        return "VARCHAR"
    elif "INTEGER" in type_name:
        return "INTEGER"
    elif "JSON" in type_name:
        # PostgreSQL uses JSON/JSONB; SQLite uses TEXT
        db_url = engine.url.drivername
        return "JSONB" if "postgres" in db_url else "TEXT"
    elif "DATETIME" in type_name:
        return "TIMESTAMP WITH TIME ZONE" if "postgres" in engine.url.drivername else "DATETIME"
    else:
        return "TEXT"

def get_column_default(column):
    """Return DEFAULT clause for a column if it has a server default."""
    if column.server_default is not None:
        # For func.now() defaults in Postgres
        if "postgres" in engine.url.drivername:
            if "now" in str(column.server_default.arg):
                return "DEFAULT CURRENT_TIMESTAMP"
    return ""

def migrate_table(table_class):
    """
    Inspect a table and add any missing columns from the SQLAlchemy model.
    
    Args:
        table_class: SQLAlchemy declarative model class (e.g., ScanRecord)
    """
    inspector = inspect(engine)
    table_name = table_class.__tablename__
    
    # Get existing columns in the actual database
    existing_columns = {col["name"] for col in inspector.get_columns(table_name)}
    
    # Get defined columns from the model
    model_columns = table_class.__table__.columns
    
    # Find missing columns
    missing_columns = []
    for col in model_columns:
        if col.name not in existing_columns:
            missing_columns.append(col)
    
    if not missing_columns:
        print(f"✓ Table '{table_name}' is up to date. No missing columns.")
        return True
    
    print(f"\n⚠ Table '{table_name}' is missing {len(missing_columns)} column(s):")
    for col in missing_columns:
        print(f"  - {col.name} ({get_sql_type(col)})")
    
    # Build and execute ALTER TABLE statements
    db_url = engine.url.drivername
    is_postgres = "postgres" in db_url
    
    try:
        with engine.connect() as connection:
            for col in missing_columns:
                col_name = col.name
                col_type = get_sql_type(col)
                nullable = "NULL" if col.nullable else "NOT NULL"
                default_clause = get_column_default(col)
                
                # SQLite doesn't support all ALTER TABLE features
                if "sqlite" in db_url:
                    # SQLite: ALTER TABLE only supports ADD COLUMN (with limitations)
                    sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type} {nullable}"
                else:
                    # Postgres: full ALTER TABLE support
                    sql = f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {col_name} {col_type} {nullable}"
                    if default_clause:
                        sql += f" {default_clause}"
                
                print(f"  Executing: {sql}")
                try:
                    connection.execute(text(sql))
                    connection.commit()
                    print(f"  ✓ Column '{col_name}' added successfully.")
                except SQLAlchemyError as e:
                    # Check if it's "column already exists" error (harmless)
                    error_str = str(e)
                    if "already exists" in error_str or "duplicate column" in error_str:
                        print(f"  ⓘ Column '{col_name}' already exists (skipped).")
                    else:
                        print(f"  ✗ Error adding column '{col_name}': {error_str}")
                        return False
        
        return True
    except SQLAlchemyError as e:
        print(f"✗ Database error: {e}")
        return False

def main():
    """Run migrations for all models."""
    print("=" * 60)
    print("ScamShield AI - Database Schema Migration")
    print("=" * 60)
    
    # Get the database URL for display
    db_url = engine.url
    print(f"\nConnected to: {db_url.drivername}://{db_url.host or 'local'}/{db_url.database or 'database'}")
    
    # Create newly introduced tables, then add missing columns to existing tables.
    Base.metadata.create_all(bind=engine)
    models = [ScanRecord, Report, HistoricalRecord, HistoricalEvent]
    
    all_success = True
    for model in models:
        try:
            success = migrate_table(model)
            if not success:
                all_success = False
        except Exception as e:
            print(f"✗ Unexpected error migrating {model.__tablename__}: {e}")
            all_success = False
    
    print("\n" + "=" * 60)
    if all_success:
        print("✓ Migration completed successfully!")
        return 0
    else:
        print("✗ Migration completed with errors.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
