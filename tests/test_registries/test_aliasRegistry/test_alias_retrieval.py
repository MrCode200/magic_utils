import pytest
from .constants import REGISTER_A, ALIASES_FOR_ARGINT

def test_resolve_key_to_canonical(alias_registry):
    """Test resolving alias to canonical key."""
    alias_registry.register('argInt', 1, aliases=['int_alias'])

    assert alias_registry.resolve_key_to_canonical('argInt') == 'argInt'
    assert alias_registry.resolve_key_to_canonical('int_alias') == 'argInt'


def test_resolve_nonexistent_key(alias_registry):
    """Test resolving non-existent key returns the key itself."""
    result = alias_registry.resolve_key_to_canonical('nonexistent')
    assert result == 'nonexistent'


def test_get_by_canonical_key(alias_registry):
    """Test retrieving value using canonical key."""
    alias_registry.register('argInt', 1, aliases=['int_alias'])
    assert alias_registry.get('argInt') == 1


def test_get_by_alias(alias_registry):
    """Test retrieving value using alias."""
    alias_registry.register('argInt', 1, aliases=['int_alias', 'integer'])

    assert alias_registry.get('int_alias') == 1
    assert alias_registry.get('integer') == 1


def test_getitem_by_canonical(alias_registry):
    """Test __getitem__ with canonical key."""
    alias_registry.register('argInt', 1, aliases=['int_alias'])
    assert alias_registry['argInt'] == 1


def test_getitem_by_alias(alias_registry):
    """Test __getitem__ with alias."""
    alias_registry.register('argInt', 1, aliases=['int_alias'])
    assert alias_registry['int_alias'] == 1


def test_aliases_property(alias_registry):
    """Test aliases property returns correct mapping."""
    alias_registry.register('key1', 'value1', aliases=['alias1', 'alias2'])
    alias_registry.register('key2', 'value2')

    aliases = alias_registry.aliases
    assert aliases == {'alias1': 'key1', 'alias2': 'key1'}


def test_canonicals_property(alias_registry):
    """Test canonicals property returns correct mapping."""
    alias_registry.register('key1', 'value1', aliases=['alias1', 'alias2'])
    alias_registry.register('key2', 'value2')

    canonicals = alias_registry.canonicals
    assert canonicals == {'key1': {'alias1', 'alias2'}, 'key2': set()}