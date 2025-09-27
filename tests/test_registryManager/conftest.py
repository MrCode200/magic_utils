import pytest

from magic_utils.registryManager import Registry

@pytest.fixture
def registry():
    registry = Registry()
    yield registry
    registry.reset()