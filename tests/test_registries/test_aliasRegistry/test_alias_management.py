import pytest
from magic_utils.exceptions import DuplicateKeyError, MissingKeyError
from .constants import REGISTER_A, ALIASES_FOR_ARGINT


def test_add_alias_to_canonical(alias_registry):
    """Test adding an alias to an existing canonical key."""
    alias_registry.register('argInt', 1)
    alias_registry.add_alias('argInt', 'int_alias')

    assert 'int_alias' in alias_registry
    assert alias_registry.get('int_alias') == 1


def test_add_alias_to_existing_alias(alias_registry):
    """Test adding an alias using an existing alias as the key."""
    alias_registry.register('argInt', 1, aliases=['first_alias'])
    alias_registry.add_alias('first_alias', 'second_alias')

    assert 'second_alias' in alias_registry
    assert alias_registry.get('second_alias') == 1


def test_add_duplicate_alias(alias_registry):
    """Test that adding a duplicate alias raises error."""
    alias_registry.register('argInt', 1, aliases=['alias1'])

    with pytest.raises(DuplicateKeyError):
        alias_registry.add_alias('argInt', 'alias1')


def test_add_alias_to_nonexistent_key(alias_registry):
    """Test that adding alias to non-existent key raises error."""
    with pytest.raises(MissingKeyError):
        alias_registry.add_alias('nonexistent', 'new_alias')


def test_add_alias_that_exists_as_canonical(alias_registry):
    """Test that adding alias that exists as canonical key raises error."""
    alias_registry.register('key1', 'value1')
    alias_registry.register('key2', 'value2')

    with pytest.raises(DuplicateKeyError):
        alias_registry.add_alias('key1', 'key2')


def test_remove_alias(alias_registry):
    """Test removing an alias from a canonical key."""
    alias_registry.register('argInt', 1, aliases=['alias1', 'alias2'])

    assert 'alias1' in alias_registry
    alias_registry.remove_alias('argInt', 'alias1')

    assert 'alias1' not in alias_registry
    assert 'argInt' in alias_registry
    assert 'alias2' in alias_registry


def test_remove_alias_using_alias_as_key(alias_registry):
    """Test removing an alias using another alias as the key."""
    alias_registry.register('argInt', 1, aliases=['alias1', 'alias2'])

    alias_registry.remove_alias('alias1', 'alias2')

    assert 'alias2' not in alias_registry
    assert 'alias1' in alias_registry
    assert 'argInt' in alias_registry


def test_remove_nonexistent_alias(alias_registry):
    """Test that removing non-existent alias raises error."""
    alias_registry.register('argInt', 1, aliases=['alias1'])

    with pytest.raises(MissingKeyError):
        alias_registry.remove_alias('argInt', 'nonexistent_alias')


def test_remove_alias_from_nonexistent_key(alias_registry):
    """Test that removing alias from non-existent key raises error."""
    with pytest.raises(MissingKeyError):
        alias_registry.remove_alias('nonexistent', 'alias')