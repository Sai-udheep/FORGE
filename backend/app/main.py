from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models import Category
from app.api.v1.router import api_router
from app.integrations.study_cursor_adapter import adapter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("forge.main")

def init_db_and_seed():
    """Initializes tables and default categories if empty."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Seed core default categories if empty
        if db.query(Category).count() == 0:
            default_categories = [
                Category(name="GATE 2027", color="#06B6D4", icon="graduation-cap", sort_order=1),
                Category(name="InfoEdge SDE Prep", color="#FF6B35", icon="briefcase", sort_order=2),
                Category(name="DSA & Problem Solving", color="#8B5CF6", icon="code", sort_order=3),
                Category(name="Academics & Semester", color="#3B82F6", icon="book-open", sort_order=4),
                Category(name="Personal & Health", color="#10B981", icon="heart", sort_order=5),
            ]
            db.add_all(default_categories)
            db.commit()
            logger.info("Initialized default categories in FORGE database.")
        
        # Ingest Study Cursor manifest on startup if present
        try:
            adapter.ingest_manifest(db)
            logger.info("Successfully ingested Study Cursor catalog manifest.")
        except Exception as e:
            logger.warning(f"Initial Study Cursor ingestion skipped: {e}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    init_db_and_seed()
    yield
    # Shutdown
    logger.info(f"Shutting down {settings.PROJECT_NAME}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Personal Execution System — Plan, Focus, Track, Grow",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "api_v1": settings.API_V1_STR
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal Server Error", "detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
