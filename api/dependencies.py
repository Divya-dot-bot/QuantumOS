"""Shared QuantumOS API dependencies."""

from qos.runtime.runtime import QuantumRuntime


_runtime = QuantumRuntime()


def get_runtime() -> QuantumRuntime:
    """Return the shared QuantumOS runtime instance."""
    return _runtime