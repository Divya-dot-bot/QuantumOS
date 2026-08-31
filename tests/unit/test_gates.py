"""
QuantumOS - Quantum Gate Tests

Unit tests for the fundamental quantum gates.
"""

import math

import pytest

from qos.core.gates import (
    cnot,
    get_single_qubit_gate,
    hadamard,
    identity,
    pauli_x,
    pauli_y,
    pauli_z,
    phase_s,
    phase_t,
)


class TestGateDimensions:
    """Tests for gate matrix dimensions."""

    @pytest.mark.parametrize(
        "gate_function",
        [
            identity,
            pauli_x,
            pauli_y,
            pauli_z,
            hadamard,
            phase_s,
            phase_t,
        ],
    )
    def test_single_qubit_gates_are_2x2(
        self,
        gate_function,
    ) -> None:
        """Every single-qubit gate should be a 2x2 matrix."""

        gate = gate_function()

        assert len(gate) == 2
        assert all(len(row) == 2 for row in gate)

    def test_cnot_is_4x4(self) -> None:
        """CNOT should be a 4x4 matrix."""

        gate = cnot()

        assert len(gate) == 4
        assert all(len(row) == 4 for row in gate)


class TestIdentityGate:
    """Tests for the identity gate."""

    def test_identity_matrix(self) -> None:
        """Verify the identity matrix."""

        assert identity() == [
            [1 + 0j, 0 + 0j],
            [0 + 0j, 1 + 0j],
        ]


class TestPauliGates:
    """Tests for X, Y and Z gates."""

    def test_pauli_x(self) -> None:
        """Verify the Pauli-X matrix."""

        assert pauli_x() == [
            [0 + 0j, 1 + 0j],
            [1 + 0j, 0 + 0j],
        ]

    def test_pauli_y(self) -> None:
        """Verify the Pauli-Y matrix."""

        assert pauli_y() == [
            [0 + 0j, -1j],
            [1j, 0 + 0j],
        ]

    def test_pauli_z(self) -> None:
        """Verify the Pauli-Z matrix."""

        assert pauli_z() == [
            [1 + 0j, 0 + 0j],
            [0 + 0j, -1 + 0j],
        ]


class TestHadamardGate:
    """Tests for the Hadamard gate."""

    def test_hadamard_values(self) -> None:
        """Verify the Hadamard matrix."""

        factor = 1 / math.sqrt(2)

        expected = [
            [factor + 0j, factor + 0j],
            [factor + 0j, -factor + 0j],
        ]

        actual = hadamard()

        for row_actual, row_expected in zip(actual, expected):
            for value_actual, value_expected in zip(
                row_actual,
                row_expected,
            ):
                assert math.isclose(
                    value_actual.real,
                    value_expected.real,
                    rel_tol=1e-10,
                )

                assert math.isclose(
                    value_actual.imag,
                    value_expected.imag,
                    rel_tol=1e-10,
                )


class TestPhaseGates:
    """Tests for S and T phase gates."""

    def test_s_gate(self) -> None:
        """Verify the S gate."""

        assert phase_s() == [
            [1 + 0j, 0 + 0j],
            [0 + 0j, 1j],
        ]

    def test_t_gate(self) -> None:
        """Verify the T gate."""

        gate = phase_t()

        expected_phase = complex(
            math.cos(math.pi / 4),
            math.sin(math.pi / 4),
        )

        assert gate[0][0] == 1 + 0j
        assert gate[0][1] == 0 + 0j
        assert gate[1][0] == 0 + 0j

        assert math.isclose(
            gate[1][1].real,
            expected_phase.real,
            rel_tol=1e-10,
        )

        assert math.isclose(
            gate[1][1].imag,
            expected_phase.imag,
            rel_tol=1e-10,
        )


class TestCNOTGate:
    """Tests for the controlled-NOT gate."""

    def test_cnot_matrix(self) -> None:
        """Verify the CNOT matrix."""

        assert cnot() == [
            [1 + 0j, 0 + 0j, 0 + 0j, 0 + 0j],
            [0 + 0j, 1 + 0j, 0 + 0j, 0 + 0j],
            [0 + 0j, 0 + 0j, 0 + 0j, 1 + 0j],
            [0 + 0j, 0 + 0j, 1 + 0j, 0 + 0j],
        ]


class TestGateLookup:
    """Tests for gate lookup."""

    @pytest.mark.parametrize(
        "name",
        [
            "I",
            "X",
            "Y",
            "Z",
            "H",
            "S",
            "T",
        ],
    )
    def test_supported_gate_lookup(self, name: str) -> None:
        """Every supported gate should be retrievable by name."""

        gate = get_single_qubit_gate(name)

        assert len(gate) == 2
        assert all(len(row) == 2 for row in gate)

    def test_gate_lookup_is_case_insensitive(self) -> None:
        """Gate names should work regardless of capitalization."""

        assert get_single_qubit_gate("h") == get_single_qubit_gate("H")
        assert get_single_qubit_gate("x") == get_single_qubit_gate("X")

    def test_unsupported_gate_is_rejected(self) -> None:
        """Unknown gates should raise ValueError."""

        with pytest.raises(ValueError):
            get_single_qubit_gate("INVALID")