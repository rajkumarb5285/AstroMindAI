import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.v1.health import router as health_router
from backend.app.api.v1.router import api_v1_router
from backend.app.core.config import settings
from backend.app.core.logging import setup_logging
from backend.app.core.middleware import RequestContextMiddleware, SecurityHeadersMiddleware
from backend.app.core.rate_limit import RateLimitMiddleware

# Initialize structured logging
setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger("astromind.app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode")
    from backend.app.db.session import Base, engine

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Synchronized database schema tables successfully")
    except Exception as exc:
        logger.error(f"Database schema auto-creation notice: {exc}")
    yield
    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    description="Deterministic Vedic Astrology Calculation Platform and Grounded AI Assistant",
    version="1.0.0",
    docs_url="/docs" if not settings.is_production else None,  # Hide Swagger in production
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None,
    lifespan=lifespan,
)

# 1. Custom Security & Context Middleware (LIFO order: outermost to innermost)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestContextMiddleware)

# 2. Strict CORS policy - No wildcard '*' with credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)


# 3. Standardized Validation Error Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(
        f"Validation error on {request.url.path}: {exc.errors()}",
        extra={"request_id": request_id},
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed. Please check the provided fields.",
                "request_id": request_id,
                "details": jsonable_encoder(exc.errors()),
            }
        },
        headers={"X-Request-ID": request_id},
    )


# 4. Mount Health Probes at root level (standard Kubernetes/Docker probes)
app.include_router(health_router)

# 5. Mount API v1 router
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root(request: Request):
    request_id = getattr(request.state, "request_id", "unknown")
    return {
        "name": settings.APP_NAME,
        "status": "operational",
        "version": "1.0.0",
        "request_id": request_id,
    }
