"""
QuantumOS Compiler - Transpiler

Converts QuantumCircuit objects into backend-compatible executable
representations.

The MVP supports the built-in state-vector QVM backend.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from qos.core.circuit import QuantumCircuit
from qos.compiler.optimizer import CircuitOptimizer


@dataclass(frozen=True)
class ExecutableInstruction:
    """
    A backend-ready quantum instruction.

    Attributes:
        operation: Normalized operation name.
        qubits: Qubit indices operated on by the instruction.
    """

    operation: str
    qubits: tuple[int, ...]

    def __post_init__(self) -> None:
        """Normalize and validate instruction fields."""

        operation = self.operation.strip().lower()

        if not operation:
            raise ValueError(
                "instruction operation cannot be empty"
            )

        object.__setattr__(
            self,
            "operation",
            operation,
        )

        object.__setattr__(
            self,
            "qubits",
            tuple(self.qubits),
        )


@dataclass(frozen=True)
class ExecutableCircuit:
    """
    Backend-ready representation of a quantum circuit.
    """

    num_qubits: int
    instructions: tuple[ExecutableInstruction, ...]

    @property
    def depth(self) -> int:
        """
        Return the sequential instruction depth.

        The MVP uses sequential depth because instructions are currently
        executed in circuit order.
        """

        return len(self.instructions)

    @property
    def gate_count(self) -> int:
        """Return the number of executable instructions."""

        return len(self.instructions)

    def operations(self) -> list[str]:
        """Return operation names in execution order."""

        return [
            instruction.operation
            for instruction in self.instructions
        ]

    def __iter__(self):
        """Iterate over executable instructions."""

        return iter(self.instructions)


class Transpiler:
    """
    QuantumOS circuit transpiler.

    The MVP transpiler:

    1. Validates the input circuit.
    2. Optionally optimizes it.
    3. Normalizes gate names.
    4. Produces an ExecutableCircuit.
    """

    SUPPORTED_OPERATIONS = {
        "i",
        "x",
        "y",
        "z",
        "h",
        "s",
        "t",
        "cx",
    }

    def __init__(
        self,
        *,
        optimize: bool = True,
    ) -> None:
        """
        Initialize the transpiler.

        Args:
            optimize:
                Whether to run the circuit optimizer before
                generating executable instructions.
        """

        self.optimize = optimize

    def transpile(
        self,
        circuit: QuantumCircuit,
    ) -> ExecutableCircuit:
        """
        Transpile a QuantumCircuit.

        Args:
            circuit: Input quantum circuit.

        Returns:
            Backend-ready executable circuit.
        """

        self._validate_circuit(circuit)

        working_circuit = circuit

        if self.optimize:
            optimizer = CircuitOptimizer()

            working_circuit = optimizer.optimize(
                circuit
            )

            instructions = tuple(
            self._convert_gate(gate)
            for gate in working_circuit.operations
        )


        return ExecutableCircuit(
            num_qubits=working_circuit.num_qubits,
            instructions=instructions,
        )

    def transpile_many(
        self,
        circuits: Iterable[QuantumCircuit],
    ) -> list[ExecutableCircuit]:
        """Transpile multiple circuits."""

        return [
            self.transpile(circuit)
            for circuit in circuits
        ]

    def _convert_gate(self, gate) -> ExecutableInstruction:
        """Convert a circuit gate into an executable instruction."""

        operation = gate.name.strip().lower()

        if operation not in self.SUPPORTED_OPERATIONS:
            raise ValueError(
                f"unsupported operation for QVM backend: "
                f"{gate.name}"
            )

        qubits = tuple(gate.qubits)

        return ExecutableInstruction(
            operation=operation,
            qubits=qubits,
        )

    @staticmethod
    def _validate_circuit(
        circuit: QuantumCircuit,
    ) -> None:
        """Validate a transpiler input."""

        if not isinstance(circuit, QuantumCircuit):
            raise TypeError(
                "circuit must be a QuantumCircuit"
            )


def transpile(
    circuit: QuantumCircuit,
    *,
    optimize: bool = True,
) -> ExecutableCircuit:
    """
    Convenience function for transpiling a quantum circuit.
    """

    compiler = Transpiler(
        optimize=optimize
    )

    return compiler.transpile(circuit)