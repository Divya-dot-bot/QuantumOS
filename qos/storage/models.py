"""
QuantumOS Storage - Models

Data models used by the persistence layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> datetime:
    """Return the current UTC timestamp."""

    return datetime.now(timezone.utc)


@dataclass
class JobRecord:
    """
    Persistent representation of a QuantumOS job.

    This model stores the job metadata and lifecycle state needed
    to reconstruct job history.
    """

    job_id: str
    status: str
    shots: int
    circuit: Any

    backend: str | None = None

    submitted_at: datetime = field(
        default_factory=utc_now
    )

    started_at: datetime | None = None
    completed_at: datetime | None = None

    error: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """Validate the job record."""

        if not isinstance(self.job_id, str):
            raise TypeError(
                "job_id must be a string"
            )

        if not self.job_id.strip():
            raise ValueError(
                "job_id cannot be empty"
            )

        if not isinstance(self.status, str):
            raise TypeError(
                "status must be a string"
            )

        if not isinstance(
            self.shots,
            int,
        ) or isinstance(
            self.shots,
            bool,
        ):
            raise TypeError(
                "shots must be an integer"
            )

        if self.shots < 1:
            raise ValueError(
                "shots must be at least 1"
            )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise TypeError(
                "metadata must be a dictionary"
            )

    def as_dict(self) -> dict[str, Any]:
        """Convert the record into a serializable dictionary."""

        return {
            "job_id": self.job_id,
            "status": self.status,
            "shots": self.shots,
            "circuit": self.circuit,
            "backend": self.backend,
            "submitted_at": self.submitted_at.isoformat(),
            "started_at": (
                self.started_at.isoformat()
                if self.started_at
                else None
            ),
            "completed_at": (
                self.completed_at.isoformat()
                if self.completed_at
                else None
            ),
            "error": self.error,
            "metadata": dict(self.metadata),
        }


@dataclass
class ExecutionRecord:
    """
    Persistent record of a completed or failed execution.
    """

    execution_id: str
    job_id: str
    backend_id: str
    backend_name: str

    status: str

    shots: int

    counts: dict[str, int] = field(
        default_factory=dict
    )

    started_at: datetime = field(
        default_factory=utc_now
    )

    completed_at: datetime | None = None

    error: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """Validate the execution record."""

        if not isinstance(
            self.execution_id,
            str,
        ):
            raise TypeError(
                "execution_id must be a string"
            )

        if not self.execution_id.strip():
            raise ValueError(
                "execution_id cannot be empty"
            )

        if not isinstance(
            self.job_id,
            str,
        ):
            raise TypeError(
                "job_id must be a string"
            )

        if not self.job_id.strip():
            raise ValueError(
                "job_id cannot be empty"
            )

        if not isinstance(
            self.backend_id,
            str,
        ):
            raise TypeError(
                "backend_id must be a string"
            )

        if not self.backend_id.strip():
            raise ValueError(
                "backend_id cannot be empty"
            )

        if not isinstance(
            self.backend_name,
            str,
        ):
            raise TypeError(
                "backend_name must be a string"
            )

        if not self.backend_name.strip():
            raise ValueError(
                "backend_name cannot be empty"
            )

        if not isinstance(
            self.status,
            str,
        ):
            raise TypeError(
                "status must be a string"
            )

        if not isinstance(
            self.shots,
            int,
        ) or isinstance(
            self.shots,
            bool,
        ):
            raise TypeError(
                "shots must be an integer"
            )

        if self.shots < 1:
            raise ValueError(
                "shots must be at least 1"
            )

        if not isinstance(
            self.counts,
            dict,
        ):
            raise TypeError(
                "counts must be a dictionary"
            )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise TypeError(
                "metadata must be a dictionary"
            )

    def as_dict(self) -> dict[str, Any]:
        """Convert the execution record into a dictionary."""

        return {
            "execution_id": self.execution_id,
            "job_id": self.job_id,
            "backend_id": self.backend_id,
            "backend_name": self.backend_name,
            "status": self.status,
            "shots": self.shots,
            "counts": dict(self.counts),
            "started_at": self.started_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat()
                if self.completed_at
                else None
            ),
            "error": self.error,
            "metadata": dict(self.metadata),
        }


@dataclass
class ResourceRecord:
    """
    Persistent representation of a quantum execution resource.
    """

    resource_id: str
    name: str
    resource_type: str
    num_qubits: int
    status: str

    supported_operations: list[str] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    updated_at: datetime = field(
        default_factory=utc_now
    )

    def __post_init__(self) -> None:
        """Validate the resource record."""

        if not isinstance(
            self.resource_id,
            str,
        ):
            raise TypeError(
                "resource_id must be a string"
            )

        if not self.resource_id.strip():
            raise ValueError(
                "resource_id cannot be empty"
            )

        if not isinstance(
            self.name,
            str,
        ):
            raise TypeError(
                "name must be a string"
            )

        if not self.name.strip():
            raise ValueError(
                "name cannot be empty"
            )

        if not isinstance(
            self.resource_type,
            str,
        ):
            raise TypeError(
                "resource_type must be a string"
            )

        if not isinstance(
            self.num_qubits,
            int,
        ) or isinstance(
            self.num_qubits,
            bool,
        ):
            raise TypeError(
                "num_qubits must be an integer"
            )

        if self.num_qubits < 1:
            raise ValueError(
                "num_qubits must be at least 1"
            )

        if not isinstance(
            self.status,
            str,
        ):
            raise TypeError(
                "status must be a string"
            )

        if not isinstance(
            self.supported_operations,
            list,
        ):
            raise TypeError(
                "supported_operations must be a list"
            )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise TypeError(
                "metadata must be a dictionary"
            )

    def as_dict(self) -> dict[str, Any]:
        """Convert the resource record into a dictionary."""

        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "resource_type": self.resource_type,
            "num_qubits": self.num_qubits,
            "status": self.status,
            "supported_operations": list(
                self.supported_operations
            ),
            "metadata": dict(self.metadata),
            "updated_at": self.updated_at.isoformat(),
        }