"""Unit tests for the QuantumOS scheduler."""

from qos.core.circuit import QuantumCircuit
from qos.scheduler.job import JobStatus, QuantumJob
from qos.scheduler.queue import JobQueue
from qos.scheduler.scheduler import Scheduler
from qos.scheduler.policies import FIFOPolicy


def make_job() -> QuantumJob:
    """Create a minimal valid quantum job."""
    return QuantumJob(
        circuit=QuantumCircuit(1),
        shots=1,
    )


def test_job_starts_in_created_state():
    """A newly created job should start in CREATED state."""
    job = make_job()

    assert job.status == JobStatus.CREATED


def test_job_can_be_queued():
    """A created job should be able to enter the queue."""
    job = make_job()

    job.queue()

    assert job.status == JobStatus.QUEUED
    assert job.queued_at is not None


def test_job_can_start():
    """A queued job should be able to start."""
    job = make_job()

    job.queue()
    job.start()

    assert job.status == JobStatus.RUNNING
    assert job.started_at is not None


def test_job_can_complete():
    """A running job should be able to complete."""
    job = make_job()

    job.queue()
    job.start()
    job.complete({"00": 1})

    assert job.status == JobStatus.COMPLETED
    assert job.result == {"00": 1}
    assert job.completed_at is not None
    assert job.is_finished is True


def test_job_can_fail():
    """A running job should be able to fail."""
    job = make_job()

    job.queue()
    job.start()
    job.fail("execution failed")

    assert job.status == JobStatus.FAILED
    assert job.error == "execution failed"
    assert job.completed_at is not None
    assert job.is_finished is True


def test_job_can_be_cancelled():
    """A created job should be cancellable."""
    job = make_job()

    job.cancel()

    assert job.status == JobStatus.CANCELLED
    assert job.completed_at is not None
    assert job.is_finished is True


def test_fifo_queue_preserves_submission_order():
    """FIFO queue should preserve submission order."""
    queue = JobQueue()

    job_a = make_job()
    job_b = make_job()
    job_c = make_job()

    queue.submit(job_a)
    queue.submit(job_b)
    queue.submit(job_c)

    assert queue.dequeue() is job_a
    assert queue.dequeue() is job_b
    assert queue.dequeue() is job_c


def test_queue_size():
    """The queue should report the number of waiting jobs."""
    queue = JobQueue()

    queue.submit(make_job())
    queue.submit(make_job())

    assert len(queue) == 2


def test_fifo_policy_selects_first_job():
    """FIFO policy should select the first available job."""
    policy = FIFOPolicy()

    jobs = [
        make_job(),
        make_job(),
        make_job(),
    ]

    selected = policy.select(jobs)

    assert selected is jobs[0]


def test_scheduler_can_submit_job():
    """The scheduler should accept a new job."""
    scheduler = Scheduler()

    job = make_job()

    scheduler.submit(job)

    assert job.status == JobStatus.QUEUED


def test_scheduler_queue_contains_submitted_job():
    """A submitted job should appear in the scheduler queue."""
    scheduler = Scheduler()

    job = make_job()

    scheduler.submit(job)

    assert len(scheduler.queue) == 1


def test_scheduler_selects_next_job():
    """The scheduler should select the next queued job."""
    scheduler = Scheduler()

    job_a = make_job()
    job_b = make_job()

    scheduler.submit(job_a)
    scheduler.submit(job_b)

    selected = scheduler.select_next()

    assert selected is job_a
    assert job_a.status == JobStatus.QUEUED
    assert len(scheduler.queue) == 2


def test_scheduler_next_job_preserves_fifo_order():
    """Repeated dispatching should preserve FIFO ordering."""
    scheduler = Scheduler()

    job_a = make_job()
    job_b = make_job()
    job_c = make_job()

    scheduler.submit(job_a)
    scheduler.submit(job_b)
    scheduler.submit(job_c)

    assert scheduler.dispatch_next() is job_a
    assert scheduler.dispatch_next() is job_b
    assert scheduler.dispatch_next() is job_c

    assert job_a.status == JobStatus.RUNNING
    assert job_b.status == JobStatus.RUNNING
    assert job_c.status == JobStatus.RUNNING
    assert scheduler.queue_size == 0
    assert scheduler.jobs_dispatched == 3