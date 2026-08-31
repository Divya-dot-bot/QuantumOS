"""
QuantumOS API - Job Schemas

Pydantic models used for quantum job requests and responses.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class JobCreateRequest(BaseModel):
    """
    Request body used to submit a quantum job.
    """

    circuit: Any = Field(
        ...,
        description="Quantum circuit representation.",
    )

    shots: int = Field(
        default=1024,
        ge=1,
        le=1_000_000,
        description="Number of measurement shots.",
    )

    priority: int = Field(
        default=0,
        description="Scheduling priority.",
    )

    backend: str | None = Field(
        default=None,
        description="Optional backend identifier.",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional job metadata.",
    )


class JobResponse(BaseModel):
    """
    API representation of a quantum job.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    job_id: str

    status: str

    shots: int

    priority: int

    backend: str | None = None

    submitted_at: datetime | None = None

    started_at: datetime | None = None

    completed_at: datetime | None = None

    error: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class JobSubmissionResponse(BaseModel):
    """
    Response returned immediately after job submission.
    """

    job_id: str

    status: str

    message: str


class JobResultResponse(BaseModel):
    """
    Response containing quantum execution results.
    """

    job_id: str

    status: str

    backend_id: str | None = None

    backend_name: str | None = None

    shots: int

    counts: dict[str, int] = Field(
        default_factory=dict
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class HealthResponse(BaseModel):
    """
    API health response.
    """

    status: str

    service: str

    version: str