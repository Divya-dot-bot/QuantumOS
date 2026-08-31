"""
Grover's Search Algorithm Example

Demonstrates the basic structure of Grover's search algorithm
using a two-qubit QuantumOS circuit.

For two qubits, the search space contains four states:

    00
    01
    10
    11

This example marks |11> as the target state.

The circuit demonstrates:

    1. Superposition
    2. Oracle
    3. Diffusion
    4. Measurement
"""

from qos.core.circuit import QuantumCircuit
from qos.core.qvm import QuantumVirtualMachine


def build_grover_circuit() -> QuantumCircuit:
    """Build a two-qubit Grover search circuit."""

    circuit = QuantumCircuit(2)

    # ---------------------------------------------------------
    # Step 1: Create an equal superposition of all four states.
    # ---------------------------------------------------------
    circuit.h(0)
    circuit.h(1)

    # ---------------------------------------------------------
    # Step 2: Oracle
    #
    # Mark the target state |11>.
    #
    # For a two-qubit search, a controlled-Z operation applies
    # a phase flip to |11>.
    # ---------------------------------------------------------
    circuit.cz(0, 1)

    # ---------------------------------------------------------
    # Step 3: Grover diffusion operator.
    #
    # H -> X -> CZ -> X -> H
    # ---------------------------------------------------------
    circuit.h(0)
    circuit.h(1)

    circuit.x(0)
    circuit.x(1)

    circuit.cz(0, 1)

    circuit.x(0)
    circuit.x(1)

    circuit.h(0)
    circuit.h(1)

    # ---------------------------------------------------------
    # Step 4: Measure both qubits.
    # ---------------------------------------------------------
    circuit.measure_all()

    return circuit


def main() -> None:
    """Create and execute the Grover search circuit."""

    circuit = build_grover_circuit()

    qvm = QuantumVirtualMachine()

    result = qvm.run(
        circuit,
        shots=1000,
    )

    print("Grover Search Circuit:")
    print(circuit)
    print()

    print("Measurement Results:")
    print(result)


if __name__ == "__main__":
    main()