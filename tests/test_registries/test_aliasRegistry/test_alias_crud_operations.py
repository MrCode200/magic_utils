import pytest
from magic_utils.exceptions import MissingKeyError
from .constants import REGISTER_A


def test_update_by_canonical_key(alias_registry):
    """Test updating value by canonical key."""
    alias_registry.register('argInt', 1, aliases=['int_alias'])
    alias_registry.update('argInt', 2)

    assert alias_registry.get('argInt') == 2
    assert alias_registry.get('int_alias') == 2


def test_update_by_alias(alias_registry):
    """Test updating value by alias."""
    alias_registry.register('argInt', 1, aliases=['int_alias'])
    alias_registry.update('int_alias', 5)

    assert alias_registry.get('argInt') == 5
    assert alias_registry.get('int_alias') == 5


def test_update_nonexistent_key(alias_registry):
    """Test that updating non-existent key raises error."""
    with pytest.raises(MissingKeyError):
        alias_registry.update('nonexistent', 'value')


def test_remove_by_canonical_removes_aliases(alias_registry):
    """Test that removing canonical key also removes all aliases."""
    alias_registry.register('argInt', 1, aliases=['int_alias', 'integer'])

    alias_registry.remove('argInt')

    assert 'argInt' not in alias_registry
    assert 'int_alias' not in alias_registry
    assert 'integer' not in alias_registry


def test_remove_by_alias_removes_all(alias_registry):
    """Test that removing by alias removes canonical and all aliases."""
    alias_registry.register('argInt', 1, aliases=['int_alias', 'integer'])

    alias_registry.remove('int_alias')

    assert 'argInt' not in alias_registry
    assert 'int_alias' not in alias_registry
    assert 'integer' not in alias_registry


def test_remove_by_value_with_aliases(alias_registry):
    """Test removing by value when aliases exist."""
    alias_registry.register('argInt', 1, aliases=['int_alias'])

    alias_registry.remove(value=1)

    assert 'argInt' not in alias_registry
    assert 'int_alias' not in alias_registry


def test_setitem_registers_new_key(alias_registry):
    """Test __setitem__ registers new key."""
    alias_registry['newKey'] = 'newValue'

    assert 'newKey' in alias_registry
    assert alias_registry.get('newKey') == 'newValue'


def test_setitem_updates_existing_key(alias_registry):
    """Test __setitem__ updates existing key without registering."""
    alias_registry.register('argInt', 1, aliases=['int_alias'])

    # Should update, not try to register
    alias_registry['argInt'] = 2

    assert alias_registry.get('argInt') == 2
    assert alias_registry.get('int_alias') == 2


def test_setitem_via_alias_updates_value(alias_registry):
    """Test __setitem__ using alias updates the value."""
    alias_registry.register('argInt', 1, aliases=['int_alias'])

    # Update via alias
    alias_registry['int_alias'] = 5

    assert alias_registry.get('argInt') == 5
    assert alias_registry.get('int_alias') == 5


def test_contains_with_canonical(alias_registry):
    """Test __contains__ with canonical key."""
    alias_registry.register('argInt', 1, aliases=['int_alias'])
    assert 'argInt' in alias_registry


def test_contains_with_alias(alias_registry):
    """Test __contains__ with alias."""
    alias_registry.register('argInt', 1, aliases=['int_alias'])
    assert 'int_alias' in alias_registry


def test_reset_clears_aliases(alias_registry):
    """Test that reset clears both registry and aliases."""
    alias_registry.register('key1', 'value1', aliases=['alias1'])
    alias_registry.register('key2', 'value2')

    alias_registry.reset()

    assert len(alias_registry) == 0
    assert len(alias_registry.aliases) == 0
    assert len(alias_registry.canonicals) == 0