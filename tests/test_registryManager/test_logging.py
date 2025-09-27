import logging
import pytest

from magic_utils.registryManager import Registry
from magic_utils.exceptions import MissingKeyError, DuplicateKeyError
from .helper import set_register_registry
from .constants import REGISTER_A


@pytest.fixture(autouse=True)
def reset_registry():
    """Ensure each test starts with a clean registry state."""
    Registry._instances.clear()
    yield
    Registry._instances.clear()


@pytest.fixture
def registry():
    """Create a fresh registry instance for each test."""
    """Create a fresh logger for each test."""
    logger = logging.getLogger(f"test_registry_{id('test')}")
    logger.setLevel(logging.DEBUG)

    # Remove all handlers to avoid duplicate logs
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Ensure logs propagate to the root logger where caplog can capture them
    logger.propagate = True

    return Registry(logger=logger)


def test_registry_logging_register(registry, caplog):
    # Test successful registration
    with caplog.at_level(logging.DEBUG, logger=registry.logger.name):
        registry.register('argInt', 1)
        assert f"{registry.registry_name}: Registered `argInt` to registry" in caplog.text
    
    caplog.clear()
    
    # Test duplicate registration
    with caplog.at_level(logging.DEBUG, logger=registry.logger.name):
        with pytest.raises(DuplicateKeyError):
            registry.register('argInt', 2)
        assert f"{registry.registry_name}: `argInt` already registered." in caplog.text


def test_registry_logging_update(registry, caplog):
    set_register_registry(registry, REGISTER_A)
    
    with caplog.at_level(logging.DEBUG, logger=registry.logger.name):
        registry.update('argInt', 2)
        assert f"{registry.registry_name}: Updated `argInt` with value `2` in registry" in caplog.text


def test_registry_logging_remove(registry, caplog):
    set_register_registry(registry, REGISTER_A)
    
    # Test remove by key
    with caplog.at_level(logging.DEBUG, logger=registry.logger.name):
        registry.remove('argInt')
        assert f"{registry.registry_name}: Removed `argInt` from registry" in caplog.text
    
    caplog.clear()
    
    # Test remove non-existent key
    with caplog.at_level(logging.DEBUG, logger=registry.logger.name):
        with pytest.raises(MissingKeyError):
            registry.remove('notExistingKey')
        assert f"{registry.registry_name}: `notExistingKey` not registered." in caplog.text
    
    caplog.clear()
    
    # Test remove by value
    with caplog.at_level(logging.DEBUG, logger=registry.logger.name):
        registry.remove(value='string')
        assert f"{registry.registry_name}: Removed `argString` from registry" in caplog.text
    
    caplog.clear()
    
    # Test remove non-existent value
    with caplog.at_level(logging.DEBUG, logger=registry.logger.name):
        with pytest.raises(MissingKeyError):
            registry.remove(value='notExistingKey')
        assert "No key with value: `notExistingKey` registered." in caplog.text


def test_registry_logging_get(registry, caplog):
    with caplog.at_level(logging.DEBUG, logger=registry.logger.name):
        with pytest.raises(MissingKeyError):
            registry.get('notExistingKey')
        assert f"{registry.registry_name}: `notExistingKey` not registered." in caplog.text