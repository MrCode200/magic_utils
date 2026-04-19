import pytest
from magic_utils.registries import AliasRegistry, Registry
import uuid

def test_alias_registry_eq_with_same_aliases_but_different_name(alias_registry):
    """Test equality of two AliasRegistry instances with same data."""
    alias_registry.register('key1', 'value1', aliases=['alias1'])

    registry2 = AliasRegistry(registry_name="OtherRegistry" + str(uuid.uuid4()))
    registry2.register('key1', 'value1', aliases=['alias1'])

    assert not (alias_registry == registry2)

def test_alias_registry_eq_with_same_aliases_same_name(alias_registry):
    alias_registry.register('key1', 'value1', aliases=['alias1'])

    registry3 = AliasRegistry(registry_name=alias_registry.registry_name)
    registry3.register('key3', 'value3', aliases=['alias3'])

    assert (alias_registry == registry3)


def test_alias_registry_eq_different_data(alias_registry):
    """Test inequality when data differs."""
    alias_registry.register('key1', 'value1', aliases=['alias1'])

    registry2 = AliasRegistry(registry_name="OtherRegistry" + str(uuid.uuid4()))
    registry2.register('key1', 'different_value', aliases=['alias1'])

    assert not (alias_registry == registry2)


def test_alias_registry_eq_with_base_registry(alias_registry):
    """Test that AliasRegistry doesn't equal base Registry even with same data."""
    alias_registry.register('key1', 'value1')

    # Create a new base registry instance (not a singleton collision)
    base_registry = Registry(registry_name="BaseRegistryForTest" + str(uuid.uuid4()))
    base_registry.register('key1', 'value1')

    # They should not be equal since one is AliasRegistry and one is Registry
    assert not (alias_registry == base_registry)


def test_alias_registry_eq_type_check(alias_registry):
    """Test that __eq__ returns NotImplemented for non-AliasRegistry."""
    result = alias_registry.__eq__("not a registry")
    assert result is NotImplemented


def test_alias_registry_repr(alias_registry):
    """Test string representation of AliasRegistry."""
    alias_registry.register('key1', 'value1', aliases=['alias1', 'alias2'])

    repr_str = repr(alias_registry)

    assert 'AliasRegistry' in repr_str
    assert 'name=' in repr_str
    assert 'items=1' in repr_str
    assert 'canonical=1' in repr_str


def test_alias_registry_repr_multiple(alias_registry):
    """Test repr with multiple items."""
    alias_registry.register('key1', 'value1', aliases=['alias1'])
    alias_registry.register('key2', 'value2', aliases=['alias2', 'alias3'])

    repr_str = repr(alias_registry)

    assert 'items=2' in repr_str
    assert 'canonical=2' in repr_str


def test_alias_registry_repr_no_aliases(alias_registry):
    """Test repr with items but no aliases."""
    alias_registry.register('key1', 'value1')
    alias_registry.register('key2', 'value2')

    repr_str = repr(alias_registry)

    assert 'items=2' in repr_str
    assert 'canonical=2' in repr_str


def test_alias_registry_len(alias_registry):
    """Test __len__ counts only canonical keys, not aliases."""
    alias_registry.register('key1', 'value1', aliases=['alias1', 'alias2'])
    alias_registry.register('key2', 'value2', aliases=['alias3'])

    # Length should be 2 (canonical keys only)
    assert len(alias_registry) == 2