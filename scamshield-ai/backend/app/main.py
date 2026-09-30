import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("scamshield")
logging.basicConfig(level=logging.INFO)
DEBUG_ERRORS = os.getenv("SCAMSHIELD_DEBUG", "false").lower() in {"1", "true", "yes"}

from app.database import Base, engine
from app import db_models, db_models_v2
from app.routers import analyze, history, reports, verification

app = FastAPI(title="ScamShield AI API")


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception while processing %s %s", request.method, request.url.path)
    detail = str(exc) if DEBUG_ERRORS and str(exc) else "Internal server error; check the backend terminal for the traceback"
    return JSONResponse(status_code=500, content={"detail": detail})


@app.on_event("startup")
def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(verification.router, prefix="/api")


@app.get("/")
def root():
    return {"status": "ScamShield AI backend running"}