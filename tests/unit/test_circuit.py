"""
QuantumOS - Quantum Circuit Tests

Unit tests for the QuantumCircuit class.
"""

import pytest

from qos.core import Operation, QuantumCircuit


class TestQuantumCircuitInitialization:
    """Tests for circuit initialization."""

    def test_create_single_qubit_circuit(self) -> None:
        """A single-qubit circuit should be created successfully."""

        circuit = QuantumCircuit(1)

        assert circuit.num_qubits == 1
        assert circuit.operations == []
        assert len(circuit) == 0

    def test_create_multi_qubit_circuit(self) -> None:
        """A multi-qubit circuit should store the correct size."""

        circuit = QuantumCircuit(5)

        assert circuit.num_qubits == 5
        assert len(circuit.operations) == 0

    def test_zero_qubit_circuit_is_rejected(self) -> None:
        """A circuit must contain at least one qubit."""

        with pytest.raises(ValueError):
            QuantumCircuit(0)

    def test_negative_qubit_circuit_is_rejected(self) -> None:
        """Negative qubit counts must be rejected."""

        with pytest.raises(ValueError):
            QuantumCircuit(-1)


class TestSingleQubitOperations:
    """Tests for single-qubit operations."""

    def test_hadamard_operation(self) -> None:
        """H should be recorded correctly."""

        circuit = QuantumCircuit(2)

        circuit.h(0)

        assert circuit.operations == [
            Operation(
                name="H",
                qubits=(0,),
            )
        ]

    def test_x_operation(self) -> None:
        """X should be recorded correctly."""

        circuit = QuantumCircuit(2)

        circuit.x(1)

        assert circuit.operations == [
            Operation(
                name="X",
                qubits=(1,),
            )
        ]

    def test_y_operation(self) -> None:
        """Y should be recorded correctly."""

        circuit = QuantumCircuit(2)

        circuit.y(0)

        assert circuit.operations == [
            Operation(
                name="Y",
                qubits=(0,),
            )
        ]

    def test_z_operation(self) -> None:
        """Z should be recorded correctly."""

        circuit = QuantumCircuit(2)

        circuit.z(1)

        assert circuit.operations == [
            Operation(
                name="Z",
                qubits=(1,),
            )
        ]

    def test_s_operation(self) -> None:
        """S should be recorded correctly."""

        circuit = QuantumCircuit(1)

        circuit.s(0)

        assert circuit.operations == [
            Operation(
                name="S",
                qubits=(0,),
            )
        ]

    def test_t_operation(self) -> None:
        """T should be recorded correctly."""

        circuit = QuantumCircuit(1)

        circuit.t(0)

        assert circuit.operations == [
            Operation(
                name="T",
                qubits=(0,),
            )
        ]


class TestControlledOperations:
    """Tests for multi-qubit operations."""

    def test_cnot_operation(self) -> None:
        """CNOT should store control and target qubits."""

        circuit = QuantumCircuit(2)

        circuit.cx(0, 1)

        assert circuit.operations == [
            Operation(
                name="CX",
                qubits=(0, 1),
            )
        ]

    def test_cnot_preserves_argument_order(self) -> None:
        """Control and target order must be preserved."""

        circuit = QuantumCircuit(3)

        circuit.cx(2, 0)

        assert circuit.operations[0].qubits == (2, 0)

    def test_cnot_same_qubit_is_rejected(self) -> None:
        """A qubit cannot be both control and target."""

        circuit = QuantumCircuit(2)

        with pytest.raises(ValueError):
            circuit.cx(0, 0)


class TestQubitValidation:
    """Tests for qubit index validation."""

    def test_negative_qubit_index_is_rejected(self) -> None:
        """Negative indexes should not be accepted."""

        circuit = QuantumCircuit(2)

        with pytest.raises(IndexError):
            circuit.h(-1)

    def test_out_of_range_qubit_index_is_rejected(self) -> None:
        """Indexes outside the circuit should be rejected."""

        circuit = QuantumCircuit(2)

        with pytest.raises(IndexError):
            circuit.x(2)

    def test_invalid_cnot_control_is_rejected(self) -> None:
        """Invalid control qubits should be rejected."""

        circuit = QuantumCircuit(2)

        with pytest.raises(IndexError):
            circuit.cx(2, 1)

    def test_invalid_cnot_target_is_rejected(self) -> None:
        """Invalid target qubits should be rejected."""

        circuit = QuantumCircuit(2)

        with pytest.raises(IndexError):
            circuit.cx(0, 2)

    def test_non_integer_qubit_index_is_rejected(self) -> None:
        """Qubit indexes must be integers."""

        circuit = QuantumCircuit(2)

        with pytest.raises(TypeError):
            circuit.h(0.5)  # type: ignore[arg-type]


class TestCircuitOperations:
    """Tests for circuit operation management."""

    def test_operations_preserve_order(self) -> None:
        """Operations must execute in the order they were added."""

        circuit = QuantumCircuit(2)

        circuit.h(0)
        circuit.x(1)
        circuit.z(0)
        circuit.cx(0, 1)

        assert circuit.operations == [
            Operation("H", (0,)),
            Operation("X", (1,)),
            Operation("Z", (0,)),
            Operation("CX", (0, 1)),
        ]

    def test_gate_count(self) -> None:
        """gate_count should return the number of operations."""

        circuit = QuantumCircuit(2)

        circuit.h(0)
        circuit.x(1)
        circuit.cx(0, 1)

        assert circuit.gate_count() == 3

    def test_len_matches_gate_count(self) -> None:
        """len(circuit) should match gate_count()."""

        circuit = QuantumCircuit(2)

        circuit.h(0)
        circuit.x(1)

        assert len(circuit) == circuit.gate_count()

    def test_depth_for_initial_implementation(self) -> None:
        """
        The initial depth implementation is operation-count based.
        """

        circuit = QuantumCircuit(2)

        circuit.h(0)
        circuit.cx(0, 1)
        circuit.x(1)

        assert circuit.depth() == 3

    def test_clear_removes_all_operations(self) -> None:
        """clear() should remove every operation."""

        circuit = QuantumCircuit(2)

        circuit.h(0)
        circuit.cx(0, 1)

        circuit.clear()

        assert circuit.operations == []
        assert len(circuit) == 0


class TestCircuitGateMatrices:
    """Tests for circuit access to gate matrices."""

    def test_get_hadamard_matrix(self) -> None:
        """The circuit should expose the H matrix."""

        circuit = QuantumCircuit(1)

        matrix = circuit.single_qubit_gate_matrix("H")

        assert len(matrix) == 2
        assert len(matrix[0]) == 2

    def test_invalid_gate_matrix_is_rejected(self) -> None:
        """Unsupported gates should raise ValueError."""

        circuit = QuantumCircuit(1)

        with pytest.raises(ValueError):
            circuit.single_qubit_gate_matrix("INVALID")


class TestCircuitRepresentation:
    """Tests for debugging representation."""

    def test_repr_contains_circuit_information(self) -> None:
        """repr() should contain useful circuit information."""

        circuit = QuantumCircuit(2)

        circuit.h(0)

        representation = repr(circuit)

        assert "QuantumCircuit" in representation
        assert "num_qubits=2" in representation
        assert "H" in representation