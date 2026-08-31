"""
QuantumOS - Quantum Virtual Machine Tests

Unit tests for the Quantum Virtual Machine.
"""

import math

import pytest

from qos.core import QuantumCircuit, QuantumVirtualMachine


class TestQuantumVirtualMachineInitialization:
    """Tests for QVM initialization."""

    def test_qvm_starts_without_state(self) -> None:
        """A new QVM should not have an executed state."""

        qvm = QuantumVirtualMachine()

        assert qvm.last_state is None


class TestSingleQubitExecution:
    """Tests for single-qubit gate execution."""

    def test_x_gate_flips_zero_to_one(self) -> None:
        """X|0> should produce |1>."""

        circuit = QuantumCircuit(1)
        circuit.x(0)

        qvm = QuantumVirtualMachine()

        state = qvm.simulate(circuit)

        assert math.isclose(
            abs(state.get_amplitude(0)),
            0.0,
            abs_tol=1e-10,
        )

        assert math.isclose(
            abs(state.get_amplitude(1)),
            1.0,
            abs_tol=1e-10,
        )

    def test_x_gate_probability(self) -> None:
        """X|0> should measure as |1> with probability 1."""

        circuit = QuantumCircuit(1)
        circuit.x(0)

        qvm = QuantumVirtualMachine()

        state = qvm.simulate(circuit)

        probabilities = state.probabilities()

        assert math.isclose(
            probabilities[0],
            0.0,
            abs_tol=1e-10,
        )

        assert math.isclose(
            probabilities[1],
            1.0,
            abs_tol=1e-10,
        )

    def test_hadamard_creates_superposition(self) -> None:
        """H|0> should produce equal probabilities."""

        circuit = QuantumCircuit(1)
        circuit.h(0)

        qvm = QuantumVirtualMachine()

        state = qvm.simulate(circuit)

        probabilities = state.probabilities()

        assert math.isclose(
            probabilities[0],
            0.5,
            rel_tol=1e-10,
        )

        assert math.isclose(
            probabilities[1],
            0.5,
            rel_tol=1e-10,
        )

    def test_hadamard_state_amplitudes(self) -> None:
        """H|0> should produce 1/sqrt(2) amplitudes."""

        circuit = QuantumCircuit(1)
        circuit.h(0)

        qvm = QuantumVirtualMachine()

        state = qvm.simulate(circuit)

        expected = 1 / math.sqrt(2)

        assert math.isclose(
            state.get_amplitude(0).real,
            expected,
            rel_tol=1e-10,
        )

        assert math.isclose(
            state.get_amplitude(1).real,
            expected,
            rel_tol=1e-10,
        )

    def test_hadamard_twice_returns_to_zero(self) -> None:
        """H followed by H should return |0>."""

        circuit = QuantumCircuit(1)

        circuit.h(0)
        circuit.h(0)

        qvm = QuantumVirtualMachine()

        state = qvm.simulate(circuit)

        assert math.isclose(
            abs(state.get_amplitude(0)),
            1.0,
            abs_tol=1e-10,
        )

        assert math.isclose(
            abs(state.get_amplitude(1)),
            0.0,
            abs_tol=1e-10,
        )

    def test_z_on_zero_does_not_change_state(self) -> None:
        """Z|0> should remain |0>."""

        circuit = QuantumCircuit(1)
        circuit.z(0)

        qvm = QuantumVirtualMachine()

        state = qvm.simulate(circuit)

        assert state.get_amplitude(0) == 1 + 0j
        assert state.get_amplitude(1) == 0 + 0j

    def test_z_on_one_changes_phase(self) -> None:
        """Z|1> should produce -|1>."""

        circuit = QuantumCircuit(1)

        circuit.x(0)
        circuit.z(0)

        qvm = QuantumVirtualMachine()

        state = qvm.simulate(circuit)

        assert math.isclose(
            state.get_amplitude(0).real,
            0.0,
            abs_tol=1e-10,
        )

        assert math.isclose(
            state.get_amplitude(1).real,
            -1.0,
            abs_tol=1e-10,
        )


class TestTwoQubitExecution:
    """Tests for two-qubit operations."""

    def test_cnot_with_control_zero_does_nothing(self) -> None:
        """
        If the control is |0>, CNOT should not flip the target.
        """

        circuit = QuantumCircuit(2)

        circuit.cx(0, 1)

        qvm = QuantumVirtualMachine()

        state = qvm.simulate(circuit)

        probabilities = state.probabilities()

        assert math.isclose(
            probabilities[0],
            1.0,
            abs_tol=1e-10,
        )

    def test_cnot_flips_target_when_control_is_one(self) -> None:
        """
        Prepare |10> and apply CNOT.

        With qubit 0 as control and qubit 1 as target,
        this implementation uses little-endian qubit indexing.
        """

        circuit = QuantumCircuit(2)

        circuit.x(0)
        circuit.cx(0, 1)

        qvm = QuantumVirtualMachine()

        state = qvm.simulate(circuit)

        probabilities = state.probabilities()

        assert math.isclose(
            probabilities[3],
            1.0,
            abs_tol=1e-10,
        )

    def test_bell_state(self) -> None:
        """
        Create a Bell state:

            H(0)
            CX(0, 1)

        Expected probabilities:

            |00> = 0.5
            |11> = 0.5
        """

        circuit = QuantumCircuit(2)

        circuit.h(0)
        circuit.cx(0, 1)

        qvm = QuantumVirtualMachine()

        state = qvm.simulate(circuit)

        probabilities = state.probabilities()

        assert math.isclose(
            probabilities[0],
            0.5,
            rel_tol=1e-10,
        )

        assert math.isclose(
            probabilities[1],
            0.0,
            abs_tol=1e-10,
        )

        assert math.isclose(
            probabilities[2],
            0.0,
            abs_tol=1e-10,
        )

        assert math.isclose(
            probabilities[3],
            0.5,
            rel_tol=1e-10,
        )


class TestMeasurement:
    """Tests for measurement sampling."""

    def test_x_state_always_measures_one(self) -> None:
        """X|0> should always produce measurement result 1."""

        circuit = QuantumCircuit(1)
        circuit.x(0)

        qvm = QuantumVirtualMachine()

        result = qvm.run(
            circuit,
            shots=100,
        )

        assert result == {
            "1": 100,
        }

    def test_zero_state_always_measures_zero(self) -> None:
        """The initial |0> state should always measure as 0."""

        circuit = QuantumCircuit(1)

        qvm = QuantumVirtualMachine()

        result = qvm.run(
            circuit,
            shots=100,
        )

        assert result == {
            "0": 100,
        }

    def test_bell_state_measurement(self) -> None:
        """
        Bell-state measurements should only produce 00 and 11.
        """

        circuit = QuantumCircuit(2)

        circuit.h(0)
        circuit.cx(0, 1)

        qvm = QuantumVirtualMachine()

        result = qvm.run(
            circuit,
            shots=1000,
        )

        assert set(result.keys()).issubset(
            {"00", "11"}
        )

        assert sum(result.values()) == 1000

    def test_measurement_count_matches_shots(self) -> None:
        """The total measurement count must equal shots."""

        circuit = QuantumCircuit(2)

        circuit.h(0)

        qvm = QuantumVirtualMachine()

        result = qvm.run(
            circuit,
            shots=500,
        )

        assert sum(result.values()) == 500


class TestStatevector:
    """Tests for statevector access."""

    def test_statevector_requires_execution(self) -> None:
        """Statevector access should fail before execution."""

        qvm = QuantumVirtualMachine()

        with pytest.raises(RuntimeError):
            qvm.statevector()

    def test_statevector_after_simulation(self) -> None:
        """The final statevector should be accessible."""

        circuit = QuantumCircuit(1)
        circuit.x(0)

        qvm = QuantumVirtualMachine()

        qvm.simulate(circuit)

        statevector = qvm.statevector()

        assert len(statevector) == 2
        assert statevector[0] == 0 + 0j
        assert statevector[1] == 1 + 0j


class TestQVMValidation:
    """Tests for invalid QVM inputs."""

    def test_non_circuit_is_rejected(self) -> None:
        """QVM should only accept QuantumCircuit objects."""

        qvm = QuantumVirtualMachine()

        with pytest.raises(TypeError):
            qvm.simulate("not a circuit")  # type: ignore[arg-type]

    def test_invalid_shot_count_is_rejected(self) -> None:
        """Shots must be at least 1."""

        circuit = QuantumCircuit(1)

        qvm = QuantumVirtualMachine()

        with pytest.raises(ValueError):
            qvm.run(circuit, shots=0)

    def test_negative_shot_count_is_rejected(self) -> None:
        """Negative shot counts must be rejected."""

        circuit = QuantumCircuit(1)

        qvm = QuantumVirtualMachine()

        with pytest.raises(ValueError):
            qvm.run(circuit, shots=-10)