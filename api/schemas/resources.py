"""
QuantumOS API - Resource Schemas

Pydantic models used for quantum resource and backend
requests/responses.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ResourceResponse(BaseModel):
    """
    API representation of a quantum resource.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    resource_id: str

    name: str

    resource_type: str

    num_qubits: int = Field(
        ge=1
    )

    status: str

    supported_operations: list[str] = Field(
        default_factory=list
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class ResourceListResponse(BaseModel):
    """
    Response containing multiple quantum resources.
    """

    resources: list[ResourceResponse] = Field(
        default_factory=list
    )

    total: int


class BackendResponse(BaseModel):
    """
    API representation of a quantum backend.
    """

    backend_id: str

    name: str

    resource_type: str

    num_qubits: int = Field(
        ge=1
    )

    status: str

    is_busy: bool

    supported_operations: list[str] = Field(
        default_factory=list
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class BackendListResponse(BaseModel):
    """
    Response containing available quantum backends.
    """

    backends: list[BackendResponse] = Field(
        default_factory=list
    )

    total: int


class ResourceAllocationResponse(BaseModel):
    """
    Response describing a resource allocation.
    """

    job_id: str

    backend_id: str

    backend_name: str

    allocated: bool