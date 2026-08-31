"""
QuantumOS Runtime - Runtime Coordinator

Provides the top-level runtime responsible for coordinating
scheduling, compilation, resource allocation, and execution.
"""

from __future__ import annotations
from qos.core.circuit import QuantumCircuit
from dataclasses import dataclass
from enum import Enum
from typing import Any

from qos.compiler.optimizer import optimize
from qos.compiler.parser import parse
from qos.compiler.transpiler import transpile
from qos.resources.manager import (
    ResourceAllocation,
    ResourceManager,
)
from qos.runtime.executor import (
    ExecutionError,
    ExecutionResult,
    Executor,
)
from qos.runtime.worker import (
    Worker,
    WorkerPool,
    WorkerResult,
)
from qos.scheduler.job import (
    JobStatus,
    QuantumJob,
)
from qos.scheduler.scheduler import Scheduler


class RuntimeStatus(str, Enum):
    """Lifecycle states of the QuantumOS runtime."""

    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"


class RuntimeErrorBase(RuntimeError):
    """Base exception for QuantumOS runtime errors."""


@dataclass(frozen=True)
class RuntimeExecution:
    """
    Complete runtime execution record.

    Contains information from scheduling, resource allocation,
    and backend execution.
    """

    job_id: str
    worker_id: str
    backend_id: str
    backend_name: str
    result: ExecutionResult

    def as_dict(self) -> dict[str, Any]:
        """Return a serializable execution record."""

        return {
            "job_id": self.job_id,
            "worker_id": self.worker_id,
            "backend_id": self.backend_id,
            "backend_name": self.backend_name,
            "result": self.result.as_dict(),
        }


class QuantumRuntime:
    """
    Top-level QuantumOS runtime.

    Coordinates:

    * Scheduler
    * Compiler
    * ResourceManager
    * Executor
    * WorkerPool

    The runtime provides the high-level execution API for the MVP.
    """

    def __init__(
        self,
        scheduler: Scheduler | None = None,
        resource_manager: ResourceManager | None = None,
        worker_pool: WorkerPool | None = None,
    ) -> None:
        """
        Create a QuantumOS runtime.

        Components are created automatically when omitted.
        """

        self.scheduler = (
            scheduler
            if scheduler is not None
            else Scheduler()
        )

        self.resource_manager = (
            resource_manager
            if resource_manager is not None
            else ResourceManager()
        )

        self.executor = Executor(
            self.resource_manager
        )
        if worker_pool is not None:
             self.worker_pool = worker_pool
        else:
             self.worker_pool = WorkerPool(
                workers=[
                    Worker(
                        worker_id="worker-0",
                        executor=self.executor,
                    )
                ]
            )

        self.status = RuntimeStatus.STOPPED

        self._execution_history: list[
            RuntimeExecution
        ] = []
        self._jobs: dict[str, QuantumJob] = {}
    # ------------------------------------------------------------------
    # Runtime lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the runtime."""

        if self.status == RuntimeStatus.RUNNING:
            return

        if self.status == RuntimeStatus.STOPPED:
            self.worker_pool.start_all()

        self.status = RuntimeStatus.RUNNING

    def pause(self) -> None:
        """Pause scheduling and execution."""

        if self.status != RuntimeStatus.RUNNING:
            raise RuntimeErrorBase(
                "runtime must be running before it can be paused"
            )

        self.status = RuntimeStatus.PAUSED

    def stop(self) -> None:
        """
        Stop the runtime.

        Idle workers are stopped. Busy workers are left alone.
        """

        self.worker_pool.stop_all()

        self.status = RuntimeStatus.STOPPED

    # ------------------------------------------------------------------
    # Job submission
    # ------------------------------------------------------------------

    def submit(
        self,
        job: QuantumJob,
    ) -> str:
        """
        Submit a quantum job to the runtime.

        Returns:
            Job ID.
        """

        if not isinstance(
            job,
            QuantumJob,
        ):
            raise TypeError(
                "job must be a QuantumJob"
            )

        job_id = self.scheduler.submit(
           job
)

        self._jobs[job.id] = job

        return job_id

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def run_next(self) -> RuntimeExecution | None:
        """
        Execute the next scheduled job.

        Pipeline:

            Scheduler
                ↓
            Compiler
                ↓
            ResourceManager
                ↓
            Worker
                ↓
            Executor
                ↓
            Backend

        Returns:
            RuntimeExecution or None if no job is waiting.
        """

        if self.status != RuntimeStatus.RUNNING:
            raise RuntimeErrorBase(
                "runtime must be running before executing jobs"
            )

        job = self.scheduler.dispatch_next()

        if job is None:
            return None

        allocation: ResourceAllocation | None = None

        try:
            executable = self._compile(
                job
            )

            allocation = (
                self.resource_manager.allocate(
                    job,
                    executable,
                )
            )

            worker = (
                self.worker_pool.available_worker()
            )

            if worker is None:
                raise RuntimeErrorBase(
                    "no available runtime worker"
                )

            worker_result = worker.process(
                job,
                executable,
            )

            self._complete_job(
                job,
                worker_result,
            )

            execution = RuntimeExecution(
                job_id=job.id,
                worker_id=worker_result.worker_id,
                backend_id=allocation.backend_id,
                backend_name=allocation.backend_name,
                result=worker_result.execution,
            )

            self._execution_history.append(
                execution
            )

            return execution

        except Exception as exc:
            self._fail_job(
                job,
                exc,
            )

            raise

        finally:
            if allocation is not None:
                self.resource_manager.release(
                    job.id
                )

    def run_all(self) -> list[RuntimeExecution]:
        """
        Execute all currently queued jobs.

        Returns:
            Execution records for successfully completed jobs.

        Raises:
            Exception:
                If a job fails during execution.
        """

        executions: list[
            RuntimeExecution
        ] = []

        while self.scheduler.queue_size > 0:
            execution = self.run_next()

            if execution is None:
                break

            executions.append(
                execution
            )

        return executions

    # ------------------------------------------------------------------
    # Compilation
    # ------------------------------------------------------------------

    @staticmethod
    def _compile(
        job: QuantumJob,
    ):
        """
        Compile a job's circuit into an executable circuit.
        """

        if not isinstance(
            job.circuit,
            QuantumCircuit,
        ):
            raise TypeError(
                "job.circuit must be a QuantumCircuit"
            )

        optimized = optimize(
            job.circuit
        )

        return transpile(
            optimized
        )

    # ------------------------------------------------------------------
    # Job lifecycle
    # ------------------------------------------------------------------

    @staticmethod
    def _complete_job(
        job: QuantumJob,
        worker_result: WorkerResult,
    ) -> None:
        """Mark a job as completed."""

        job.complete(
            worker_result.execution
        )

    @staticmethod
    def _fail_job(
        job: QuantumJob,
        error: Exception,
    ) -> None:
        """Mark a running job as failed."""

        if job.status == JobStatus.RUNNING:
            job.fail(error)

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    def get_job(
    self,
    job_id: str,
) -> QuantumJob | None:
     """Return a submitted job by ID."""

     return self._jobs.get(
        job_id
    )

    def pending_jobs(self) -> list[QuantumJob]:
        """Return currently pending jobs."""

        return self.scheduler.pending_jobs()

    def execution_history(
        self,
    ) -> list[RuntimeExecution]:
        """Return completed runtime executions."""

        return list(
            self._execution_history
        )

    def statistics(self) -> dict[str, Any]:
        """Return runtime statistics."""

        return {
            "status": self.status.value,
            "scheduler": self.scheduler.statistics(),
            "resources": self.resource_manager.summary(),
            "workers": {
                "total": len(self.worker_pool),
                "idle": len(
                    self.worker_pool.idle_workers()
                ),
                "busy": len(
                    self.worker_pool.busy_workers()
                ),
            },
            "executions": len(
                self._execution_history
            ),
        }