import pytest

from .constants import REGISTER_A
from .helper import set_register_registry

def test_registry_register(registry):
    registry.register('argInt', 1)
    registry["argString"] = "argString"
    assert registry.registry == {'argInt': 1, 'argString': 'argString'}

def test_registry_register_class(registry):
    @registry.register_class('test')
    class Test:
        value: int = 1

    assert registry['test'] == Test

def test_registry_register_function(registry):
    @registry.register_function('test')
    def test():
        return 1

    assert registry.get('test')() == test()

def test_registry_get(registry):
    set_register_registry(registry, REGISTER_A)
    assert registry.get('argInt') == 2
    assert registry['argString'] == "string"
    assert registry.get('argBool') == True

def test_registry_update(registry):
    set_register_registry(registry, REGISTER_A)

    assert registry.get('argInt') == 2
    assert registry['argBool'] == True

    registry.update('argInt', 3)
    registry['argBool'] = False

    assert registry.get('argInt') == 3
    assert registry.get('argBool') == False

def test_registry_remove(registry):
    set_register_registry(registry, REGISTER_A)

    # By Value
    registry.remove(value=2) # argInt

    # By Key
    del registry['argString']

    assert 'argInt' not in registry
    assert 'argString' not in registry.registry
    assert 'argBool' in registry

    with pytest.raises(ValueError, match='Either key or value must be provided.'):
        registry.remove(None)

    with pytest.raises(ValueError, match='Only key or value can be provided.'):
        registry.remove(key='argInt', value=1)
