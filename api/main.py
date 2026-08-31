"""
QuantumOS HTTP API.

FastAPI application entry point.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.backends import router as backends_router
from api.routes.jobs import router as jobs_router
from api.routes.resources import router as resources_router
from api.schemas.jobs import HealthResponse


APP_TITLE = "QuantumOS API"
APP_DESCRIPTION = """
QuantumOS is a research-oriented quantum operating system MVP.

The API provides access to:

- quantum job submission
- job scheduling
- quantum backends
- resource management
- execution results
"""

APP_VERSION = "0.1.0"


def create_app() -> FastAPI:
    """
    Create and configure the QuantumOS FastAPI application.
    """

    app = FastAPI(
        title=APP_TITLE,
        description=APP_DESCRIPTION,
        version=APP_VERSION,
    )

    # --------------------------------------------------------------
    # CORS
    # --------------------------------------------------------------

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --------------------------------------------------------------
    # Routes
    # --------------------------------------------------------------

    app.include_router(
        jobs_router,
        prefix="/api/jobs",
        tags=["Jobs"],
    )

    app.include_router(
        resources_router,
        prefix="/api/resources",
        tags=["Resources"],
    )

    app.include_router(
        backends_router,
        prefix="/api/backends",
        tags=["Backends"],
    )

    # --------------------------------------------------------------
    # Health endpoint
    # --------------------------------------------------------------

    @app.get(
        "/health",
        response_model=HealthResponse,
        tags=["System"],
    )
    def health() -> HealthResponse:
        """Return API health information."""

        return HealthResponse(
            status="healthy",
            service="quantumos-api",
            version=APP_VERSION,
        )

    # --------------------------------------------------------------
    # Root endpoint
    # --------------------------------------------------------------

    @app.get(
        "/",
        tags=["System"],
    )
    def root() -> dict[str, str]:
        """Return basic API information."""

        return {
            "name": APP_TITLE,
            "version": APP_VERSION,
            "status": "running",
            "docs": "/docs",
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )