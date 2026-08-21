"""FastAPI application factory, lifespan management, middleware, and exception handlers."""

from contextlib import asynccontextmanager
from typing import Any
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.logging import get_logger, request_id_ctx, setup_logging
from app.core.middleware import (
    HttpLoggingMiddleware,
    RequestIdMiddleware,
    SecurityHeadersMiddleware,
)
from app.db.session import close_db_engine

logger = get_logger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and graceful shutdown."""
    settings = get_settings()
    setup_logging()
    logger.info(
        f"Starting {settings.APP_NAME} in '{settings.APP_ENV}' mode (debug={settings.DEBUG})"
    )
    yield
    logger.info("Shutting down application...")
    await close_db_engine()
    logger.info("Application shutdown complete.")


def create_application() -> FastAPI:
    """Instantiate and configure the FastAPI application instance."""
    settings = get_settings()

    docs_url = "/docs" if settings.DOCS_ENABLED else None
    redoc_url = "/redoc" if settings.DOCS_ENABLED else None
    openapi_url = "/openapi.json" if settings.DOCS_ENABLED else None

    app = FastAPI(
        title=settings.APP_NAME,
        description="Production-oriented API for the RecoverAI revenue recovery platform.",
        version="0.1.0",
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
        lifespan=lifespan,
    )

    # --------------------------------------------------------------------------
    # Middleware Registration (Executed in reverse order of addition)
    # --------------------------------------------------------------------------
    # 1. CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    # 2. Security Headers Middleware
    app.add_middleware(SecurityHeadersMiddleware)

    # 3. HTTP Request Logging Middleware
    app.add_middleware(HttpLoggingMiddleware)

    # 4. Request ID Middleware (Outermost to ensure context is set first)
    app.add_middleware(RequestIdMiddleware)

    # --------------------------------------------------------------------------
    # Centralized Exception Handlers
    # --------------------------------------------------------------------------
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        req_id = getattr(request.state, "request_id", request_id_ctx.get())
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "request_id": req_id,
                    "details": exc.details,
                }
            },
            headers={"X-Request-ID": req_id} if req_id else None,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        req_id = getattr(request.state, "request_id", request_id_ctx.get())
        # Clean up Pydantic validation errors for serialization
        formatted_errors = []
        for err in exc.errors():
            formatted_errors.append(
                {
                    "loc": list(err.get("loc", [])),
                    "msg": err.get("msg", ""),
                    "type": err.get("type", ""),
                }
            )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "The submitted payload failed validation constraints.",
                    "request_id": req_id,
                    "details": formatted_errors,
                }
            },
            headers={"X-Request-ID": req_id} if req_id else None,
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        req_id = getattr(request.state, "request_id", request_id_ctx.get())
        code = "HTTP_ERROR"
        if exc.status_code == 404:
            code = "NOT_FOUND"
        elif exc.status_code == 401:
            code = "UNAUTHORIZED"
        elif exc.status_code == 403:
            code = "FORBIDDEN"
        elif exc.status_code == 409:
            code = "CONFLICT"

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": code,
                    "message": str(exc.detail),
                    "request_id": req_id,
                }
            },
            headers={"X-Request-ID": req_id} if req_id else None,
        )

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: Any) -> JSONResponse:
        req_id = getattr(request.state, "request_id", request_id_ctx.get())
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Resource not found: {request.url.path}",
                    "request_id": req_id,
                }
            },
            headers={"X-Request-ID": req_id} if req_id else None,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        req_id = getattr(request.state, "request_id", request_id_ctx.get())
        logger.error(
            f"Unhandled exception processing {request.method} {request.url.path}: {exc.__class__.__name__} ({str(exc)})",
            exc_info=True,
            extra={"request_id": req_id},
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred while processing your request.",
                    "request_id": req_id,
                }
            },
            headers={"X-Request-ID": req_id} if req_id else None,
        )

    # --------------------------------------------------------------------------
    # API Routers Mount
    # --------------------------------------------------------------------------
    app.include_router(api_router, prefix="/api")

    return app


app = create_application()
