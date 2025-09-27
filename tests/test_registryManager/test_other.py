import pytest

from magic_utils.registryManager import Registry
from .helper import set_register_registry
from .constants import REGISTER_A


@pytest.fixture
def registry():
    registry = Registry()
    yield registry
    registry.reset()

def test_registry_reset(registry):
    set_register_registry(registry, REGISTER_A)
    assert registry.registry != {}
    registry.reset()
    assert registry.registry == {}

def test_registry_singleton(registry):
    registrySame = Registry()
    assert registry == registrySame

    registrySame.register('argInt', 2)
    assert registry.get('argInt') == 2
    assert registrySame.get('argInt') == 2

    del registry['argInt']
    assert 'argInt' not in registry
    assert 'argInt' not in registrySame

    registryDifferentName = Registry("RegistryDifferentName")
    assert registryDifferentName != registry
    registryDifferentName.reset()

def test_registry_alias(registry):
    registry.register(['argBool', 'argBoolAlias'], True)
    assert registry.get('argBool') == True
    assert registry.get('argBoolAlias') == True
