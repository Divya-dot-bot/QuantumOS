"""
QuantumOS API - Resource Routes

REST endpoints for quantum resource discovery,
inspection, and utilization.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status

from api.dependencies import get_runtime
from api.schemas.resources import (
    ResourceListResponse,
    ResourceResponse,
)


router = APIRouter()


# ----------------------------------------------------------------------
# Resource statistics
# ----------------------------------------------------------------------


@router.get(
    "/stats",
)
def resource_stats() -> dict[str, Any]:
    """
    Return live QuantumOS resource statistics.
    """

    runtime = get_runtime()

    resources = (
        runtime.resource_manager.list_resources()
    )

    available = [
        resource
        for resource in resources
        if resource.is_available
    ]

    busy = [
        resource
        for resource in resources
        if resource.is_busy
    ]

    return {
        "total_resources": len(resources),
        "available_resources": len(available),
        "busy_resources": len(busy),
        "offline_resources": len(
            [
                resource
                for resource in resources
                if resource.status.value == "offline"
            ]
        ),
        "maintenance_resources": len(
            [
                resource
                for resource in resources
                if resource.status.value == "maintenance"
            ]
        ),
        "allocations": (
            runtime.resource_manager.allocation_count
        ),
    }


# ----------------------------------------------------------------------
# List resources
# ----------------------------------------------------------------------


@router.get(
    "",
    response_model=ResourceListResponse,
)
def list_resources() -> ResourceListResponse:
    """
    Return all registered quantum resources.
    """

    runtime = get_runtime()

    resources = (
        runtime.resource_manager.list_resources()
    )

    result = [
        _resource_to_response(resource)
        for resource in resources
    ]

    return ResourceListResponse(
        resources=result,
        total=len(result),
    )


# ----------------------------------------------------------------------
# Get resource
# ----------------------------------------------------------------------


@router.get(
    "/{resource_id}",
    response_model=ResourceResponse,
)
def get_resource(
    resource_id: str,
) -> ResourceResponse:
    """
    Return information about a specific resource.
    """

    runtime = get_runtime()

    resource = (
        runtime.resource_manager.get_resource(
            resource_id
        )
    )

    if resource is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Resource '{resource_id}' not found."
            ),
        )

    return _resource_to_response(
        resource
    )


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _resource_to_response(
    resource,
) -> ResourceResponse:
    """
    Convert a resource object into an API response.
    """

    return ResourceResponse(
        resource_id=resource.resource_id,
        name=resource.name,
        resource_type=(
            resource.resource_type.value
            if hasattr(
                resource.resource_type,
                "value",
            )
            else str(
                resource.resource_type
            )
        ),
        num_qubits=resource.num_qubits,
        status=(
            resource.status.value
            if hasattr(
                resource.status,
                "value",
            )
            else str(
                resource.status
            )
        ),
        supported_operations=list(
            resource.supported_operations
        ),
        metadata=dict(
            getattr(
                resource,
                "metadata",
                {},
            )
        ),
    )