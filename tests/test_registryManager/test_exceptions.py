import pytest

from magic_utils.exceptions import MissingKeyError, DuplicateKeyError
from .helper import set_register_registry
from .constants import REGISTER_A


def test_registry_raise_exception_false(registry):
    registry.raise_exception = False

    registry.register('ExistingKey', 1)
    assert registry.register('ExistingKey', 2) is None
    assert registry.remove(key='nonExistingKey') is None
    registry.update('nonExistingKey', 2)
    registry.get('nonExistingKey')
    assert registry["nonExistingKey"] is None

    registry.raise_exception = True

def test_duplicate_key_error_str():
    """Test the __str__ method of DuplicateKeyError."""
    # Test with custom message
    error = DuplicateKeyError("Custom error message", "TestRegistry", "test_key")
    assert str(error) == "Custom error message"
    
    # Test with default message
    error = DuplicateKeyError(None, "TestRegistry", "test_key")
    assert str(error) == "TestRegistry: Duplicate item = test_key"

def test_registry_duplicate_key_exception(registry):
    set_register_registry(registry, REGISTER_A)

    def check_exception_metadata(e):
        assert e.value.registry_name == registry.registry_name
        assert e.value.duplicate_item == 'argInt'
        assert e.value.message == f"{registry.registry_name}: `argInt` already registered."
        assert str(e.value) == e.value.message  # Test __str__ method

    with pytest.raises(DuplicateKeyError) as e:
        registry.register('argInt', 2)
    check_exception_metadata(e)

    with pytest.raises(DuplicateKeyError) as e:
        registry.register(['newKey', 'argInt'], 2)
    check_exception_metadata(e)

    assert registry['argInt'] == 1
    with pytest.raises(MissingKeyError, match="BaseRegistry: `newKey` not registered."):
        assert registry['newKey'] == 2

def test_registry_missing_key_exception(registry):
    def check_exception_metadata(e):
        assert e.value.registry_name == registry.registry_name
        assert e.value.missing_key == 'nonExistingKey'
        assert e.value.message == f"{registry.registry_name}: `nonExistingKey` not registered."
        assert str(e.value) == e.value.message  # Test __str__ method for consistency

    with pytest.raises(MissingKeyError) as e:
        registry.get('nonExistingKey')
    check_exception_metadata(e)

    with pytest.raises(MissingKeyError) as e:
        registry.update('nonExistingKey', 1)
    check_exception_metadata(e)

    with pytest.raises(MissingKeyError) as e:
        registry.remove(value='nonExistingKey')
    assert e.value.registry_name == registry.registry_name
    assert e.value.missing_key == 'nonExistingKey'
    assert e.value.message == f"{registry.registry_name}: No key with value: `nonExistingKey` registered."

    with pytest.raises(MissingKeyError) as e:
        registry.remove(key='nonExistingKey')
    check_exception_metadata(e)