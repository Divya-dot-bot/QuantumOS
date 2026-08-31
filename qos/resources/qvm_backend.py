"""
QuantumOS Resources - QVM Backend

Concrete backend that executes quantum circuits using
the built-in Quantum Virtual Machine.
"""

from __future__ import annotations

from qos.compiler.transpiler import ExecutableCircuit
from qos.core.circuit import QuantumCircuit
from qos.core.qvm import QuantumVirtualMachine
from qos.resources.backend import Backend, BackendResult


class QVMBackend(Backend):
    """
    QuantumOS backend powered by the built-in QVM.

    This connects the resource/backend layer to the actual
    state-vector quantum simulator.
    """

    def __init__(
    self,
    name: str = "qvm",
    num_qubits: int = 32,
    resource_id: str | None = None,
) -> None:
     super().__init__(
        name=name,
        backend_type="simulator",
        num_qubits=num_qubits,
        resource_id=resource_id,
    )

     self.resource.supported_operations = {
        "i",
        "x",
        "y",
        "z",
        "h",
        "s",
        "t",
        "cx",
    }

     self.qvm = QuantumVirtualMachine()

    def execute(
        self,
        circuit: ExecutableCircuit,
        shots: int = 1000,
        *,
        job_id: str | None = None,
    ) -> BackendResult:
        """
        Execute a compiled circuit using the QVM.
        """

        if not isinstance(
            circuit,
            ExecutableCircuit,
        ):
            raise TypeError(
                "circuit must be an ExecutableCircuit"
            )

        if not isinstance(shots, int) or isinstance(shots, bool):
            raise TypeError(
                "shots must be an integer"
            )

        if shots < 1:
            raise ValueError(
                "shots must be at least 1"
            )

        if circuit.num_qubits > self.num_qubits:
            raise ValueError(
                f"circuit requires {circuit.num_qubits} qubits, "
                f"but backend supports only {self.num_qubits}"
            )

        quantum_circuit = QuantumCircuit(
            circuit.num_qubits
        )

        for instruction in circuit.instructions:
            operation = instruction.operation.lower()
            qubits = instruction.qubits

            if operation == "i":
                quantum_circuit.i(qubits[0])

            elif operation == "x":
                quantum_circuit.x(qubits[0])

            elif operation == "y":
                quantum_circuit.y(qubits[0])

            elif operation == "z":
                quantum_circuit.z(qubits[0])

            elif operation == "h":
                quantum_circuit.h(qubits[0])

            elif operation == "s":
                quantum_circuit.s(qubits[0])

            elif operation == "t":
                quantum_circuit.t(qubits[0])

            elif operation == "cx":
                quantum_circuit.cx(
                    qubits[0],
                    qubits[1],
                )

            else:
                raise ValueError(
                    f"unsupported operation '{instruction.operation}'"
                )

        counts = self.qvm.run(
            quantum_circuit,
            shots=shots,
        )

        return BackendResult(
            counts=counts,
            shots=shots,
            backend=self.backend_id,
            job_id=job_id,
            metadata={
                "engine": "qvm",
                "simulation": "state-vector",
            },
        )