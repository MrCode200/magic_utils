"""Magic Utils - A collection of useful utility classes and functions."""

__title__ = "magic_utils"
__version__ = "0.2.0"
__author__ = "MrCode200"
__license__ = "MIT"

from .eventManager import EventManager
from .registryManager import Registry
from .magicLogger import setup_logger

__all__ = ["EventManager", "Registry", "setup_logger"]