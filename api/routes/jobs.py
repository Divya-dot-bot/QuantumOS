"""
QuantumOS API - Job Routes

REST endpoints for quantum job submission,
inspection, and execution.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status

from api.schemas.jobs import (
    JobCreateRequest,
    JobResponse,
    JobResultResponse,
    JobSubmissionResponse,
)
from api.dependencies import get_runtime
from qos.scheduler.job import QuantumJob
from qos.compiler.parser import parse_program
router = APIRouter()


# ----------------------------------------------------------------------
# Submit job
# ----------------------------------------------------------------------


@router.post(
    "",
    response_model=JobSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_job(
    request: JobCreateRequest,
) -> JobSubmissionResponse:
    """
    Submit a new quantum job.
    """

    runtime = get_runtime()

    try:
        circuit = request.circuit

        if isinstance(circuit, str):
         circuit = parse_program(circuit)

        job = QuantumJob(
    circuit=circuit,
    shots=request.shots,
    priority=request.priority,
    backend=request.backend,
    metadata=request.metadata,
)

        job_id = runtime.submit(job)

    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return JobSubmissionResponse(
        job_id=job_id,
        status=job.status.value,
        message="Quantum job submitted successfully.",
    )


# ----------------------------------------------------------------------
# List jobs
# ----------------------------------------------------------------------


@router.get(
    "",
    response_model=list[JobResponse],
)
def list_jobs() -> list[JobResponse]:
    """
    Return currently pending jobs.
    """

    runtime = get_runtime()

    jobs = runtime.pending_jobs()

    return [
        _job_to_response(job)
        for job in jobs
    ]

# ----------------------------------------------------------------------
# Scheduler status
# ----------------------------------------------------------------------


@router.get(
    "/scheduler/status",
)
def scheduler_status() -> dict[str, Any]:
    """
    Return the current QuantumOS scheduler state.
    """

    runtime = get_runtime()

    statistics = runtime.scheduler.statistics()

    return {
        "runtime_status": runtime.status.value,
        "policy": statistics["policy"],
        "queue_size": statistics["queue_size"],
        "jobs_submitted": statistics["jobs_submitted"],
        "jobs_dispatched": statistics["jobs_dispatched"],
        "last_decision": statistics["last_decision"],
    }
# ----------------------------------------------------------------------
# Get job
# ----------------------------------------------------------------------


@router.get(
    "/{job_id}",
    response_model=JobResponse,
)
def get_job(
    job_id: str,
) -> JobResponse:
    """
    Return information about a specific job.
    """

    runtime = get_runtime()

    job = runtime.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )

    return _job_to_response(job)


# ----------------------------------------------------------------------
# Run job
# ----------------------------------------------------------------------


@router.post(
    "/{job_id}/run",
    response_model=JobResultResponse,
)
def run_job(
    job_id: str,
) -> JobResultResponse:
    """
    Execute a specific queued job.

    The MVP scheduler currently dispatches the next available
    job, so the requested job must be the next job in the queue.
    """

    runtime = get_runtime()

    job = runtime.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found.",
        )

    if runtime.status.value != "running":
        runtime.start()

    try:
        execution = runtime.run_next()

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    if execution is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No queued job is available for execution.",
        )

    if execution.job_id != job_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Job '{job_id}' was not the next scheduled job."
            ),
        )

    return JobResultResponse(
        job_id=execution.job_id,
        status=job.status.value,
        backend_id=execution.backend_id,
        backend_name=execution.backend_name,
        shots=execution.result.shots,
        counts=execution.result.counts,
        metadata=execution.result.metadata,
    )


# ----------------------------------------------------------------------
# Runtime history
# ----------------------------------------------------------------------


@router.get(
    "/history/all",
)
def execution_history() -> list[dict[str, Any]]:
    """
    Return completed execution history.
    """

    runtime = get_runtime()

    return [
        execution.as_dict()
        for execution in runtime.execution_history()
    ]


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _job_to_response(
    job: QuantumJob,
) -> JobResponse:
    """
    Convert a QuantumJob into an API response.
    """

    return JobResponse(
        job_id=job.id,
        status=job.status.value,
        shots=job.shots,
        priority=job.priority,
        backend=getattr(
            job,
            "backend",
            None,
        ),
        submitted_at=getattr(
            job,
            "submitted_at",
            None,
        ),
        started_at=getattr(
            job,
            "started_at",
            None,
        ),
        completed_at=getattr(
            job,
            "completed_at",
            None,
        ),
        error=getattr(
            job,
            "error",
            None,
        ),
        metadata=getattr(
            job,
            "metadata",
            {},
        ),
    )