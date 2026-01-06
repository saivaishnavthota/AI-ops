from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config.settings import settings
from app.config.database import init_db, close_db
from app.config.redis import init_redis, close_redis
from app.config.logging import setup_logging, get_logger
from app.api.v1.router import api_router
from app.core.exceptions import AIOpsPlatformException

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting AI-Ops Platform...")

    # Initialize database
    logger.info("Initializing database connection...")
    await init_db()

    # Initialize Redis
    logger.info("Initializing Redis connection...")
    await init_redis()

    logger.info("AI-Ops Platform started successfully!")

    yield

    # Shutdown
    logger.info("Shutting down AI-Ops Platform...")
    await close_db()
    await close_redis()
    logger.info("AI-Ops Platform stopped.")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Managed Services Operations Platform",
    version=settings.APP_VERSION,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Add CORS middleware
# SECURITY: Never use wildcard "*" with allow_credentials=True
# This combination allows any website to make authenticated requests
cors_origins = settings.CORS_ORIGINS

# Filter out wildcards - they're not allowed with credentials
safe_origins = [
    origin for origin in cors_origins
    if origin.strip() != "*" and origin.strip()
]

# Log warning if wildcards were configured (security misconfiguration)
if len(safe_origins) != len(cors_origins):
    import logging
    logging.getLogger(__name__).warning(
        "SECURITY: Wildcard '*' in CORS_ORIGINS is not allowed with credentials. "
        "Specify explicit origins instead. Wildcards have been removed."
    )

# Use only explicit origins with credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=safe_origins if safe_origins else ["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],  # Allow all headers for development
    expose_headers=["X-Total-Count", "X-Page", "X-Page-Size"],
    max_age=600,  # Cache preflight requests for 10 minutes
)


# Exception handlers
@app.exception_handler(AIOpsPlatformException)
async def platform_exception_handler(request: Request, exc: AIOpsPlatformException):
    """Handle platform-specific exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Request validation failed",
            "details": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
        },
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


# API info endpoint
@app.get("/api", tags=["Info"])
async def api_info():
    """API information endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "AI-Powered Managed Services Operations Platform API",
        "docs": "/api/docs" if settings.DEBUG else None,
    }


# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
