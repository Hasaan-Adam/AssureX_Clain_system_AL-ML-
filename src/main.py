"""
AssureX Claim Engine - FastAPI Enterprise Application Entrypoint
Configures CORS, global exception middleware, static file directories, database lifecycle, and API v1 routing.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from database.connection import Base, engine
from src.api.v1.router import api_router
from src.config import settings
from src.core.exceptions import AssureXBaseException, format_error_response
from src.core.logging_config import setup_logging

setup_logging(
    log_level=settings.logging.level,
    log_format=settings.logging.format,
    log_file=settings.logging.log_file,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown event handler.
    Ensures database schema exists and directories are initialized.
    """
    upload_path = Path(settings.uploads.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)

    static_path = Path("static")
    static_path.mkdir(parents=True, exist_ok=True)

    Base.metadata.create_all(bind=engine)

    yield


app = FastAPI(
    title=settings.app.name,
    version=settings.app.version,
    description=settings.app.description,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    redirect_slashes=False,  # Prevents 307 redirects that bypass Vite proxy and cause CORS errors
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allow_origins,
    allow_credentials=settings.cors.allow_credentials,
    allow_methods=settings.cors.allow_methods,
    allow_headers=settings.cors.allow_headers,
)


@app.exception_handler(AssureXBaseException)
async def assurex_exception_handler(request: Request, exc: AssureXBaseException):
    """Handle custom application exceptions cleanly."""
    return format_error_response(
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print('VALIDATION ERROR:', exc.errors())
    """Handle FastAPI / Pydantic schema validation failures."""
    return format_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="VALIDATION_ERROR",
        message="Request payload failed structural validation.",
        details=exc.errors(),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, dict):
        code = detail.get("code", "HTTP_ERROR")
        msg = detail.get("message", "An HTTP error occurred.")
        details = detail.get("details", {})
    else:
        status_code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            409: "CONFLICT",
            422: "VALIDATION_ERROR",
            429: "RATE_LIMIT_EXCEEDED",
        }
        code = status_code_map.get(exc.status_code, "HTTP_ERROR")
        msg = str(detail)
        details = {}

    return format_error_response(
        status_code=exc.status_code,
        code=code,
        message=msg,
        details=details,
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unhandled server exceptions and print traceback securely."""
    import traceback
    traceback.print_exc()
    is_debug = getattr(settings.app, "debug", False)
    msg = f"{type(exc).__name__}: {str(exc)}" if is_debug else "An unexpected internal server error occurred. Please try again later."
    details = {"error_type": type(exc).__name__} if is_debug else {}
    return format_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="INTERNAL_SERVER_ERROR",
        message=msg,
        details=details,
    )


uploads_dir = Path(settings.uploads.upload_dir)
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

static_dir = Path("static")
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


app.include_router(api_router, prefix=settings.app.api_prefix)


@app.get("/", tags=["Health"])
@app.get("/health", tags=["Health"])
def health_check():
    """Top-level health and service telemetry endpoint."""
    return {
        "status": "healthy",
        "service": settings.app.name,
        "version": settings.app.version,
        "environment": settings.app.environment,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.reload,
    )
