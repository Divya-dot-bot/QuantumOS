"""
QuantumOS Scheduler - Scheduling Policies

Defines scheduling-policy abstractions and built-in policies for
selecting the next quantum job to execute.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from qos.scheduler.job import QuantumJob


class SchedulingPolicy(ABC):
    """
    Abstract interface for QuantumOS scheduling policies.

    A policy receives the currently waiting jobs and selects which
    job should be executed next.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the policy's human-readable name."""
        raise NotImplementedError

    @abstractmethod
    def select(
        self,
        jobs: Sequence[QuantumJob],
    ) -> QuantumJob | None:
        """
        Select the next job.

        Args:
            jobs: Jobs currently waiting in the scheduler queue.

        Returns:
            The selected job, or None if no jobs are available.
        """
        raise NotImplementedError


class FIFOPolicy(SchedulingPolicy):
    """
    First-In, First-Out scheduling.

    The job that entered the queue first is selected first.
    """

    @property
    def name(self) -> str:
        """Return the policy name."""

        return "fifo"

    def select(
        self,
        jobs: Sequence[QuantumJob],
    ) -> QuantumJob | None:
        """Select the oldest waiting job."""

        if not jobs:
            return None

        return jobs[0]


class PriorityPolicy(SchedulingPolicy):
    """
    Priority-based scheduling.

    Jobs with higher priority values are selected first.

    Equal-priority jobs preserve their existing queue order.
    """

    @property
    def name(self) -> str:
        """Return the policy name."""

        return "priority"

    def select(
        self,
        jobs: Sequence[QuantumJob],
    ) -> QuantumJob | None:
        """Select the highest-priority job."""

        if not jobs:
            return None

        best_job = jobs[0]

        for job in jobs[1:]:
            if job.priority > best_job.priority:
                best_job = job

        return best_job


class ShortestJobFirstPolicy(SchedulingPolicy):
    """
    Select the job with the smallest estimated workload.

    For the MVP, workload is estimated using:

        number of gates × number of shots

    This is only a heuristic. A future implementation can use
    backend-specific execution-time estimates.
    """

    @property
    def name(self) -> str:
        """Return the policy name."""

        return "shortest_job_first"

    def select(
        self,
        jobs: Sequence[QuantumJob],
    ) -> QuantumJob | None:
        """Select the job with the smallest estimated workload."""

        if not jobs:
            return None

        return min(
            jobs,
            key=self._workload,
        )

    @staticmethod
    def _workload(
        job: QuantumJob,
    ) -> int:
        """Estimate the computational workload of a job."""

        return (
            job.circuit.gate_count()
            * job.shots
        )


class HighestPriorityThenShortestPolicy(
    SchedulingPolicy
):
    """
    Hybrid policy.

    Higher priority always wins.

    When priorities are equal, the job with the smaller estimated
    workload is selected.
    """

    @property
    def name(self) -> str:
        """Return the policy name."""

        return "priority_then_shortest"

    def select(
        self,
        jobs: Sequence[QuantumJob],
    ) -> QuantumJob | None:
        """Select using priority first and workload second."""

        if not jobs:
            return None

        return min(
            jobs,
            key=lambda job: (
                -job.priority,
                self._workload(job),
            ),
        )

    @staticmethod
    def _workload(
        job: QuantumJob,
    ) -> int:
        """Estimate a job's workload."""

        return (
            job.circuit.gate_count()
            * job.shots
        )


def get_policy(
    name: str,
) -> SchedulingPolicy:
    """
    Create a scheduling policy by name.

    Supported names:

        fifo
        priority
        shortest_job_first
        priority_then_shortest

    Args:
        name: Policy name.

    Returns:
        A SchedulingPolicy instance.

    Raises:
        ValueError: If the policy name is unknown.
        TypeError: If name is not a string.
    """

    if not isinstance(name, str):
        raise TypeError(
            "policy name must be a string"
        )

    normalized = name.strip().lower()

    policies: dict[str, type[SchedulingPolicy]] = {
        "fifo": FIFOPolicy,
        "priority": PriorityPolicy,
        "shortest_job_first": ShortestJobFirstPolicy,
        "priority_then_shortest": (
            HighestPriorityThenShortestPolicy
        ),
    }

    policy_class = policies.get(normalized)

    if policy_class is None:
        supported = ", ".join(
            sorted(policies)
        )

        raise ValueError(
            f"unknown scheduling policy '{name}'. "
            f"Supported policies: {supported}"
        )

    return policy_class()