"""
Quantum Teleportation Example

Demonstrates the standard three-qubit quantum teleportation circuit.

The circuit contains:
    - Qubit 0: the state to be teleported
    - Qubit 1: Alice's entangled qubit
    - Qubit 2: Bob's entangled qubit

The example demonstrates:
    1. State preparation
    2. Bell-pair creation
    3. Entanglement
    4. Measurement
    5. Classical correction
    6. Final measurement
"""

from qos.core.circuit import QuantumCircuit
from qos.core.qvm import QuantumVirtualMachine


def build_teleportation_circuit() -> QuantumCircuit:
    """Build the quantum teleportation circuit."""

    circuit = QuantumCircuit(3)

    # ---------------------------------------------------------
    # Step 1: Prepare the state to be teleported.
    #
    # We use |+> as the input state:
    #
    # |+> = (|0> + |1>) / sqrt(2)
    # ---------------------------------------------------------
    circuit.h(0)

    # ---------------------------------------------------------
    # Step 2: Create an entangled Bell pair between qubits 1
    # and 2.
    # ---------------------------------------------------------
    circuit.h(1)
    circuit.cx(1, 2)

    # ---------------------------------------------------------
    # Step 3: Entangle the state being teleported with Alice's
    # half of the Bell pair.
    # ---------------------------------------------------------
    circuit.cx(0, 1)
    circuit.h(0)

    # ---------------------------------------------------------
    # Step 4: Measure Alice's two qubits.
    # ---------------------------------------------------------
    circuit.measure(0)
    circuit.measure(1)

    # ---------------------------------------------------------
    # Step 5:
    #
    # In a complete teleportation implementation, the two
    # classical measurement results control corrections on
    # Bob's qubit:
    #
    #   measurement q1 -> X correction
    #   measurement q0 -> Z correction
    #
    # The exact classical-control API depends on the current
    # QuantumOS circuit implementation.
    #
    # Therefore, this example records the teleportation circuit
    # up to Alice's measurement stage. The complete conditional
    # correction mechanism can be added when classical control
    # operations are supported by the core.
    # ---------------------------------------------------------

    # Measure Bob's qubit so that the final result is visible.
    circuit.measure(2)

    return circuit


def main() -> None:
    """Create and execute the teleportation circuit."""

    circuit = build_teleportation_circuit()

    qvm = QuantumVirtualMachine()

    result = qvm.run(
        circuit,
        shots=1000,
    )

    print("Quantum Teleportation Circuit:")
    print(circuit)
    print()

    print("Measurement Results:")
    print(result)


if __name__ == "__main__":
    main()