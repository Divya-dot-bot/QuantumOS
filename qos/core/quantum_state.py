"""
QuantumOS - Quantum State

Provides the fundamental representation of a quantum state.

A quantum state for n qubits is represented as a state vector
containing 2^n complex amplitudes.
"""

from __future__ import annotations

import math
from typing import List


class QuantumState:
    """
    Represents the state vector of an n-qubit quantum system.

    The state vector contains 2^n complex amplitudes.

    Example for one qubit:

        |ψ⟩ = α|0⟩ + β|1⟩

    represented internally as:

        [α, β]
    """

    def __init__(self, num_qubits: int) -> None:
        """
        Create a quantum state initialized to |00...0⟩.

        Args:
            num_qubits: Number of qubits in the system.

        Raises:
            ValueError: If num_qubits is less than 1.
        """
        if num_qubits < 1:
            raise ValueError("Number of qubits must be at least 1.")

        self.num_qubits = num_qubits
        self.dimension = 2**num_qubits

        # |00...0⟩
        #
        # The first basis state has amplitude 1.
        # Every other basis state has amplitude 0.
        self.amplitudes: List[complex] = [0j] * self.dimension
        self.amplitudes[0] = 1 + 0j

    def normalize(self) -> None:
        """
        Normalize the quantum state.

        A valid quantum state must satisfy:

            Σ |amplitude|² = 1
        """

        magnitude_squared = sum(
            abs(amplitude) ** 2
            for amplitude in self.amplitudes
        )

        if magnitude_squared == 0:
            raise ValueError(
                "Cannot normalize a quantum state with zero magnitude."
            )

        magnitude = math.sqrt(magnitude_squared)

        self.amplitudes = [
            amplitude / magnitude
            for amplitude in self.amplitudes
        ]

    def probabilities(self) -> List[float]:
        """
        Return the probability of measuring each computational basis state.

        For n qubits there are 2^n possible basis states.

        Returns:
            A list containing one probability for each basis state.
        """

        return [
            abs(amplitude) ** 2
            for amplitude in self.amplitudes
        ]

    def probability(self, state_index: int) -> float:
        """
        Return the probability of measuring a specific basis state.

        Args:
            state_index: Integer index of the basis state.

        Returns:
            Measurement probability.
        """

        self._validate_state_index(state_index)

        return abs(self.amplitudes[state_index]) ** 2

    def set_amplitude(
        self,
        state_index: int,
        amplitude: complex,
    ) -> None:
        """
        Set the amplitude of a specific basis state.

        Args:
            state_index: Integer index of the basis state.
            amplitude: Complex amplitude.
        """

        self._validate_state_index(state_index)

        self.amplitudes[state_index] = complex(amplitude)

    def get_amplitude(self, state_index: int) -> complex:
        """
        Get the amplitude of a specific basis state.

        Args:
            state_index: Integer index of the basis state.

        Returns:
            Complex amplitude.
        """

        self._validate_state_index(state_index)

        return self.amplitudes[state_index]

    def is_normalized(self, tolerance: float = 1e-10) -> bool:
        """
        Check whether the state satisfies the normalization condition.

        Args:
            tolerance: Allowed numerical error.

        Returns:
            True if the state is normalized.
        """

        total_probability = sum(self.probabilities())

        return abs(total_probability - 1.0) <= tolerance

    def _validate_state_index(self, state_index: int) -> None:
        """Validate a basis-state index."""

        if not isinstance(state_index, int):
            raise TypeError("State index must be an integer.")

        if not 0 <= state_index < self.dimension:
            raise IndexError(
                f"State index must be between 0 and {self.dimension - 1}."
            )

    def __repr__(self) -> str:
        """Return a useful representation for debugging."""

        return (
            f"QuantumState("
            f"num_qubits={self.num_qubits}, "
            f"dimension={self.dimension}, "
            f"amplitudes={self.amplitudes}"
            f")"
        )