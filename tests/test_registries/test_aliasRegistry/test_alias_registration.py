import pytest
from magic_utils.exceptions import DuplicateKeyError, MissingKeyError
from .constants import REGISTER_A, ALIASES_FOR_ARGINT, ALIASES_FOR_ARGSTRING

def test_alias_registry_register_with_aliases(alias_registry):
    """Test registering a key with multiple aliases."""
    alias_registry.register('argInt', 1, aliases=['int_alias', 'integer'])

    assert 'argInt' in alias_registry
    assert 'int_alias' in alias_registry
    assert 'integer' in alias_registry
    assert alias_registry.get('argInt') == 1
    assert alias_registry.get('int_alias') == 1
    assert alias_registry.get('integer') == 1


def test_alias_registry_register_without_aliases(alias_registry):
    """Test registering a key without aliases."""
    alias_registry.register('key1', 'value1')

    assert 'key1' in alias_registry
    assert alias_registry.get('key1') == 'value1'


def test_alias_registry_register_empty_aliases(alias_registry):
    """Test registering a key with empty aliases list."""
    alias_registry.register('key1', 'value1', aliases=[])

    assert 'key1' in alias_registry
    assert alias_registry.get('key1') == 'value1'


def test_alias_registry_duplicate_in_aliases(alias_registry):
    """Test that duplicate values in canonical and aliases raises error."""
    with pytest.raises(DuplicateKeyError):
        alias_registry.register('key1', 'value1', aliases=['key1', 'alias1'])


def test_alias_registry_duplicate_alias_in_list(alias_registry):
    """Test that duplicate values within aliases list raises error."""
    with pytest.raises(DuplicateKeyError):
        alias_registry.register('key1', 'value1', aliases=['alias1', 'alias1'])


def test_alias_registry_duplicate_canonical_key(alias_registry):
    """Test that registering duplicate canonical key raises error."""
    alias_registry.register('key1', 'value1', aliases=['alias1'])

    with pytest.raises(DuplicateKeyError):
        alias_registry.register('key1', 'value2')


def test_alias_registry_duplicate_as_alias(alias_registry):
    """Test that registering a canonical key that exists as alias raises error."""
    alias_registry.register('key1', 'value1', aliases=['alias1'])

    with pytest.raises(DuplicateKeyError):
        alias_registry.register('alias1', 'value2')


def test_alias_registry_duplicate_alias(alias_registry):
    """Test that registering with an alias that already exists raises error."""
    alias_registry.register('key1', 'value1', aliases=['alias1'])

    with pytest.raises(DuplicateKeyError):
        alias_registry.register('key2', 'value2', aliases=['alias1'])