"""
QuantumOS Resources - Resource

Defines the generic computational resource abstraction used by
QuantumOS resource management.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ResourceType(str, Enum):
    """Types of computational resources supported by QuantumOS."""

    SIMULATOR = "simulator"
    QPU = "qpu"
    EMULATOR = "emulator"


class ResourceStatus(str, Enum):
    """Operational state of a computational resource."""

    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


@dataclass
class Resource:
    """
    Represents computational capacity available to QuantumOS.

    The class supports both the current resource model and the
    older compatibility API:

        Resource(
            resource_id="qvm-1",
            name="Local QVM",
            backend="qvm",
        )
    """

    resource_id: str
    name: str

    resource_type: ResourceType = ResourceType.SIMULATOR
    num_qubits: int = 1

    status: ResourceStatus = ResourceStatus.AVAILABLE

    supported_operations: set[str] = field(
        default_factory=set
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    backend: str | None = None

    def __post_init__(self) -> None:
        """Validate resource configuration."""

        if not isinstance(self.resource_id, str):
            raise TypeError(
                "resource_id must be a string"
            )

        if not self.resource_id.strip():
            raise ValueError(
                "resource_id cannot be empty"
            )

        if not isinstance(self.name, str):
            raise TypeError(
                "name must be a string"
            )

        if not self.name.strip():
            raise ValueError(
                "name cannot be empty"
            )

        if not isinstance(
            self.resource_type,
            ResourceType,
        ):
            raise TypeError(
                "resource_type must be a ResourceType"
            )

        if not isinstance(
            self.num_qubits,
            int,
        ) or isinstance(
            self.num_qubits,
            bool,
        ):
            raise TypeError(
                "num_qubits must be an integer"
            )

        if self.num_qubits < 1:
            raise ValueError(
                "num_qubits must be at least 1"
            )

        if not isinstance(
            self.status,
            ResourceStatus,
        ):
            raise TypeError(
                "status must be a ResourceStatus"
            )

        if not isinstance(
            self.supported_operations,
            set,
        ):
            raise TypeError(
                "supported_operations must be a set"
            )

        self.supported_operations = {
            operation.strip().lower()
            for operation in self.supported_operations
            if isinstance(operation, str)
            and operation.strip()
        }

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise TypeError(
                "metadata must be a dictionary"
            )

        if self.backend is not None:
            if not isinstance(self.backend, str):
                raise TypeError(
                    "backend must be a string or None"
                )

            if not self.backend.strip():
                raise ValueError(
                    "backend cannot be empty"
                )

    # ------------------------------------------------------------------
    # Backward-compatible availability API
    # ------------------------------------------------------------------

    @property
    def available(self) -> bool:
        """Backward-compatible availability property."""

        return self.is_available

    @available.setter
    def available(self, value: bool) -> None:
        """Backward-compatible availability setter."""

        if not isinstance(value, bool):
            raise TypeError(
                "available must be a boolean"
            )

        if value:
            self.mark_available()
        else:
            if self.status == ResourceStatus.AVAILABLE:
                self.status = ResourceStatus.OFFLINE
            else:
                self.status = ResourceStatus.OFFLINE

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    @property
    def is_available(self) -> bool:
        """Return True if the resource can accept work."""

        return self.status == ResourceStatus.AVAILABLE

    @property
    def is_busy(self) -> bool:
        """Return True if the resource is currently busy."""

        return self.status == ResourceStatus.BUSY

    def mark_busy(self) -> None:
        """Mark the resource as busy."""

        if self.status != ResourceStatus.AVAILABLE:
            raise RuntimeError(
                f"resource '{self.resource_id}' cannot be marked "
                f"busy while status is '{self.status.value}'"
            )

        self.status = ResourceStatus.BUSY

    def mark_available(self) -> None:
        """Mark the resource as available."""

        if self.status == ResourceStatus.OFFLINE:
            self.status = ResourceStatus.AVAILABLE
            return

        if self.status == ResourceStatus.MAINTENANCE:
            raise RuntimeError(
                f"resource '{self.resource_id}' is under maintenance"
            )

        self.status = ResourceStatus.AVAILABLE

    def mark_offline(self) -> None:
        """Take the resource offline."""

        self.status = ResourceStatus.OFFLINE

    def mark_maintenance(self) -> None:
        """Put the resource into maintenance."""

        self.status = ResourceStatus.MAINTENANCE

    # ------------------------------------------------------------------
    # Capability checks
    # ------------------------------------------------------------------

    def supports_qubits(self, num_qubits: int) -> bool:
        """Check whether the resource can handle a given qubit count."""

        if not isinstance(num_qubits, int):
            raise TypeError(
                "num_qubits must be an integer"
            )

        if num_qubits < 1:
            raise ValueError(
                "num_qubits must be at least 1"
            )

        return num_qubits <= self.num_qubits

    def supports_operation(self, operation: str) -> bool:
        """Check whether a quantum operation is supported."""

        if not isinstance(operation, str):
            raise TypeError(
                "operation must be a string"
            )

        return (
            operation.strip().lower()
            in self.supported_operations
        )

    def supports_operations(
        self,
        operations: set[str] | list[str] | tuple[str, ...],
    ) -> bool:
        """Check whether all requested operations are supported."""

        normalized = {
            operation.strip().lower()
            for operation in operations
            if isinstance(operation, str)
        }

        return normalized.issubset(
            self.supported_operations
        )

    def can_run(
        self,
        *,
        num_qubits: int,
        operations: set[str] | list[str] | tuple[str, ...],
    ) -> bool:
        """Determine whether this resource can execute a workload."""

        if not self.is_available:
            return False

        if not self.supports_qubits(num_qubits):
            return False

        return self.supports_operations(operations)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def summary(self) -> dict[str, Any]:
        """Return a serializable resource description."""

        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "backend": self.backend,
            "resource_type": self.resource_type.value,
            "num_qubits": self.num_qubits,
            "status": self.status.value,
            "available": self.available,
            "supported_operations": sorted(
                self.supported_operations
            ),
            "metadata": dict(self.metadata),
        }