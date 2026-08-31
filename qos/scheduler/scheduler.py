"""
QuantumOS Scheduler - Scheduler

Coordinates quantum jobs, queues, and scheduling policies.
"""

from __future__ import annotations

from dataclasses import dataclass

from qos.scheduler.job import QuantumJob
from qos.scheduler.policies import (
    FIFOPolicy,
    SchedulingPolicy,
)
from qos.scheduler.queue import JobQueue


@dataclass(frozen=True)
class SchedulingDecision:
    """Represents a scheduler decision."""

    job_id: str
    policy: str
    queue_size: int


class Scheduler:
    """
    QuantumOS job scheduler.

    Responsibilities:

    * Accept jobs.
    * Maintain the waiting queue.
    * Apply a scheduling policy.
    * Select the next job.
    * Dispatch jobs.
    * Track scheduler statistics.
    """

    def __init__(
        self,
        queue: JobQueue | None = None,
        policy: SchedulingPolicy | None = None,
    ) -> None:
        self.queue = queue if queue is not None else JobQueue()

        self.policy = (
            policy
            if policy is not None
            else FIFOPolicy()
        )

        self._jobs_submitted = 0
        self._jobs_dispatched = 0
        self._last_decision: SchedulingDecision | None = None

    # ------------------------------------------------------------------
    # Job submission
    # ------------------------------------------------------------------

    def submit(self, job: QuantumJob) -> str:
        """Submit a quantum job."""

        self.queue.submit(job)
        self._jobs_submitted += 1

        return job.id

    # ------------------------------------------------------------------
    # Scheduling
    # ------------------------------------------------------------------

    def select_next(self) -> QuantumJob | None:
        """
        Select the next job according to the active policy.

        The selected job remains in the queue.
        """

        jobs = self.queue.snapshot()

        if not jobs:
            return None

        job = self.policy.select(jobs)

        if job is None:
            return None

        self._last_decision = SchedulingDecision(
            job_id=job.id,
            policy=self.policy.name,
            queue_size=len(jobs),
        )

        return job

    def dispatch_next(self) -> QuantumJob | None:
        """
        Remove and return the next job for execution.

        The job is transitioned from QUEUED to RUNNING.
        """

        selected = self.select_next()

        if selected is None:
            return None

        job = self._remove_selected_job(selected)

        job.start()

        self._jobs_dispatched += 1

        return job

    def next_job(self) -> QuantumJob | None:
        """
        Backward-compatible scheduler API.

        Returns the next job and transitions it to RUNNING.
        """

        return self.dispatch_next()

    # ------------------------------------------------------------------
    # Cancellation
    # ------------------------------------------------------------------

    def cancel(self, job_id: str) -> QuantumJob | None:
        """Cancel a queued job."""

        job = self.queue.find(job_id)

        if job is None:
            return None

        removed = self.queue.remove(job_id)

        return removed

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    def pending_jobs(self) -> list[QuantumJob]:
        """Return all jobs currently waiting."""

        return self.queue.snapshot()

    def get_job(self, job_id: str) -> QuantumJob | None:
        """Find a currently queued job by ID."""

        return self.queue.find(job_id)

    @property
    def queue_size(self) -> int:
        """Return the number of waiting jobs."""

        return len(self.queue)

    @property
    def jobs_submitted(self) -> int:
        """Return total number of submitted jobs."""

        return self._jobs_submitted

    @property
    def jobs_dispatched(self) -> int:
        """Return total number of dispatched jobs."""

        return self._jobs_dispatched

    @property
    def last_decision(self) -> SchedulingDecision | None:
        """Return the most recent scheduling decision."""

        return self._last_decision

    def statistics(self) -> dict[str, object]:
        """Return scheduler statistics."""

        return {
            "policy": self.policy.name,
            "queue_size": self.queue_size,
            "jobs_submitted": self.jobs_submitted,
            "jobs_dispatched": self.jobs_dispatched,
            "last_decision": (
                self.last_decision.job_id
                if self.last_decision is not None
                else None
            ),
        }

    # ------------------------------------------------------------------
    # Policy management
    # ------------------------------------------------------------------

    def set_policy(
        self,
        policy: SchedulingPolicy,
    ) -> None:
        """Replace the active scheduling policy."""

        if not isinstance(policy, SchedulingPolicy):
            raise TypeError(
                "policy must be a SchedulingPolicy"
            )

        self.policy = policy

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _remove_selected_job(
        self,
        selected: QuantumJob,
    ) -> QuantumJob:
        """Remove a selected job from the underlying queue."""

        removed = self.queue.remove_without_cancel(
            selected.id
        )

        if removed is None:
            raise RuntimeError(
                "selected job disappeared from queue"
            )

        return removed


def create_scheduler(
    policy: SchedulingPolicy | None = None,
) -> Scheduler:
    """Convenience factory for creating a Scheduler."""

    return Scheduler(policy=policy)