"""
QuantumOS API - Backend Routes

REST endpoints for quantum backend discovery and inspection.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from api.schemas.resources import (
    BackendListResponse,
    BackendResponse,
)
from api.dependencies import get_runtime


router = APIRouter()
# ----------------------------------------------------------------------
# List backends
# ----------------------------------------------------------------------


@router.get(
    "",
    response_model=BackendListResponse,
)
def list_backends() -> BackendListResponse:
    """
    Return all registered quantum backends.
    """

    runtime = get_runtime()

    backends = (
        runtime.resource_manager.list_backends()
    )

    result = [
        _backend_to_response(backend)
        for backend in backends
    ]

    return BackendListResponse(
        backends=result,
        total=len(result),
    )


# ----------------------------------------------------------------------
# Get backend
# ----------------------------------------------------------------------


@router.get(
    "/{backend_id}",
    response_model=BackendResponse,
)
def get_backend(
    backend_id: str,
) -> BackendResponse:
    """
    Return information about a specific backend.
    """

    runtime = get_runtime()

    backend = (
        runtime.resource_manager.get_backend(
            backend_id
        )
    )

    if backend is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Backend '{backend_id}' not found."
            ),
        )

    return _backend_to_response(
        backend
    )


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _backend_to_response(
    backend,
) -> BackendResponse:
    """Convert a backend object into an API response."""

    resource_type = getattr(
        backend,
        "resource_type",
        None,
    )

    status_value = getattr(
        backend,
        "status",
        None,
    )

    return BackendResponse(
        backend_id=backend.backend_id,
        name=backend.name,
        resource_type=(
            resource_type.value
            if hasattr(
                resource_type,
                "value",
            )
            else str(resource_type)
        ),
        num_qubits=backend.num_qubits,
        status=(
            status_value.value
            if hasattr(
                status_value,
                "value",
            )
            else str(status_value)
        ),
        is_busy=bool(
            backend.is_busy
        ),
        supported_operations=list(
            getattr(
                backend,
                "supported_operations",
                [],
            )
        ),
        metadata=dict(
            getattr(
                backend,
                "metadata",
                {},
            )
        ),
    )
