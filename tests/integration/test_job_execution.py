"""Integration tests for the QuantumOS job execution pipeline."""

from qos.core.circuit import QuantumCircuit
from qos.core.qvm import QuantumVirtualMachine
from qos.scheduler.job import JobStatus, QuantumJob
from qos.scheduler.scheduler import Scheduler


def create_bell_circuit() -> QuantumCircuit:
    """Create a simple two-qubit Bell-state circuit."""
    circuit = QuantumCircuit(2)

    circuit.h(0)
    circuit.cx(0, 1)

    return circuit


def test_bell_job_can_be_created():
    """A quantum job should accept a valid circuit."""
    circuit = create_bell_circuit()

    job = QuantumJob(
        job_id="integration-bell-1",
        circuit=circuit,
        shots=100,
    )

    assert job.job_id == "integration-bell-1"
    assert job.circuit is circuit
    assert job.shots == 100
    assert job.status == JobStatus.SUBMITTED


def test_job_can_move_through_scheduler():
    """A submitted job should enter the scheduler queue."""
    circuit = create_bell_circuit()

    job = QuantumJob(
        job_id="integration-bell-2",
        circuit=circuit,
        shots=100,
    )

    scheduler = Scheduler()
    scheduler.submit(job)

    assert job.status == JobStatus.QUEUED

    selected_job = scheduler.next_job()

    assert selected_job is job


def test_bell_circuit_executes_on_qvm():
    """A Bell-state circuit should execute successfully on the QVM."""
    circuit = create_bell_circuit()

    qvm = QuantumVirtualMachine()

    result = qvm.run(
        circuit,
        shots=100,
    )

    assert result is not None


def test_bell_state_produces_expected_basis_states():
    """An ideal Bell state should produce 00 and 11 outcomes."""
    circuit = create_bell_circuit()

    qvm = QuantumVirtualMachine()

    result = qvm.run(
        circuit,
        shots=1000,
    )

    if hasattr(result, "counts"):
        counts = result.counts
    else:
        counts = result

    assert isinstance(counts, dict)

    assert set(counts.keys()).issubset({"00", "11"})

    assert "00" in counts
    assert "11" in counts

    assert counts["00"] > 0
    assert counts["11"] > 0


def test_end_to_end_bell_job():
    """Test the basic QuantumOS job-to-execution workflow."""
    circuit = create_bell_circuit()

    job = QuantumJob(
        job_id="integration-bell-3",
        circuit=circuit,
        shots=500,
    )

    scheduler = Scheduler()
    scheduler.submit(job)

    selected_job = scheduler.next_job()

    assert selected_job is job

    qvm = QuantumVirtualMachine()

    result = qvm.run(
        selected_job.circuit,
        shots=selected_job.shots,
    )

    assert result is not None

    if hasattr(result, "counts"):
        counts = result.counts
    else:
        counts = result

    assert isinstance(counts, dict)
    assert sum(counts.values()) == 500