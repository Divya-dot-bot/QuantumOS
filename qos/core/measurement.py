"""
QuantumOS - Measurement

Utilities for measuring quantum states and sampling classical
measurement results from probability distributions.
"""

from __future__ import annotations

import random
from collections import Counter
from typing import Sequence


def _validate_probabilities(
    probabilities: Sequence[float],
    tolerance: float = 1e-10,
) -> None:
    """
    Validate a quantum probability distribution.

    Args:
        probabilities: Sequence of measurement probabilities.
        tolerance: Numerical tolerance for validation.

    Raises:
        ValueError: If probabilities are invalid.
        TypeError: If a probability is not numeric.
    """

    if not probabilities:
        raise ValueError("probabilities cannot be empty")

    if tolerance < 0:
        raise ValueError("tolerance must not be negative")

    total = 0.0

    for probability in probabilities:
        if not isinstance(probability, (int, float)):
            raise TypeError(
                "probabilities must contain numeric values"
            )

        if probability < -tolerance:
            raise ValueError(
                "probabilities cannot be negative"
            )

        total += probability

    if abs(total - 1.0) > tolerance:
        raise ValueError(
            f"probabilities must sum to 1, got {total}"
        )


def probabilities_to_counts(
    probabilities: Sequence[float],
    shots: int,
) -> list[int]:
    """
    Convert a probability distribution into deterministic counts.

    This helper uses the largest-remainder method so that the resulting
    counts always sum exactly to the requested number of shots.

    Args:
        probabilities: Probability distribution.
        shots: Number of measurements.

    Returns:
        Integer count for each basis state.

    Raises:
        ValueError: If shots is invalid or probabilities are invalid.
    """

    if not isinstance(shots, int) or isinstance(shots, bool):
        raise TypeError("shots must be an integer")

    if shots < 1:
        raise ValueError("shots must be at least 1")

    _validate_probabilities(probabilities)

    raw_counts = [
        probability * shots
        for probability in probabilities
    ]

    counts = [
        int(value)
        for value in raw_counts
    ]

    remaining = shots - sum(counts)

    remainders = sorted(
        range(len(probabilities)),
        key=lambda index: raw_counts[index] - counts[index],
        reverse=True,
    )

    for index in remainders[:remaining]:
        counts[index] += 1

    return counts


def sample_measurements(
    probabilities: Sequence[float],
    shots: int,
    *,
    rng: random.Random | None = None,
) -> Counter[str]:
    """
    Sample computational-basis measurement results.

    Args:
        probabilities:
            Probability associated with each computational-basis state.

        shots:
            Number of measurements to perform.

        rng:
            Optional random number generator. Supplying one makes tests
            deterministic and avoids relying on global random state.

    Returns:
        Counter mapping bitstrings to measurement counts.

    Example:

        probabilities = [0.5, 0.0, 0.0, 0.5]

        result might be:

        {
            "00": 497,
            "11": 503,
        }
    """

    if not isinstance(shots, int) or isinstance(shots, bool):
        raise TypeError("shots must be an integer")

    if shots < 1:
        raise ValueError("shots must be at least 1")

    _validate_probabilities(probabilities)

    generator = rng if rng is not None else random.Random()

    cumulative = []
    total = 0.0

    for probability in probabilities:
        total += max(0.0, float(probability))
        cumulative.append(total)

    # Protect against tiny floating-point differences.
    cumulative[-1] = 1.0

    num_qubits = _infer_num_qubits(len(probabilities))

    results: Counter[str] = Counter()

    for _ in range(shots):
        value = generator.random()

        for index, boundary in enumerate(cumulative):
            if value < boundary:
                bitstring = format(
                    index,
                    f"0{num_qubits}b",
                )

                results[bitstring] += 1
                break

    return results


def sample_state(
    amplitudes: Sequence[complex],
    shots: int,
    *,
    rng: random.Random | None = None,
) -> Counter[str]:
    """
    Sample measurements directly from a state vector.

    Args:
        amplitudes:
            Complex state-vector amplitudes.

        shots:
            Number of measurements.

        rng:
            Optional random number generator.

    Returns:
        Counter containing measured computational-basis states.
    """

    if not amplitudes:
        raise ValueError("amplitudes cannot be empty")

    probabilities = [
        abs(amplitude) ** 2
        for amplitude in amplitudes
    ]

    total = sum(probabilities)

    if total <= 0:
        raise ValueError(
            "cannot measure a zero-magnitude state"
        )

    # Measurement requires a normalized probability distribution.
    if abs(total - 1.0) > 1e-10:
        probabilities = [
            probability / total
            for probability in probabilities
        ]

    return sample_measurements(
        probabilities,
        shots,
        rng=rng,
    )


def measure_once(
    probabilities: Sequence[float],
    *,
    rng: random.Random | None = None,
) -> str:
    """
    Perform a single measurement.

    Args:
        probabilities:
            Probability distribution.

        rng:
            Optional random number generator.

    Returns:
        Measured computational-basis bitstring.
    """

    result = sample_measurements(
        probabilities,
        shots=1,
        rng=rng,
    )

    return next(iter(result))


def measure_state_once(
    amplitudes: Sequence[complex],
    *,
    rng: random.Random | None = None,
) -> str:
    """
    Perform a single measurement directly on a state vector.
    """

    result = sample_state(
        amplitudes,
        shots=1,
        rng=rng,
    )

    return next(iter(result))


def _infer_num_qubits(dimension: int) -> int:
    """
    Infer the number of qubits from a state-vector dimension.

    A valid n-qubit state vector has dimension 2^n.
    """

    if dimension < 1:
        raise ValueError(
            "state-vector dimension must be positive"
        )

    if dimension & (dimension - 1):
        raise ValueError(
            "state-vector dimension must be a power of two"
        )

    num_qubits = dimension.bit_length() - 1

    if 2**num_qubits != dimension:
        raise ValueError(
            "invalid state-vector dimension"
        )

    return num_qubits