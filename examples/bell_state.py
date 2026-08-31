"""
QuantumOS - Bell State Example

Demonstrates the creation and measurement of a Bell state
using the QuantumOS Quantum Virtual Machine.
"""

from qos import QuantumCircuit, QuantumVirtualMachine


def main() -> None:
    """Create and execute a Bell-state circuit."""

    # Create a two-qubit circuit.
    circuit = QuantumCircuit(2)

    # Put qubit 0 into superposition.
    circuit.h(0)

    # Entangle qubit 0 with qubit 1.
    circuit.cx(0, 1)

    print("=== QuantumOS Bell State Example ===")
    print()

    print("Circuit:")
    print("q0 ── H ──●──")
    print("          │")
    print("q1 ───────X──")
    print()

    print(f"Qubits: {circuit.num_qubits}")
    print(f"Gates:  {circuit.gate_count()}")
    print(f"Depth:  {circuit.depth()}")
    print()

    # Create the Quantum Virtual Machine.
    qvm = QuantumVirtualMachine()

    # Simulate the circuit without measurement.
    state = qvm.simulate(circuit)

    print("Final statevector:")

    for index, amplitude in enumerate(state.amplitudes):
        print(
            f"|{index:02b}>: "
            f"{amplitude.real:.6f}"
            f"{amplitude.imag:+.6f}i"
        )

    print()

    # Perform 1000 measurements.
    shots = 1000

    results = qvm.run(
        circuit,
        shots=shots,
    )

    print(f"Measurement results ({shots} shots):")

    for state_name, count in results.items():
        percentage = (count / shots) * 100

        print(
            f"|{state_name}>: "
            f"{count:4d} "
            f"({percentage:6.2f}%)"
        )


if __name__ == "__main__":
    main()