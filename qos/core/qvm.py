"""
QuantumOS - Quantum Virtual Machine

The Quantum Virtual Machine (QVM) executes quantum circuits using
a state-vector simulation.

This is the execution engine of the first QuantumOS MVP.
"""

from __future__ import annotations

import random
from collections import Counter
from typing import Dict, List

from .circuit import Operation, QuantumCircuit
from .gates import Matrix, get_single_qubit_gate
from .quantum_state import QuantumState


class QuantumVirtualMachine:
    """
    State-vector based quantum virtual machine.

    The QVM takes a QuantumCircuit and applies each operation to
    a QuantumState.

    Example:

        qvm = QuantumVirtualMachine()

        circuit = QuantumCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)

        result = qvm.run(circuit, shots=1000)
    """

    def __init__(self) -> None:
        """Create a new Quantum Virtual Machine."""

        self.last_state: QuantumState | None = None

    def run(
        self,
        circuit: QuantumCircuit,
        shots: int = 1024,
    ) -> Dict[str, int]:
        """
        Execute a quantum circuit and perform measurements.

        Args:
            circuit: Quantum circuit to execute.
            shots: Number of measurement repetitions.

        Returns:
            Dictionary mapping measured bitstrings to counts.

        Example:

            {
                "00": 512,
                "11": 512
            }
        """

        if not isinstance(circuit, QuantumCircuit):
            raise TypeError(
                "run() expects a QuantumCircuit."
            )

        if shots < 1:
            raise ValueError(
                "Number of shots must be at least 1."
            )

        state = QuantumState(circuit.num_qubits)

        for operation in circuit.operations:
            self._execute_operation(state, operation)

        self.last_state = state

        return self._measure(state, shots)

    def simulate(
        self,
        circuit: QuantumCircuit,
    ) -> QuantumState:
        """
        Execute a circuit and return the final quantum state.

        Unlike run(), this does not perform measurement sampling.

        Args:
            circuit: Quantum circuit to execute.

        Returns:
            Final QuantumState.
        """

        if not isinstance(circuit, QuantumCircuit):
            raise TypeError(
                "simulate() expects a QuantumCircuit."
            )

        state = QuantumState(circuit.num_qubits)

        for operation in circuit.operations:
            self._execute_operation(state, operation)

        self.last_state = state

        return state

    def _execute_operation(
        self,
        state: QuantumState,
        operation: Operation,
    ) -> None:
        """Execute a single circuit operation."""

        if operation.name == "CX":
            self._apply_cnot(
                state,
                operation.qubits[0],
                operation.qubits[1],
            )
            return

        gate = get_single_qubit_gate(operation.name)

        self._apply_single_qubit_gate(
            state,
            gate,
            operation.qubits[0],
        )

    def _apply_single_qubit_gate(
        self,
        state: QuantumState,
        gate: Matrix,
        qubit: int,
    ) -> None:
        """
        Apply a 2x2 single-qubit gate to one qubit.

        The operation is performed directly on the state vector
        without constructing the full 2^n x 2^n matrix.
        """

        if not 0 <= qubit < state.num_qubits:
            raise IndexError(
                f"Qubit index must be between "
                f"0 and {state.num_qubits - 1}."
            )

        mask = 1 << qubit

        amplitudes = state.amplitudes

        for index in range(state.dimension):
            # Only process the |0> side of each pair.
            if index & mask:
                continue

            paired_index = index | mask

            amplitude_zero = amplitudes[index]
            amplitude_one = amplitudes[paired_index]

            amplitudes[index] = (
                gate[0][0] * amplitude_zero
                + gate[0][1] * amplitude_one
            )

            amplitudes[paired_index] = (
                gate[1][0] * amplitude_zero
                + gate[1][1] * amplitude_one
            )

    def _apply_cnot(
        self,
        state: QuantumState,
        control: int,
        target: int,
    ) -> None:
        """
        Apply a controlled-NOT gate.

        If the control qubit is |1>, the target qubit is flipped.
        """

        if not 0 <= control < state.num_qubits:
            raise IndexError("Invalid control qubit.")

        if not 0 <= target < state.num_qubits:
            raise IndexError("Invalid target qubit.")

        if control == target:
            raise ValueError(
                "Control and target qubits must be different."
            )

        control_mask = 1 << control
        target_mask = 1 << target

        amplitudes = state.amplitudes

        for index in range(state.dimension):

            # Only states where the control is |1>
            # need to be considered.
            if not (index & control_mask):
                continue

            paired_index = index ^ target_mask

            # Swap each pair exactly once.
            if index < paired_index:
                amplitudes[index], amplitudes[paired_index] = (
                    amplitudes[paired_index],
                    amplitudes[index],
                )

    def _measure(
        self,
        state: QuantumState,
        shots: int,
    ) -> Dict[str, int]:
        """
        Sample the quantum state repeatedly.

        Measurement probabilities are determined by the squared
        magnitudes of the state-vector amplitudes.
        """

        probabilities = state.probabilities()

        outcomes = list(range(state.dimension))

        samples = random.choices(
            outcomes,
            weights=probabilities,
            k=shots,
        )

        counts = Counter(
            self._index_to_bitstring(
                index,
                state.num_qubits,
            )
            for index in samples
        )

        return dict(
            sorted(counts.items())
        )

    @staticmethod
    def _index_to_bitstring(
        index: int,
        num_qubits: int,
    ) -> str:
        """
        Convert a basis-state index to a binary string.

        Example:

            index = 2
            num_qubits = 2

            result = "10"
        """

        return format(
            index,
            f"0{num_qubits}b",
        )

    def statevector(self) -> List[complex]:
        """
        Return the amplitudes of the most recently simulated state.

        Raises:
            RuntimeError: If no circuit has been executed yet.
        """

        if self.last_state is None:
            raise RuntimeError(
                "No quantum circuit has been executed yet."
            )

        return list(self.last_state.amplitudes)