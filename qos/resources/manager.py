"""
QuantumOS Resources - Resource Manager

Provides resource and backend registration, discovery, allocation,
and compatibility between the legacy Resource API and Backend API.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from qos.compiler.transpiler import ExecutableCircuit
from qos.resources.backend import Backend, BackendRegistry
from qos.resources.qvm_backend import QVMBackend
from qos.resources.resource import Resource
from qos.scheduler.job import QuantumJob


class ResourceAllocationError(RuntimeError):
    """Raised when a resource cannot be allocated."""


@dataclass(frozen=True)
class ResourceAllocation:
    """Represents a backend allocation for a job."""

    job_id: str
    backend_id: str
    backend_name: str


class ResourceManager:
    """Manage QuantumOS resources and execution backends."""

    def __init__(
        self,
        registry: BackendRegistry | None = None,
    ) -> None:

        self.registry = (
            registry
            if registry is not None
            else BackendRegistry()
        )

        self._resources: dict[str, Resource] = {}

        self._allocations: dict[
            str,
            ResourceAllocation,
        ] = {}

        # The built-in QVM is available by default.
        if registry is None:
            self.register_backend(QVMBackend())

    # ------------------------------------------------------------------
    # Resource registration
    # ------------------------------------------------------------------

    def register(
        self,
        resource: Resource | Backend,
    ) -> None:
        """Register either a Resource or Backend."""

        if isinstance(resource, Resource):
            if resource.resource_id in self._resources:
                raise ValueError(
                    f"resource '{resource.resource_id}' is already registered"
                )

            self._resources[resource.resource_id] = resource
            return

        if isinstance(resource, Backend):
            self.register_backend(resource)
            return

        raise TypeError(
            "resource must be a Resource or Backend"
        )

    def get(
        self,
        resource_id: str,
    ) -> Resource | Backend | None:
        """Return a registered resource or backend."""

        resource = self._resources.get(resource_id)

        if resource is not None:
            return resource

        return self.registry.get(resource_id)

    def get_resource(
        self,
        resource_id: str,
    ) -> Resource | None:
        """
        Return a resource by ID.

        Backend resources are exposed through this method as well.
        """

        resource = self._resources.get(resource_id)

        if resource is not None:
            return resource

        backend = self.registry.get(resource_id)

        if backend is not None:
            return backend.resource

        return None

    def list_resources(self) -> list[Resource]:
        """
        Return all resources.

        Backend resources are automatically included so that
        execution backends such as the built-in QVM appear in
        the Memory dashboard.
        """

        resources: dict[str, Resource] = dict(
            self._resources
        )

        for backend in self.registry.list_backends():
            resources.setdefault(
                backend.backend_id,
                backend.resource,
            )

        return list(resources.values())

    def available_resources(self) -> list[Resource]:
        """Return currently available resources."""

        return [
            resource
            for resource in self.list_resources()
            if resource.is_available
        ]

    def remove(
        self,
        resource_id: str,
    ) -> Resource | Backend | None:
        """Remove a resource or backend."""

        resource = self._resources.pop(
            resource_id,
            None,
        )

        if resource is not None:
            return resource

        return self.registry.unregister(
            resource_id
        )

    # ------------------------------------------------------------------
    # Backend registration
    # ------------------------------------------------------------------

    def register_backend(
        self,
        backend: Backend,
    ) -> None:
        """Register an execution backend."""

        self.registry.register(backend)

    def unregister_backend(
        self,
        backend_id: str,
    ) -> Backend | None:
        """Unregister an execution backend."""

        return self.registry.unregister(
            backend_id
        )

    def get_backend(
        self,
        backend_id: str,
    ) -> Backend | None:
        """Return a backend by ID."""

        return self.registry.get(backend_id)

    # ------------------------------------------------------------------
    # Backend discovery
    # ------------------------------------------------------------------

    def list_backends(self) -> list[Backend]:
        """Return all registered backends."""

        return self.registry.list_backends()

    def available_backends(self) -> list[Backend]:
        """Return currently available backends."""

        return self.registry.available_backends()

    def capable_backends(
        self,
        circuit: ExecutableCircuit,
    ) -> list[Backend]:
        """Return available backends capable of running a circuit."""

        return self.registry.find_capable(circuit)

    # ------------------------------------------------------------------
    # Allocation
    # ------------------------------------------------------------------

    def allocate(
        self,
        job: QuantumJob,
        circuit: ExecutableCircuit,
    ) -> ResourceAllocation:
        """Allocate a suitable backend to a job."""

        if not isinstance(job, QuantumJob):
            raise TypeError(
                "job must be a QuantumJob"
            )

        if not isinstance(circuit, ExecutableCircuit):
            raise TypeError(
                "circuit must be an ExecutableCircuit"
            )

        if job.id in self._allocations:
            raise ResourceAllocationError(
                f"job '{job.id}' already has a resource allocation"
            )

        backend = self._select_backend(
            job,
            circuit,
        )

        if backend is None:
            raise ResourceAllocationError(
                self._allocation_error_message(
                    job,
                    circuit,
                )
            )

        backend.acquire()

        allocation = ResourceAllocation(
            job_id=job.id,
            backend_id=backend.backend_id,
            backend_name=backend.name,
        )

        self._allocations[job.id] = allocation

        return allocation

    def release(
        self,
        job_id: str,
    ) -> ResourceAllocation | None:
        """Release a resource allocated to a job."""

        allocation = self._allocations.pop(
            job_id,
            None,
        )

        if allocation is None:
            return None

        backend = self.registry.get(
            allocation.backend_id
        )

        if backend is not None:
            backend.release()

        return allocation

    def get_allocation(
        self,
        job_id: str,
    ) -> ResourceAllocation | None:
        """Return the allocation for a job."""

        return self._allocations.get(job_id)

    def allocated_backend(
        self,
        job_id: str,
    ) -> Backend | None:
        """Return the backend allocated to a job."""

        allocation = self.get_allocation(job_id)

        if allocation is None:
            return None

        return self.registry.get(
            allocation.backend_id
        )

    # ------------------------------------------------------------------
    # Resource status
    # ------------------------------------------------------------------

    def is_allocated(
        self,
        job_id: str,
    ) -> bool:
        """Return whether a job has an active allocation."""

        return job_id in self._allocations

    @property
    def allocation_count(self) -> int:
        """Return the number of active allocations."""

        return len(self._allocations)

    def allocations(self) -> list[ResourceAllocation]:
        """Return all active allocations."""

        return list(
            self._allocations.values()
        )

    # ------------------------------------------------------------------
    # Backend selection
    # ------------------------------------------------------------------

    def _select_backend(
        self,
        job: QuantumJob,
        circuit: ExecutableCircuit,
    ) -> Backend | None:

        if job.backend is not None:
            backend = self.registry.get(
                job.backend
            )

            if backend is None:
                return None

            if not backend.is_available:
                return None

            if not backend.can_execute(circuit):
                return None

            return backend

        capable = self.capable_backends(circuit)

        if not capable:
            return None

        return self._rank_backends(capable)[0]

    @staticmethod
    def _rank_backends(
        backends: list[Backend],
    ) -> list[Backend]:
        """Rank candidate backends."""

        return sorted(
            backends,
            key=lambda backend: (
                backend.resource_type.value != "simulator",
                backend.num_qubits,
            ),
        )

    @staticmethod
    def _allocation_error_message(
        job: QuantumJob,
        circuit: ExecutableCircuit,
    ) -> str:

        if job.backend is not None:
            return (
                f"backend '{job.backend}' is unavailable or "
                "cannot execute the requested circuit"
            )

        return (
            "no available backend can execute the requested "
            f"circuit requiring {circuit.num_qubits} qubits"
        )

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self) -> dict[str, Any]:
        """Return resource manager status."""

        resources = self.list_resources()

        return {
            "resource_count": len(resources),
            "backend_count": len(self.registry),
            "available_resource_count": len(
                [
                    resource
                    for resource in resources
                    if resource.is_available
                ]
            ),
            "available_backend_count": len(
                self.available_backends()
            ),
            "allocation_count": self.allocation_count,
            "resources": [
                resource.summary()
                for resource in resources
            ],
            "backends": [
                backend.summary()
                for backend in self.list_backends()
            ],
        }