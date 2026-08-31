"""
QuantumOS Scheduler - Quantum Jobs

Defines the QuantumJob abstraction and its lifecycle.

A QuantumJob represents a unit of quantum work submitted to
the QuantumOS runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from qos.core.circuit import QuantumCircuit


class JobStatus(str, Enum):
    """
    Lifecycle states for a QuantumOS job.

    CREATED and SUBMITTED are aliases representing the initial
    state of a newly created job.

    The scheduler moves the job from CREATED/SUBMITTED to QUEUED
    when the job is submitted to the scheduler.
    """

    CREATED = "created"

    # Backwards-compatible name used by integration tests/API code.
    # It intentionally has the same value as CREATED.
    SUBMITTED = "created"

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class InvalidJobStateError(RuntimeError):
    """Raised when an invalid job state transition is requested."""


@dataclass
class QuantumJob:
    """
    Represents a quantum workload submitted to QuantumOS.

    Attributes:
        circuit:
            Quantum circuit that should be executed.

        shots:
            Number of measurement shots.

        priority:
            Scheduling priority. Higher values represent higher priority.

        backend:
            Optional backend name requested by the user.

        metadata:
            Arbitrary user-defined job metadata.

        job_id:
            Optional user-provided job identifier. If omitted,
            QuantumOS generates a UUID automatically.
    """

    circuit: QuantumCircuit
    shots: int = 1000
    priority: int = 0
    backend: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    id: str = field(
        default_factory=lambda: str(uuid4()),
        init=False,
    )

    status: JobStatus = field(
        default=JobStatus.CREATED,
        init=False,
    )

    result: Any = field(
        default=None,
        init=False,
    )

    error: str | None = field(
        default=None,
        init=False,
    )

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc),
        init=False,
    )

    queued_at: datetime | None = field(
        default=None,
        init=False,
    )

    started_at: datetime | None = field(
        default=None,
        init=False,
    )

    completed_at: datetime | None = field(
        default=None,
        init=False,
    )

    def __init__(
        self,
        circuit: QuantumCircuit | None,
        shots: int = 1000,
        priority: int = 0,
        backend: str | None = None,
        metadata: dict[str, Any] | None = None,
        job_id: str | None = None,
    ) -> None:
        """
        Create a QuantumOS job.

        Args:
            circuit:
                Quantum circuit to execute.

                None is accepted for lightweight scheduler tests.

            shots:
                Number of execution shots.

            priority:
                Scheduling priority.

            backend:
                Optional backend name.

            metadata:
                Optional user metadata.

            job_id:
                Optional explicit job identifier. If omitted, a UUID
                is generated automatically.
        """

        self.circuit = circuit
        self.shots = shots
        self.priority = priority
        self.backend = backend

        self.metadata = (
            {}
            if metadata is None
            else metadata
        )

        self.id = (
            str(uuid4())
            if job_id is None
            else job_id
        )

        # A newly created job MUST remain CREATED.
        # Scheduler submission will transition it to QUEUED.
        self.status = JobStatus.CREATED

        self.result = None
        self.error = None

        self.created_at = _utc_now()

        self.queued_at = None
        self.started_at = None
        self.completed_at = None

        self._validate()

    @property
    def job_id(self) -> str:
        """
        Backwards-compatible alias for the job identifier.

        QuantumOS internally uses ``id`` while some integration/API
        code uses ``job_id``.
        """

        return self.id

    def _validate(self) -> None:
        """Validate job configuration."""

        # Scheduler tests intentionally use circuit=None.
        if self.circuit is not None and not isinstance(
            self.circuit,
            QuantumCircuit,
        ):
            raise TypeError(
                "circuit must be a QuantumCircuit or None"
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
            self.priority,
            int,
        ) or isinstance(
            self.priority,
            bool,
        ):
            raise TypeError(
                "priority must be an integer"
            )

        if self.backend is not None and not isinstance(
            self.backend,
            str,
        ):
            raise TypeError(
                "backend must be a string or None"
            )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise TypeError(
                "metadata must be a dictionary"
            )

        if not isinstance(
            self.id,
            str,
        ):
            raise TypeError(
                "job_id must be a string"
            )

        if not self.id:
            raise ValueError(
                "job_id cannot be empty"
            )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def queue(self) -> None:
        """
        Move the job from CREATED/SUBMITTED to QUEUED.
        """

        self._transition(
            expected=JobStatus.CREATED,
            new_status=JobStatus.QUEUED,
        )

        self.queued_at = _utc_now()

    def start(self) -> None:
        """
        Move the job from QUEUED to RUNNING.
        """

        self._transition(
            expected=JobStatus.QUEUED,
            new_status=JobStatus.RUNNING,
        )

        self.started_at = _utc_now()

    def complete(
        self,
        result: Any = None,
    ) -> None:
        """
        Mark a running job as completed.

        Args:
            result:
                Execution result returned by the backend.
        """

        self._transition(
            expected=JobStatus.RUNNING,
            new_status=JobStatus.COMPLETED,
        )

        self.result = result
        self.completed_at = _utc_now()

    def fail(
        self,
        error: Exception | str,
    ) -> None:
        """
        Mark a running job as failed.

        Args:
            error:
                Exception or error message describing the failure.
        """

        if self.status != JobStatus.RUNNING:
            raise InvalidJobStateError(
                "only running jobs can be failed"
            )

        self.status = JobStatus.FAILED

        if isinstance(error, Exception):
            self.error = str(error)
        else:
            self.error = error

        self.completed_at = _utc_now()

    def cancel(self) -> None:
        """
        Cancel a job that has not completed.
        """

        allowed_states = {
            JobStatus.CREATED,
            JobStatus.QUEUED,
            JobStatus.RUNNING,
        }

        if self.status not in allowed_states:
            raise InvalidJobStateError(
                f"cannot cancel job in state "
                f"'{self.status.value}'"
            )

        self.status = JobStatus.CANCELLED
        self.completed_at = _utc_now()

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------

    @property
    def is_finished(self) -> bool:
        """Return True if the job reached a terminal state."""

        return self.status in {
            JobStatus.COMPLETED,
            JobStatus.FAILED,
            JobStatus.CANCELLED,
        }

    @property
    def is_pending(self) -> bool:
        """Return True if the job is waiting to execute."""

        return self.status in {
            JobStatus.CREATED,
            JobStatus.QUEUED,
        }

    @property
    def duration_seconds(self) -> float | None:
        """
        Return execution duration in seconds.

        Returns None if execution has not started.
        """

        if self.started_at is None:
            return None

        end_time = self.completed_at

        if end_time is None:
            end_time = _utc_now()

        return (
            end_time - self.started_at
        ).total_seconds()

    def summary(self) -> dict[str, Any]:
        """
        Return a serializable summary of the job.
        """

        if self.circuit is None:
            num_qubits = None
            gate_count = 0
        else:
            num_qubits = self.circuit.num_qubits
            gate_count = self.circuit.gate_count()

        return {
            "id": self.id,
            "job_id": self.id,
            "status": self.status.value,
            "shots": self.shots,
            "priority": self.priority,
            "backend": self.backend,
            "num_qubits": num_qubits,
            "gate_count": gate_count,
            "created_at": self.created_at.isoformat(),
            "queued_at": (
                self.queued_at.isoformat()
                if self.queued_at
                else None
            ),
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
            "duration_seconds": self.duration_seconds,
            "error": self.error,
        }

    def _transition(
        self,
        *,
        expected: JobStatus,
        new_status: JobStatus,
    ) -> None:
        """Perform a validated lifecycle transition."""

        if self.status != expected:
            raise InvalidJobStateError(
                f"cannot transition job from "
                f"'{self.status.value}' to "
                f"'{new_status.value}'; "
                f"expected current state "
                f"'{expected.value}'"
            )

        self.status = new_status


def _utc_now() -> datetime:
    """Return the current UTC time."""

    return datetime.now(timezone.utc)