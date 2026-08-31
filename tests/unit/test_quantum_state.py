"""
QuantumOS - Quantum State Tests

Unit tests for the QuantumState class.
"""

import math

import pytest

from qos.core import QuantumState


class TestQuantumStateInitialization:
    """Tests for QuantumState initialization."""

    def test_single_qubit_initial_state(self) -> None:
        """A single qubit should start in |0>."""

        state = QuantumState(1)

        assert state.num_qubits == 1
        assert state.dimension == 2

        assert state.amplitudes == [
            1 + 0j,
            0 + 0j,
        ]

    def test_two_qubit_initial_state(self) -> None:
        """Two qubits should start in |00>."""

        state = QuantumState(2)

        assert state.num_qubits == 2
        assert state.dimension == 4

        assert state.amplitudes == [
            1 + 0j,
            0 + 0j,
            0 + 0j,
            0 + 0j,
        ]

    def test_dimension_grows_exponentially(self) -> None:
        """The state-vector dimension should be 2^n."""

        for num_qubits in range(1, 6):
            state = QuantumState(num_qubits)

            assert state.dimension == 2**num_qubits

    def test_zero_qubits_are_rejected(self) -> None:
        """A quantum system must contain at least one qubit."""

        with pytest.raises(ValueError):
            QuantumState(0)

    def test_negative_qubits_are_rejected(self) -> None:
        """Negative qubit counts must be rejected."""

        with pytest.raises(ValueError):
            QuantumState(-1)


class TestQuantumStateAmplitudes:
    """Tests for amplitude access and modification."""

    def test_get_initial_amplitude(self) -> None:
        """The |0> amplitude should initially be 1."""

        state = QuantumState(1)

        assert state.get_amplitude(0) == 1 + 0j
        assert state.get_amplitude(1) == 0 + 0j

    def test_set_amplitude(self) -> None:
        """An amplitude should be changeable."""

        state = QuantumState(1)

        state.set_amplitude(1, 1 / math.sqrt(2))

        assert math.isclose(
            state.get_amplitude(1).real,
            1 / math.sqrt(2),
        )

    def test_invalid_state_index_is_rejected(self) -> None:
        """Indexes outside the state vector must be rejected."""

        state = QuantumState(2)

        with pytest.raises(IndexError):
            state.get_amplitude(4)

    def test_negative_state_index_is_rejected(self) -> None:
        """Negative indexes must be rejected."""

        state = QuantumState(2)

        with pytest.raises(IndexError):
            state.get_amplitude(-1)

    def test_non_integer_state_index_is_rejected(self) -> None:
        """State indexes must be integers."""

        state = QuantumState(2)

        with pytest.raises(TypeError):
            state.get_amplitude(1.5)  # type: ignore[arg-type]


class TestQuantumStateNormalization:
    """Tests for quantum-state normalization."""

    def test_initial_state_is_normalized(self) -> None:
        """The initial |0...0> state must be normalized."""

        state = QuantumState(3)

        assert state.is_normalized()

    def test_normalization(self) -> None:
        """Normalization should make total probability equal to 1."""

        state = QuantumState(1)

        state.set_amplitude(0, 3)
        state.set_amplitude(1, 4)

        assert not state.is_normalized()

        state.normalize()

        assert state.is_normalized()

    def test_normalization_preserves_relative_amplitudes(self) -> None:
        """Normalization should preserve amplitude ratios."""

        state = QuantumState(1)

        state.set_amplitude(0, 3)
        state.set_amplitude(1, 4)

        state.normalize()

        assert math.isclose(
            abs(state.get_amplitude(0)),
            0.6,
            rel_tol=1e-10,
        )

        assert math.isclose(
            abs(state.get_amplitude(1)),
            0.8,
            rel_tol=1e-10,
        )

    def test_zero_state_cannot_be_normalized(self) -> None:
        """A zero-magnitude state cannot be normalized."""

        state = QuantumState(1)

        state.set_amplitude(0, 0)
        state.set_amplitude(1, 0)

        with pytest.raises(ValueError):
            state.normalize()


class TestQuantumStateProbabilities:
    """Tests for measurement probabilities."""

    def test_initial_probabilities(self) -> None:
        """|0> should have probability 1 and |1> probability 0."""

        state = QuantumState(1)

        probabilities = state.probabilities()

        assert probabilities == [
            1.0,
            0.0,
        ]

    def test_probability_of_specific_state(self) -> None:
        """The probability should equal |amplitude|^2."""

        state = QuantumState(1)

        amplitude = 1 / math.sqrt(2)

        state.set_amplitude(0, amplitude)
        state.set_amplitude(1, amplitude)

        assert math.isclose(
            state.probability(0),
            0.5,
            rel_tol=1e-10,
        )

        assert math.isclose(
            state.probability(1),
            0.5,
            rel_tol=1e-10,
        )

    def test_probabilities_sum_to_one(self) -> None:
        """A normalized state must have total probability 1."""

        state = QuantumState(2)

        amplitude = 0.5

        for index in range(4):
            state.set_amplitude(index, amplitude)

        assert state.is_normalized()

        assert math.isclose(
            sum(state.probabilities()),
            1.0,
            rel_tol=1e-10,
        )


class TestQuantumStateRepresentation:
    """Tests for debugging and representation."""

    def test_repr_contains_useful_information(self) -> None:
        """repr() should identify the object and its dimensions."""

        state = QuantumState(2)

        representation = repr(state)

        assert "QuantumState" in representation
        assert "num_qubits=2" in representation
        assert "dimension=4" in representation