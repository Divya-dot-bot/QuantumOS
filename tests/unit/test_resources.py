"""Unit tests for QuantumOS resource management."""

from qos.resources.resource import Resource
from qos.resources.manager import ResourceManager
from qos.resources.backend import Backend


def test_resource_creation():
    """A resource should store its basic information."""
    resource = Resource(
        resource_id="qvm-1",
        name="Local QVM",
        backend="qvm",
    )

    assert resource.resource_id == "qvm-1"
    assert resource.name == "Local QVM"
    assert resource.backend == "qvm"


def test_resource_is_available_by_default():
    """A newly created resource should be available."""
    resource = Resource(
        resource_id="qvm-1",
        name="Local QVM",
        backend="qvm",
    )

    assert resource.available is True


def test_resource_can_be_marked_unavailable():
    """A resource should allow its availability to change."""
    resource = Resource(
        resource_id="qvm-1",
        name="Local QVM",
        backend="qvm",
    )

    resource.available = False

    assert resource.available is False


def test_backend_creation():
    """A backend should store its identity and capabilities."""
    backend = Backend(
        name="qvm",
        backend_type="simulator",
        num_qubits=4,
    )

    assert backend.name == "qvm"
    assert backend.backend_type == "simulator"
    assert backend.num_qubits == 4


def test_resource_manager_can_register_resource():
    """The resource manager should register resources."""
    manager = ResourceManager()

    resource = Resource(
        resource_id="qvm-1",
        name="Local QVM",
        backend="qvm",
    )

    manager.register(resource)

    assert manager.get("qvm-1") is resource


def test_resource_manager_lists_resources():
    """The resource manager should return registered resources."""
    manager = ResourceManager()

    resource_a = Resource(
        resource_id="qvm-1",
        name="Local QVM",
        backend="qvm",
    )

    resource_b = Resource(
        resource_id="qvm-2",
        name="Second QVM",
        backend="qvm",
    )

    manager.register(resource_a)
    manager.register(resource_b)

    resources = manager.list_resources()

    assert len(resources) == 2
    assert resource_a in resources
    assert resource_b in resources


def test_resource_manager_returns_available_resources():
    """Only available resources should be returned."""
    manager = ResourceManager()

    available = Resource(
        resource_id="qvm-1",
        name="Available QVM",
        backend="qvm",
    )

    unavailable = Resource(
        resource_id="qvm-2",
        name="Unavailable QVM",
        backend="qvm",
    )

    unavailable.available = False

    manager.register(available)
    manager.register(unavailable)

    resources = manager.available_resources()

    assert available in resources
    assert unavailable not in resources


def test_resource_manager_removes_resource():
    """A registered resource should be removable."""
    manager = ResourceManager()

    resource = Resource(
        resource_id="qvm-1",
        name="Local QVM",
        backend="qvm",
    )

    manager.register(resource)
    manager.remove("qvm-1")

    assert manager.get("qvm-1") is None