"""
QuantumOS Scheduler - Job Queue

Provides an in-memory queue for QuantumOS jobs.

The queue is intentionally independent from the scheduling policy.
The scheduler decides how jobs should be selected; the queue manages
which jobs are currently waiting.
"""

from __future__ import annotations

from collections import deque
from typing import Iterator

from qos.scheduler.job import (
    JobStatus,
    QuantumJob,
)


class JobQueue:
    """
    In-memory queue for pending QuantumOS jobs.

    The default behavior is FIFO.

    Priority-based scheduling can be implemented by the Scheduler
    using the queue's inspection and removal methods.
    """

    def __init__(self) -> None:
        """Create an empty job queue."""

        self._jobs: deque[QuantumJob] = deque()

    def submit(
        self,
        job: QuantumJob,
    ) -> None:
        """
        Add a job to the queue.

        A job must be in the CREATED state when submitted.
        """

        self._validate_job(job)

        if job.status != JobStatus.CREATED:
            raise ValueError(
                f"cannot submit job in state "
                f"'{job.status.value}'"
            )

        job.queue()

        self._jobs.append(job)

    def dequeue(self) -> QuantumJob | None:
        """
        Remove and return the oldest queued job.

        Returns:
            The next queued job, or None if the queue is empty.
        """

        if not self._jobs:
            return None

        return self._jobs.popleft()

    def peek(self) -> QuantumJob | None:
        """
        Return the oldest queued job without removing it.
        """

        if not self._jobs:
            return None

        return self._jobs[0]

    def remove(
        self,
        job_id: str,
    ) -> QuantumJob | None:
        """
        Remove a specific job from the queue.

        A removed job is marked as cancelled.

        Args:
            job_id: ID of the job to remove.

        Returns:
            Removed job, or None if not found.
        """

        for job in self._jobs:
            if job.id == job_id:
                self._jobs.remove(job)

                job.cancel()

                return job

        return None

    def remove_without_cancel(
        self,
        job_id: str,
    ) -> QuantumJob | None:
        """
        Remove a specific job without changing its state.

        This is used by the Scheduler when it has selected a
        queued job for execution. The Scheduler will transition
        the job from QUEUED to RUNNING separately.
        """

        for job in self._jobs:
            if job.id == job_id:
                self._jobs.remove(job)
                return job

        return None

    def find(
        self,
        job_id: str,
    ) -> QuantumJob | None:
        """
        Find a queued job by ID without removing it.
        """

        for job in self._jobs:
            if job.id == job_id:
                return job

        return None

    def clear(self) -> list[QuantumJob]:
        """
        Remove all jobs from the queue.

        All removed jobs are cancelled.

        Returns:
            List of cancelled jobs.
        """

        removed: list[QuantumJob] = []

        while self._jobs:
            job = self._jobs.popleft()

            if not job.is_finished:
                job.cancel()

            removed.append(job)

        return removed

    def snapshot(self) -> list[QuantumJob]:
        """
        Return a list of currently queued jobs.

        The queue itself is not modified.
        """

        return list(self._jobs)

    def __len__(self) -> int:
        """Return the number of queued jobs."""

        return len(self._jobs)

    def __bool__(self) -> bool:
        """Return True when at least one job is queued."""

        return bool(self._jobs)

    def __iter__(self) -> Iterator[QuantumJob]:
        """Iterate over queued jobs without removing them."""

        return iter(self._jobs)

    def __contains__(
        self,
        job_id: str,
    ) -> bool:
        """Return True if a job ID exists in the queue."""

        return self.find(job_id) is not None

    @staticmethod
    def _validate_job(
        job: QuantumJob,
    ) -> None:
        """Validate a job argument."""

        if not isinstance(job, QuantumJob):
            raise TypeError(
                "job must be a QuantumJob"
            )


class PriorityJobQueue(JobQueue):
    """
    Priority-aware job queue.

    Higher priority values are returned first.

    Jobs with equal priority preserve FIFO submission order.
    """

    def dequeue(self) -> QuantumJob | None:
        """
        Remove the highest-priority queued job.

        Equal-priority jobs are handled in FIFO order.
        """

        if not self._jobs:
            return None

        best_index = 0
        best_job = self._jobs[0]

        for index, job in enumerate(self._jobs):
            if job.priority > best_job.priority:
                best_index = index
                best_job = job

        del self._jobs[best_index]

        return best_job

    def peek(self) -> QuantumJob | None:
        """
        Return the highest-priority queued job without removing it.
        """

        if not self._jobs:
            return None

        best_job = self._jobs[0]

        for job in self._jobs:
            if job.priority > best_job.priority:
                best_job = job

        return best_job