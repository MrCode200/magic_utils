import pytest
from magic_utils.registries import AliasRegistry


@pytest.fixture
def alias_registry():
    """Fixture providing a fresh AliasRegistry instance for each test."""
    import uuid
    # Use unique registry names to avoid singleton collisions
    registry = AliasRegistry(registry_name=f"TestRegistry-{uuid.uuid4()}")
    yield registry
    registry.reset()