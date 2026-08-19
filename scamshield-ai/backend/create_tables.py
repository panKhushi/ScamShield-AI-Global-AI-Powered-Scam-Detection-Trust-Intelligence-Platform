import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parent))

from app.database import Base, engine
from app import db_models

print(f"Using database: {engine.url}")
Base.metadata.create_all(bind=engine)
print("Tables created successfully.")