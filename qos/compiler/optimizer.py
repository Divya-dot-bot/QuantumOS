"""
QuantumOS Compiler - Optimizer

Provides conservative optimization passes for quantum circuits.
"""

from __future__ import annotations

from dataclasses import dataclass

from qos.core.circuit import QuantumCircuit


@dataclass(frozen=True)
class OptimizationStats:
    """Statistics describing an optimization pass."""

    original_gate_count: int
    optimized_gate_count: int

    @property
    def gates_removed(self) -> int:
        """Return the number of gates removed."""

        return (
            self.original_gate_count
            - self.optimized_gate_count
        )

    @property
    def reduction_ratio(self) -> float:
        """Return the fraction of gates removed."""

        if self.original_gate_count == 0:
            return 0.0

        return self.gates_removed / self.original_gate_count


class CircuitOptimizer:
    """
    Conservative quantum-circuit optimizer.

    Supported optimizations:

    * Removing identity gates.
    * Cancelling adjacent self-inverse gates.
    * Combining adjacent S gates into Z.
    * Repeating optimization passes until stable.
    """

    SELF_INVERSE_GATES = {
        "i",
        "x",
        "y",
        "z",
        "h",
        "cx",
    }

    def optimize(
        self,
        circuit: QuantumCircuit,
    ) -> QuantumCircuit:
        """Return an optimized copy of a circuit."""

        self._validate_circuit(circuit)

        optimized = self._remove_identity_gates(circuit)

        changed = True

        while changed:
            optimized, changed = self._cancel_adjacent_gates(
                optimized
            )

            optimized, s_changed = self._combine_phase_gates(
                optimized
            )

            changed = changed or s_changed

        return optimized

    def optimize_with_stats(
        self,
        circuit: QuantumCircuit,
    ) -> tuple[QuantumCircuit, OptimizationStats]:
        """Optimize a circuit and return optimization statistics."""

        self._validate_circuit(circuit)

        original_count = circuit.gate_count()

        optimized = self.optimize(circuit)

        stats = OptimizationStats(
            original_gate_count=original_count,
            optimized_gate_count=optimized.gate_count(),
        )

        return optimized, stats

    def _add_operation(
        self,
        circuit: QuantumCircuit,
        name: str,
        qubits: tuple[int, ...],
    ) -> None:
        """Add an operation using the public QuantumCircuit API."""

        operation = name.lower()

        if operation == "i":
            # Identity has no effect, so it is never added.
            return

        if operation == "h":
            circuit.h(qubits[0])
            return

        if operation == "x":
            circuit.x(qubits[0])
            return

        if operation == "y":
            circuit.y(qubits[0])
            return

        if operation == "z":
            circuit.z(qubits[0])
            return

        if operation == "s":
            circuit.s(qubits[0])
            return

        if operation == "t":
            circuit.t(qubits[0])
            return

        if operation == "cx":
            circuit.cx(
                qubits[0],
                qubits[1],
            )
            return

        raise ValueError(
            f"unsupported operation '{name}'"
        )

    def _remove_identity_gates(
        self,
        circuit: QuantumCircuit,
    ) -> QuantumCircuit:
        """Remove explicit identity gates."""

        result = QuantumCircuit(
            circuit.num_qubits
        )

        for operation in circuit.operations:
            self._add_operation(
                result,
                operation.name,
                operation.qubits,
            )

        return result

    def _cancel_adjacent_gates(
        self,
        circuit: QuantumCircuit,
    ) -> tuple[QuantumCircuit, bool]:
        """Cancel adjacent identical self-inverse gates."""

        result = QuantumCircuit(
            circuit.num_qubits
        )

        changed = False
        index = 0

        while index < len(circuit.operations):
            current = circuit.operations[index]

            if (
                index + 1 < len(circuit.operations)
                and current.name.lower()
                == circuit.operations[index + 1].name.lower()
                and current.qubits
                == circuit.operations[index + 1].qubits
                and current.name.lower()
                in self.SELF_INVERSE_GATES
            ):
                index += 2
                changed = True
                continue

            self._add_operation(
                result,
                current.name,
                current.qubits,
            )

            index += 1

        return result, changed

    def _combine_phase_gates(
        self,
        circuit: QuantumCircuit,
    ) -> tuple[QuantumCircuit, bool]:
        """Combine adjacent S gates acting on the same qubit."""

        result = QuantumCircuit(
            circuit.num_qubits
        )

        changed = False
        index = 0

        while index < len(circuit.operations):
            current = circuit.operations[index]

            if (
                index + 1 < len(circuit.operations)
                and current.name.lower() == "s"
                and circuit.operations[index + 1].name.lower() == "s"
                and current.qubits
                == circuit.operations[index + 1].qubits
            ):
                result.z(current.qubits[0])

                index += 2
                changed = True
                continue

            self._add_operation(
                result,
                current.name,
                current.qubits,
            )

            index += 1

        return result, changed

    @staticmethod
    def _validate_circuit(
        circuit: QuantumCircuit,
    ) -> None:
        """Validate an optimizer input."""

        if not isinstance(circuit, QuantumCircuit):
            raise TypeError(
                "circuit must be a QuantumCircuit"
            )


def optimize(
    circuit: QuantumCircuit,
) -> QuantumCircuit:
    """
    Convenience function used by the compiler.
    """

    optimizer = CircuitOptimizer()

    return optimizer.optimize(circuit)


def optimize_circuit(
    circuit: QuantumCircuit,
) -> QuantumCircuit:
    """Backward-compatible convenience function."""

    return optimize(circuit)