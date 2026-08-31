import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.config import settings
from app.database import engine
from app.api.v1.router import api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("deepprep")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered role-readiness platform for engineering candidates.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Explicit CORS configuration without wildcard for safe credential sharing
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global safe exception handler to prevent raw traceback leakage to clients
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected server error occurred."},
    )

# Mount versioned API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    db_status = "connected"
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Healthcheck database failure: {e}")
        db_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": settings.PROJECT_NAME,
        "database": db_status,
        "ai_provider": settings.AI_PROVIDER,
        "version": "1.0.0",
    }

@app.get("/")
async def root():
    return {
        "message": "Welcome to DeepPrep API",
        "docs": "/docs",
        "health": "/health",
    }
