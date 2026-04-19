import pytest

from magic_utils.registries import Registry

@pytest.fixture
def registry():
    registry = Registry()
    yield registry
    registry.reset()