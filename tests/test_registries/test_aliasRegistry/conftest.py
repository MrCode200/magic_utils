import pytest
from magic_utils.registries import AliasRegistry


@pytest.fixture
def alias_registry():
    """Fixture providing a fresh AliasRegistry instance for each test."""
    registry = AliasRegistry()
    yield registry
    registry.reset()