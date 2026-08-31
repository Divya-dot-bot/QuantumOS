"""
QuantumOS Runtime - Worker

Defines the worker abstraction responsible for processing
dispatched quantum jobs.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable

from qos.compiler.transpiler import ExecutableCircuit
from qos.runtime.executor import (
    ExecutionError,
    ExecutionResult,
    Executor,
)
from qos.scheduler.job import QuantumJob


class WorkerStatus(str, Enum):
    """Lifecycle states of a runtime worker."""

    IDLE = "idle"
    BUSY = "busy"
    STOPPED = "stopped"


class WorkerError(RuntimeError):
    """Raised when a worker cannot process a job."""


@dataclass(frozen=True)
class WorkerResult:
    """Result returned after a worker processes a job."""

    worker_id: str
    execution: ExecutionResult

    def as_dict(self) -> dict[str, Any]:
        """Return a serializable representation."""

        return {
            "worker_id": self.worker_id,
            "execution": self.execution.as_dict(),
        }


class Worker:
    """
    Processes QuantumOS jobs using an Executor.

    A worker handles one job at a time in the MVP.
    """

    def __init__(
        self,
        worker_id: str,
        executor: Executor,
    ) -> None:
        """
        Create a runtime worker.

        Args:
            worker_id:
                Unique worker identifier.

            executor:
                Executor used to execute jobs.
        """

        if not isinstance(worker_id, str):
            raise TypeError(
                "worker_id must be a string"
            )

        if not worker_id.strip():
            raise ValueError(
                "worker_id cannot be empty"
            )

        if not isinstance(
            executor,
            Executor,
        ):
            raise TypeError(
                "executor must be an Executor"
            )

        self.worker_id = worker_id
        self.executor = executor
        self.status = WorkerStatus.IDLE
        self.current_job: QuantumJob | None = None

    @property
    def is_idle(self) -> bool:
        """Return True when the worker is idle."""

        return self.status == WorkerStatus.IDLE

    @property
    def is_busy(self) -> bool:
        """Return True when the worker is processing a job."""

        return self.status == WorkerStatus.BUSY

    @property
    def is_stopped(self) -> bool:
        """Return True when the worker is stopped."""

        return self.status == WorkerStatus.STOPPED

    def start(self) -> None:
        """Start the worker."""

        if self.status == WorkerStatus.STOPPED:
            raise WorkerError(
                f"worker '{self.worker_id}' is stopped"
            )

        self.status = WorkerStatus.IDLE

    def stop(self) -> None:
        """
        Stop the worker.

        A busy worker cannot be stopped in the MVP.
        """

        if self.status == WorkerStatus.BUSY:
            raise WorkerError(
                f"worker '{self.worker_id}' is currently busy"
            )

        self.status = WorkerStatus.STOPPED

    def process(
        self,
        job: QuantumJob,
        circuit: ExecutableCircuit,
    ) -> WorkerResult:
        """
        Process one quantum job.

        Args:
            job:
                Dispatched QuantumOS job.

            circuit:
                Compiled executable circuit.

        Returns:
            WorkerResult.

        Raises:
            WorkerError:
                If the worker cannot process the job.
        """

        if self.status == WorkerStatus.STOPPED:
            raise WorkerError(
                f"worker '{self.worker_id}' is stopped"
            )

        if self.status == WorkerStatus.BUSY:
            raise WorkerError(
                f"worker '{self.worker_id}' is already busy"
            )

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

        if job.status.value != "running":
            raise WorkerError(
                f"job '{job.id}' must be running before "
                "a worker can process it"
            )

        self.status = WorkerStatus.BUSY
        self.current_job = job

        try:
            execution = self.executor.execute(
                job,
                circuit,
            )

            return WorkerResult(
                worker_id=self.worker_id,
                execution=execution,
            )

        except ExecutionError:
            raise

        finally:
            self.status = WorkerStatus.IDLE
            self.current_job = None


class WorkerPool:
    """
    Collection of runtime workers.

    The MVP uses synchronous workers, but the abstraction is
    designed so asynchronous execution can be added later.
    """

    def __init__(
        self,
        workers: list[Worker] | None = None,
    ) -> None:
        """Create a worker pool."""

        self._workers: dict[str, Worker] = {}

        if workers is not None:
            for worker in workers:
                self.add(worker)

    def add(
        self,
        worker: Worker,
    ) -> None:
        """Add a worker to the pool."""

        if not isinstance(
            worker,
            Worker,
        ):
            raise TypeError(
                "worker must be a Worker"
            )

        if worker.worker_id in self._workers:
            raise ValueError(
                f"worker '{worker.worker_id}' "
                "already exists"
            )

        self._workers[
            worker.worker_id
        ] = worker

    def remove(
        self,
        worker_id: str,
    ) -> Worker | None:
        """Remove a worker from the pool."""

        worker = self._workers.get(worker_id)

        if worker is not None and worker.is_busy:
            raise WorkerError(
                f"worker '{worker_id}' is busy"
            )

        return self._workers.pop(
            worker_id,
            None,
        )

    def get(
        self,
        worker_id: str,
    ) -> Worker | None:
        """Return a worker by ID."""

        return self._workers.get(
            worker_id
        )

    def idle_workers(self) -> list[Worker]:
        """Return all idle workers."""

        return [
            worker
            for worker in self._workers.values()
            if worker.is_idle
        ]

    def busy_workers(self) -> list[Worker]:
        """Return all busy workers."""

        return [
            worker
            for worker in self._workers.values()
            if worker.is_busy
        ]

    def available_worker(self) -> Worker | None:
        """Return one available worker."""

        idle = self.idle_workers()

        if not idle:
            return None

        return idle[0]

    def start_all(self) -> None:
        """Start all workers."""

        for worker in self._workers.values():
            worker.start()

    def stop_all(self) -> None:
        """Stop all idle workers."""

        for worker in self._workers.values():
            if worker.is_idle:
                worker.stop()

    def __len__(self) -> int:
        """Return number of workers."""

        return len(self._workers)

    def __iter__(self):
        """Iterate over workers."""

        return iter(
            self._workers.values()
        )