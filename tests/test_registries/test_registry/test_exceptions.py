import pytest

from magic_utils.exceptions import MissingKeyError, DuplicateKeyError
from .constants import REGISTER_A
from .helper import set_register_registry


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

    assert registry['argInt'] == 2
    with pytest.raises(MissingKeyError, match="BaseRegistry: `newKey` not registered."):
        assert registry['newKey'] == 3


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


def test_rmv_with_mutliple_same_values(registry):
    set_register_registry(registry, REGISTER_A)
    registry.register('argInt2', 2)
    registry.register('argInt3', 2)

    with pytest.raises(ValueError) as e:
        registry.remove(value=2, rmv_all=False)

    assert str(e.value) == f"{registry.registry_name}: Multiple keys with value: `2` registered (set rmv_all=True to remove all)."

    registry.remove(value=2, rmv_all=True)
    assert len([k for k, v in registry.registry.items() if v == 2]) == 0
