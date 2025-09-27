import pytest

from magic_utils.registryManager import Registry
from .helper import set_register_registry
from .constants import REGISTER_A


@pytest.fixture
def registry():
    registry = Registry()
    yield registry
    registry.reset()

def test_registry_contains(registry):
    set_register_registry(registry, REGISTER_A)
    assert registry.registry == REGISTER_A

    for key, value in REGISTER_A.items():
        assert key in registry

def test_registry_len(registry):
    set_register_registry(registry, REGISTER_A)
    assert len(registry) == len(REGISTER_A)

def test_registry_eq(registry):
    set_register_registry(registry, REGISTER_A)
    registry2 = Registry("Registry2")
    set_register_registry(registry2, REGISTER_A)
    assert not registry == registry2

    base_registry = Registry()
    assert registry == base_registry #same registry name and registry content

    result = registry.__eq__("not a registry")
    assert result is NotImplemented

def test_registry_repr(registry):
    registry.register("foo", 42)
    r = repr(registry)
    assert "Registry" in r
    assert registry.registry_name in r
    assert str(len(registry)) in r
