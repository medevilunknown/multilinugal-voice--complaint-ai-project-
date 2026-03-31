import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

import models  # noqa: F401
from config import settings
from database import Base, engine, SessionLocal
from models.admin import Admin
from routes.admin import router as admin_router
from routes.ai import router as ai_router
from routes.chat import router as chat_router
from routes.complaint import router as complaint_router
from utils.file_utils import ensure_upload_dirs
from utils.logger import log
from utils.security import hash_password

# ─── Rate Limiter ─────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])


# ─── Lifespan (replaces deprecated on_event) ──────────────────────────
@asynccontextmanager
async def lifespan(application: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    seed_admin()
    log.info("CyberGuard AI backend started successfully")
    yield
    # Shutdown
    log.info("CyberGuard AI backend shutting down")


app = FastAPI(
    title="CyberGuard AI Backend",
    version="2.0.0",
    description="Enterprise-grade AI-powered Cyber Crime Complaint System",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

Base.metadata.create_all(bind=engine)

# Ensure upload folders exist before serving static files.
try:
    ensure_upload_dirs()
    if os.path.exists(settings.upload_dir):
        app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
except Exception as e:
    log.warning(f"Static mount failed: {e}")

# ─── CORS Configuration ───────────────────────────────────────────────
ALLOWED_ORIGINS = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:8080,http://localhost:8081,http://127.0.0.1:8080,http://127.0.0.1:8081",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


def seed_admin() -> None:
    db: Session = SessionLocal()
    try:
        admin = db.query(Admin).filter(Admin.email == settings.admin_email).first()
        if not admin:
            db.add(Admin(email=settings.admin_email, password=hash_password(settings.admin_password)))
            db.commit()
            log.info("Admin user seeded successfully")
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}


@app.get("/")
def root():
    return {
        "message": "CyberGuard AI backend is running",
        "supported_languages": [
            "English",
            "Hindi",
            "Konkani",
            "Kannada",
            "Dogri",
            "Bodo",
            "Urdu",
            "Tamil",
            "Kashmiri",
            "Assamese",
            "Bengali",
            "Marathi",
            "Sindhi",
            "Maithili",
            "Punjabi",
            "Malayalam",
            "Manipuri",
            "Telugu",
            "Sanskrit",
            "Nepali",
            "Santali",
            "Gujarati",
            "Odia",
        ],
    }


app.include_router(chat_router)
app.include_router(complaint_router)
app.include_router(admin_router)
app.include_router(ai_router)
