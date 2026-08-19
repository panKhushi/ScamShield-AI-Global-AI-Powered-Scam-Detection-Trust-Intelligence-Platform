from app.database import engine, Base
from app import db_models_v2

Base.metadata.create_all(bind=engine)
print("V2 normalized tables created.")