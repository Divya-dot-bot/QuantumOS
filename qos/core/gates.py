"""
QuantumOS - Quantum Gates

Defines the fundamental quantum gates used by the Quantum Virtual Machine.

Single-qubit gates are represented as 2x2 complex matrices.

Two-qubit gates are represented separately because they operate on
multiple qubits.
"""

from __future__ import annotations

import math
from typing import List


# Type alias for a matrix of complex numbers.
Matrix = List[List[complex]]


def _validate_2x2_matrix(matrix: Matrix) -> None:
    """Validate that a matrix is 2x2."""

    if len(matrix) != 2 or any(len(row) != 2 for row in matrix):
        raise ValueError("A single-qubit gate must be a 2x2 matrix.")


def identity() -> Matrix:
    """
    Identity gate.

    The identity gate does nothing to the quantum state.

        I = [1  0]
            [0  1]
    """

    return [
        [1 + 0j, 0 + 0j],
        [0 + 0j, 1 + 0j],
    ]


def pauli_x() -> Matrix:
    """
    Pauli-X gate.

    Acts like a quantum NOT gate:

        |0⟩ -> |1⟩
        |1⟩ -> |0⟩

        X = [0  1]
            [1  0]
    """

    return [
        [0 + 0j, 1 + 0j],
        [1 + 0j, 0 + 0j],
    ]


def pauli_y() -> Matrix:
    """
    Pauli-Y gate.

        Y = [0  -i]
            [i   0]
    """

    return [
        [0 + 0j, -1j],
        [1j, 0 + 0j],
    ]


def pauli_z() -> Matrix:
    """
    Pauli-Z gate.

        Z = [1   0]
            [0  -1]
    """

    return [
        [1 + 0j, 0 + 0j],
        [0 + 0j, -1 + 0j],
    ]


def hadamard() -> Matrix:
    """
    Hadamard gate.

    Creates an equal superposition from |0⟩:

        |0⟩ -> (|0⟩ + |1⟩) / √2

        H = 1/√2 [1   1]
                  [1  -1]
    """

    factor = 1 / math.sqrt(2)

    return [
        [factor + 0j, factor + 0j],
        [factor + 0j, -factor + 0j],
    ]


def phase_s() -> Matrix:
    """
    S phase gate.

        S = [1  0]
            [0  i]
    """

    return [
        [1 + 0j, 0 + 0j],
        [0 + 0j, 1j],
    ]


def phase_t() -> Matrix:
    """
    T phase gate.

        T = [1          0]
            [0      e^(iπ/4)]
    """

    phase = complex(
        math.cos(math.pi / 4),
        math.sin(math.pi / 4),
    )

    return [
        [1 + 0j, 0 + 0j],
        [0 + 0j, phase],
    ]


def cnot() -> Matrix:
    """
    Controlled-NOT gate.

    The first qubit is the control.
    The second qubit is the target.

    Basis ordering:

        |00⟩
        |01⟩
        |10⟩
        |11⟩

    Transformation:

        |00⟩ -> |00⟩
        |01⟩ -> |01⟩
        |10⟩ -> |11⟩
        |11⟩ -> |10⟩
    """

    return [
        [1 + 0j, 0 + 0j, 0 + 0j, 0 + 0j],
        [0 + 0j, 1 + 0j, 0 + 0j, 0 + 0j],
        [0 + 0j, 0 + 0j, 0 + 0j, 1 + 0j],
        [0 + 0j, 0 + 0j, 1 + 0j, 0 + 0j],
    ]


def get_single_qubit_gate(name: str) -> Matrix:
    """
    Return a single-qubit gate by name.

    Supported gates:

        I, X, Y, Z, H, S, T

    Args:
        name: Gate name.

    Returns:
        2x2 complex matrix.

    Raises:
        ValueError: If the gate is not supported.
    """

    gates = {
        "I": identity,
        "X": pauli_x,
        "Y": pauli_y,
        "Z": pauli_z,
        "H": hadamard,
        "S": phase_s,
        "T": phase_t,
    }

    normalized_name = name.upper()

    if normalized_name not in gates:
        raise ValueError(
            f"Unsupported single-qubit gate: {name}"
        )

    gate = gates[normalized_name]()

    _validate_2x2_matrix(gate)

    return gate