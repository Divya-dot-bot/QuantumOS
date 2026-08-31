"""
QuantumOS Resources - Backend

Defines the backend abstraction used to execute compiled quantum
workloads.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from qos.compiler.transpiler import ExecutableCircuit
from qos.resources.resource import (
    Resource,
    ResourceStatus,
    ResourceType,
)


@dataclass(frozen=True)
class BackendResult:
    """Result returned by a quantum backend."""

    counts: dict[str, int]
    shots: int
    backend: str
    job_id: str | None = None
    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        if not isinstance(self.counts, dict):
            raise TypeError(
                "counts must be a dictionary"
            )

        if not isinstance(
            self.shots,
            int,
        ) or isinstance(
            self.shots,
            bool,
        ):
            raise TypeError(
                "shots must be an integer"
            )

        if self.shots < 1:
            raise ValueError(
                "shots must be at least 1"
            )

        total_counts = sum(
            self.counts.values()
        )

        if total_counts != self.shots:
            raise ValueError(
                "measurement counts must sum to shots"
            )

        if not isinstance(
            self.backend,
            str,
        ) or not self.backend.strip():
            raise ValueError(
                "backend must be a non-empty string"
            )


class Backend:
    """
    QuantumOS execution backend.

    Supports both:

    New API:

        Backend(resource)

    Compatibility API:

        Backend(
            name="qvm",
            backend_type="simulator",
            num_qubits=4,
        )
    """

    def __init__(
        self,
        resource: Resource | None = None,
        *,
        name: str | None = None,
        backend_type: str | ResourceType = "simulator",
        num_qubits: int = 1,
        resource_id: str | None = None,
    ) -> None:

        if resource is not None:

            if not isinstance(resource, Resource):
                raise TypeError(
                    "resource must be a Resource"
                )

            self.resource = resource
            return

        if name is None:
            raise TypeError(
                "either resource or name must be provided"
            )

        if not isinstance(name, str):
            raise TypeError(
                "name must be a string"
            )

        if isinstance(backend_type, ResourceType):
            resource_type = backend_type
        else:
            try:
                resource_type = ResourceType(
                    backend_type
                )
            except ValueError as exc:
                raise ValueError(
                    f"unsupported backend_type: {backend_type}"
                ) from exc

        self.resource = Resource(
            resource_id=(
                resource_id
                if resource_id is not None
                else name
            ),
            name=name,
            resource_type=resource_type,
            num_qubits=num_qubits,
            backend=name,
        )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Return the backend name."""

        return self.resource.name

    @property
    def backend_id(self) -> str:
        """Return the backend identifier."""

        return self.resource.resource_id

    @property
    def backend_type(self) -> str:
        """Backward-compatible backend type."""

        return self.resource.resource_type.value

    @property
    def resource_type(self) -> ResourceType:
        """Return the backend resource type."""

        return self.resource.resource_type

    @property
    def num_qubits(self) -> int:
        """Return the backend's qubit capacity."""

        return self.resource.num_qubits

    @property
    def status(self) -> ResourceStatus:
        """Return backend status."""

        return self.resource.status

    @property
    def is_available(self) -> bool:
        """Return whether the backend is currently available."""

        return self.resource.is_available

    @property
    def is_busy(self) -> bool:
        """Return whether the backend is currently busy."""

        return self.resource.is_busy

    @property
    def available(self) -> bool:
        """Backward-compatible availability property."""

    @available.setter
    def available(self, value: bool) -> None:
        self.resource.available = value

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def can_execute(
        self,
        circuit: ExecutableCircuit,
    ) -> bool:
        """Determine whether the backend can execute a circuit."""

        if not isinstance(
            circuit,
            ExecutableCircuit,
        ):
            raise TypeError(
                "circuit must be an ExecutableCircuit"
            )

        operations = {
            instruction.operation
            for instruction in circuit.instructions
        }

        return self.resource.can_run(
            num_qubits=circuit.num_qubits,
            operations=operations,
        )

    def execute(
        self,
        circuit: ExecutableCircuit,
        shots: int = 1000,
        *,
        job_id: str | None = None,
    ) -> BackendResult:
        """
        Execute a compiled circuit.

        Base Backend does not provide a concrete execution engine.
        """

        raise NotImplementedError(
            f"backend '{self.name}' does not implement execute()"
        )

    # ------------------------------------------------------------------
    # Resource lifecycle
    # ------------------------------------------------------------------

    def acquire(self) -> None:
        """Mark this backend's resource as busy."""

        self.resource.mark_busy()

    def release(self) -> None:
        """Mark this backend's resource as available."""

        self.resource.mark_available()

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def summary(self) -> dict[str, Any]:
        """Return backend information."""

        return {
            "backend_id": self.backend_id,
            "name": self.name,
            "backend_type": self.backend_type,
            "resource_type": self.resource_type.value,
            "num_qubits": self.num_qubits,
            "status": self.status.value,
            "available": self.is_available,
        }


class BackendRegistry:
    """Registry of available QuantumOS backends."""

    def __init__(self) -> None:
        self._backends: dict[str, Backend] = {}

    def register(
        self,
        backend: Backend,
    ) -> None:
        """Register a backend."""

        if not isinstance(
            backend,
            Backend,
        ):
            raise TypeError(
                "backend must be a Backend"
            )

        if backend.backend_id in self._backends:
            raise ValueError(
                f"backend '{backend.backend_id}' "
                f"is already registered"
            )

        self._backends[
            backend.backend_id
        ] = backend

    def unregister(
        self,
        backend_id: str,
    ) -> Backend | None:
        """Remove and return a backend."""

        return self._backends.pop(
            backend_id,
            None,
        )

    def get(
        self,
        backend_id: str,
    ) -> Backend | None:
        """Return a backend by ID."""

        return self._backends.get(
            backend_id
        )

    def list_backends(self) -> list[Backend]:
        """Return all registered backends."""

        return list(
            self._backends.values()
        )

    def available_backends(self) -> list[Backend]:
        """Return currently available backends."""

        return [
            backend
            for backend in self._backends.values()
            if backend.is_available
        ]

    def find_capable(
        self,
        circuit: ExecutableCircuit,
    ) -> list[Backend]:
        """Return available capable backends."""

        return [
            backend
            for backend in self._backends.values()
            if backend.is_available
            and backend.can_execute(circuit)
        ]

    def __len__(self) -> int:
        return len(self._backends)

    def __contains__(
        self,
        backend_id: str,
    ) -> bool:
        return backend_id in self._backends