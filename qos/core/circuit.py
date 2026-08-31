"""
QuantumOS - Quantum Circuit

Core representation of a quantum circuit.

A QuantumCircuit stores quantum operations in execution order.
Execution is handled by the Quantum Virtual Machine or another
QuantumOS backend.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .gates import Matrix, get_single_qubit_gate


@dataclass(frozen=True)
class Operation:
    """
    Represents one operation in a quantum circuit.

    Attributes:
        name:
            Gate/operation name, for example H, X, CX.

        qubits:
            Qubit indices affected by the operation.
    """

    name: str
    qubits: Tuple[int, ...]


class QuantumCircuit:
    """
    Represents a quantum circuit.

    The circuit stores operations but does not execute them.

    Example:

        circuit = QuantumCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)
    """

    SINGLE_QUBIT_GATES = {
        "I",
        "X",
        "Y",
        "Z",
        "H",
        "S",
        "T",
    }

    TWO_QUBIT_GATES = {
        "CX",
    }

    def __init__(self, num_qubits: int) -> None:
        """
        Create an empty quantum circuit.

        Args:
            num_qubits:
                Number of qubits in the circuit.
        """

        if (
            not isinstance(num_qubits, int)
            or isinstance(num_qubits, bool)
        ):
            raise TypeError(
                "Number of qubits must be an integer."
            )

        if num_qubits < 1:
            raise ValueError(
                "A quantum circuit must contain at least one qubit."
            )

        self.num_qubits = num_qubits
        self.operations: list[Operation] = []

    # ------------------------------------------------------------------
    # Single-qubit gates
    # ------------------------------------------------------------------

    def i(self, qubit: int) -> "QuantumCircuit":
        """Apply an Identity gate."""

        self._validate_qubit(qubit)

        self.operations.append(
            Operation(
                name="I",
                qubits=(qubit,),
            )
        )

        return self

    def h(self, qubit: int) -> "QuantumCircuit":
        """Apply a Hadamard gate."""

        self._validate_qubit(qubit)

        self.operations.append(
            Operation(
                name="H",
                qubits=(qubit,),
            )
        )

        return self

    def x(self, qubit: int) -> "QuantumCircuit":
        """Apply a Pauli-X gate."""

        self._validate_qubit(qubit)

        self.operations.append(
            Operation(
                name="X",
                qubits=(qubit,),
            )
        )

        return self

    def y(self, qubit: int) -> "QuantumCircuit":
        """Apply a Pauli-Y gate."""

        self._validate_qubit(qubit)

        self.operations.append(
            Operation(
                name="Y",
                qubits=(qubit,),
            )
        )

        return self

    def z(self, qubit: int) -> "QuantumCircuit":
        """Apply a Pauli-Z gate."""

        self._validate_qubit(qubit)

        self.operations.append(
            Operation(
                name="Z",
                qubits=(qubit,),
            )
        )

        return self

    def s(self, qubit: int) -> "QuantumCircuit":
        """Apply an S phase gate."""

        self._validate_qubit(qubit)

        self.operations.append(
            Operation(
                name="S",
                qubits=(qubit,),
            )
        )

        return self

    def t(self, qubit: int) -> "QuantumCircuit":
        """Apply a T phase gate."""

        self._validate_qubit(qubit)

        self.operations.append(
            Operation(
                name="T",
                qubits=(qubit,),
            )
        )

        return self

    # ------------------------------------------------------------------
    # Two-qubit gates
    # ------------------------------------------------------------------

    def cx(
        self,
        control: int,
        target: int,
    ) -> "QuantumCircuit":
        """
        Apply a controlled-NOT gate.

        Args:
            control:
                Control qubit.

            target:
                Target qubit.
        """

        self._validate_qubit(control)
        self._validate_qubit(target)

        if control == target:
            raise ValueError(
                "Control and target qubits must be different."
            )

        self.operations.append(
            Operation(
                name="CX",
                qubits=(control, target),
            )
        )

        return self

    # ------------------------------------------------------------------
    # Circuit utilities
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """Remove all operations from the circuit."""

        self.operations.clear()

    def depth(self) -> int:
        """
        Return the circuit depth.

        The MVP uses operation count as a simple approximation.
        """

        return len(self.operations)

    def gate_count(self) -> int:
        """Return the total number of operations."""

        return len(self.operations)

    def single_qubit_gate_matrix(
        self,
        name: str,
    ) -> Matrix:
        """
        Return the matrix associated with a single-qubit gate.
        """

        normalized = name.upper()

        if normalized not in self.SINGLE_QUBIT_GATES:
            raise ValueError(
                f"'{name}' is not a supported single-qubit gate."
            )

        return get_single_qubit_gate(normalized)

    def _validate_qubit(
        self,
        qubit: int,
    ) -> None:
        """Validate a qubit index."""

        if (
            not isinstance(qubit, int)
            or isinstance(qubit, bool)
        ):
            raise TypeError(
                "Qubit index must be an integer."
            )

        if not 0 <= qubit < self.num_qubits:
            raise IndexError(
                f"Qubit index must be between "
                f"0 and {self.num_qubits - 1}."
            )

    def __len__(self) -> int:
        """Return the number of operations."""

        return len(self.operations)

    def __repr__(self) -> str:
        """Return a useful representation for debugging."""

        return (
            "QuantumCircuit("
            f"num_qubits={self.num_qubits}, "
            f"operations={self.operations}"
            ")"
        )