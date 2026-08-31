"""
QuantumOS Runtime - Executor

Executes compiled quantum circuits on allocated backends.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from qos.compiler.transpiler import ExecutableCircuit
from qos.resources.backend import (
    Backend,
    BackendResult,
)
from qos.resources.manager import (
    ResourceAllocation,
    ResourceManager,
)
from qos.scheduler.job import QuantumJob


class ExecutionError(RuntimeError):
    """Raised when quantum job execution fails."""


@dataclass(frozen=True)
class ExecutionResult:
    """
    Standardized result produced by the QuantumOS executor.
    """

    job_id: str
    backend_id: str
    backend_name: str
    counts: dict[str, int]
    shots: int
    metadata: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        """Return the result as a dictionary."""

        return {
            "job_id": self.job_id,
            "backend_id": self.backend_id,
            "backend_name": self.backend_name,
            "counts": dict(self.counts),
            "shots": self.shots,
            "metadata": dict(self.metadata),
        }


class Executor:
    """
    Executes QuantumOS jobs using allocated resources.

    The Executor does not decide which job should run or which
    backend should be selected. Those responsibilities belong to
    the Scheduler and ResourceManager respectively.
    """

    def __init__(
        self,
        resource_manager: ResourceManager,
    ) -> None:
        """
        Create an Executor.

        Args:
            resource_manager:
                Resource manager responsible for backend allocation.
        """

        if not isinstance(
            resource_manager,
            ResourceManager,
        ):
            raise TypeError(
                "resource_manager must be a ResourceManager"
            )

        self.resource_manager = resource_manager

    def execute(
        self,
        job: QuantumJob,
        circuit: ExecutableCircuit,
    ) -> ExecutionResult:
        """
        Execute a quantum job.

        The job must already have a resource allocation.

        Args:
            job:
                QuantumOS job being executed.

            circuit:
                Compiled executable circuit.

        Returns:
            ExecutionResult.

        Raises:
            ExecutionError:
                If the job has no allocation or backend execution fails.
        """

        self._validate_inputs(
            job,
            circuit,
        )

        allocation = (
            self.resource_manager.get_allocation(
                job.id
            )
        )

        if allocation is None:
            raise ExecutionError(
                f"job '{job.id}' has no resource allocation"
            )

        backend = (
            self.resource_manager.allocated_backend(
                job.id
            )
        )

        if backend is None:
            raise ExecutionError(
                f"backend for job '{job.id}' "
                "could not be found"
            )

        if not backend.is_busy:
            raise ExecutionError(
                f"backend '{backend.backend_id}' "
                "is not allocated for execution"
            )

        try:
            backend_result = backend.execute(
                circuit,
                shots=job.shots,
                job_id=job.id,
            )
        except Exception as exc:
            raise ExecutionError(
                f"execution failed for job '{job.id}': {exc}"
            ) from exc

        return self._build_result(
            job,
            allocation,
            backend,
            backend_result,
        )

    @staticmethod
    def _validate_inputs(
        job: QuantumJob,
        circuit: ExecutableCircuit,
    ) -> None:
        """Validate executor inputs."""

        if not isinstance(
            job,
            QuantumJob,
        ):
            raise TypeError(
                "job must be a QuantumJob"
            )

        if not isinstance(
            circuit,
            ExecutableCircuit,
        ):
            raise TypeError(
                "circuit must be an ExecutableCircuit"
            )

    @staticmethod
    def _build_result(
        job: QuantumJob,
        allocation: ResourceAllocation,
        backend: Backend,
        backend_result: BackendResult,
    ) -> ExecutionResult:
        """Convert a backend result into an executor result."""

        return ExecutionResult(
            job_id=job.id,
            backend_id=allocation.backend_id,
            backend_name=backend.name,
            counts=dict(
                backend_result.counts
            ),
            shots=backend_result.shots,
            metadata={
                **backend_result.metadata,
                "resource_type": (
                    backend.resource_type.value
                ),
            },
        )