from functools import wraps
from logging import Logger
from typing import Any, Dict, Hashable, Union, Optional

from magic_utils.exceptions import DuplicateKeyError, MissingKeyError


# fmt: off
# TODO: on rmv or update, respect aliases
class Registry:
    _instances: Dict[str, "Registry"] = {}

    def __new__(cls, registry_name: str = "BaseRegistry", *args, **kwargs):
        if registry_name in cls._instances:
            return cls._instances[registry_name]
        instance = super().__new__(cls)
        cls._instances[registry_name] = instance
        return instance

    def __init__(
            self,
            registry_name: str = "BaseRegistry",
            logger: Optional[Logger] = None,
    ):
        """
        A generic base registry for storing and managing objects by key.

        :param registry_name: The name of the registry. If not provided, will use "BaseRegistry".
        Registered instances are stored in a class variable `_instances`.
        :param logger: The logger instance to use for logging. If None, won't log.
        """
        if getattr(self, '_initialized', False):
            return

        self._registry: Dict[Hashable, Any] = {}
        self._initialized = True

        self.registry_name: str = registry_name
        self.logger = logger

    @property
    def registry(self) -> Dict[Hashable, Any]:
        """
        Access the underlying registry.

        :return: The dictionary containing all registered items.
        :rtype: Dict[Hashable, Any]
        """
        return self._registry

    def register(self, key: Hashable, value: Any) -> None:
        """
        Register one key with a specified value.
        Skips registration if a key is already registered completely.

        :param key: A hashable key to register.
        :param value: The value to associate with the given key.
        :raises DuplicateError: If a key is already registered and exceptions are enabled.
        """
        if key in self._registry:
            self.logger.debug(f"{self.registry_name}: `{key}` already registered.") if self.logger else None

            raise DuplicateKeyError(
                f"{self.registry_name}: `{key}` already registered.",
                registry_name=self.registry_name,
                duplicate_item=key,
            )

        self._registry[key] = value
        self.logger.debug(f"{self.registry_name}: Registered `{key}` to registry") if self.logger else None

    def register_function(self, key: Optional[Hashable] = None) -> Any:
        """
        A decorator to register a function itself to the registry.
        This registration happens only once when the function is first defined.

        :param key: A single key to register the function with.
        :return: The decorated function.
        """
        has_registered: bool = False

        def decorator(func):
            nonlocal has_registered
            if not has_registered:
                k = func.__name__ if key is None else key
                self.register(k, func)
                has_registered = True

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def register_class(self, key: Optional[Hashable] = None):
        """
        A decorator to register a class to the registry.

        :param key: The key to register the class with.
        :return: The decorated class.
        """

        def decorator(cls):
            k = cls.__name__ if key is None else key
            self.register(k, cls)
            return cls

        return decorator

    def get(
            self, key: Hashable
    ) -> Union[Any, None]:
        """
        Retrieve an item from the registry.

        :param key: The key to retrieve.
        :return: The value associated with the key.
        :raises NotRegisteredError: If the key is not registered and exceptions are enabled.
        """
        if key not in self._registry:
            self.logger.warning(f"{self.registry_name}: `{key}` not registered.") if self.logger else None

            raise MissingKeyError(
                f"{self.registry_name}: `{key}` not registered.",
                registry_name=self.registry_name,
                missing_key=key,
            )

        return self._registry[key]

    def remove(self, key: Union[Hashable, None] = None, value: Any = None, rmv_all: bool = False) -> None:
        """
        Remove an item from the registry by key or value.

        :param key: The key to remove. If `None`, removal is based on the value.
        :param value: The value to remove. If `None`, removal is based on the key.
        :param rmv_all: Whether to remove all matches. If `True`, removes all matches. Only needed if removed by value.
        Else raises error if multiple matches are found.
        :raises ValueError: If both `key` and `value` are passed or `None`.
        :raises NotRegisteredError: If the key or value is not found and exceptions are enabled.
        """
        if key is None and value is None:
            raise ValueError("Either key or value must be provided.")
        elif key is not None and value is not None:
            raise ValueError("Only key or value can be provided.")

        if value is None:
            if key not in self._registry:
                self.logger.warning(f"{self.registry_name}: `{key}` not registered.") if self.logger else None

                raise MissingKeyError(
                    f"{self.registry_name}: `{key}` not registered.",
                    registry_name=self.registry_name,
                    missing_key=key,
                )

            value = self._registry[key]
            del self._registry[key]

            self.logger.debug(f"{self.registry_name}: Removed `{key}: {value}` from registry") if self.logger else None

        else:
            keys_to_rmv = [k for k, v in self._registry.items() if v == value]

            if not rmv_all and len(keys_to_rmv) > 1:
                raise ValueError(f"{self.registry_name}: Multiple keys with value: `{value}` registered (set rmv_all=True to remove all).")
            elif len(keys_to_rmv) == 0:
                self.logger.warning(
                    f"{self.registry_name}: No key with value: `{value}` registered.") if self.logger else None
                raise MissingKeyError(
                    f"{self.registry_name}: No key with value: `{value}` registered.",
                    registry_name=self.registry_name,
                    missing_key=value,
                )

            for k in keys_to_rmv:
                del self._registry[k]
                self.logger.debug(f"{self.registry_name}: Removed `{k}: {value}` from registry") if self.logger else None

    def update(self, key: Hashable, value: Any) -> None:
        """
        Update an item in the registry.

        :param key: The key to update. If `None`, removal is based on the value.
        :param value: The value to update to.
        """
        if key not in self._registry:
            self.logger.warning(f"{self.registry_name}: `{key}` not registered.") if self.logger else None

            raise MissingKeyError(
                f"{self.registry_name}: `{key}` not registered.",
                registry_name=self.registry_name,
                missing_key=key,
            )

        self._registry[key] = value
        self.logger.debug(
            f"{self.registry_name}: Updated `{key}` with value `{value}` in registry") if self.logger else None

    def reset(self) -> None:
        """
        Clear all items from the registry.

        :return: None
        """
        self._registry.clear()
        self.logger.debug(f"{self.registry_name}: Reset registry") if self.logger else None

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        if key in self._registry:
            self.update(key, value)
        else:
            self.register(key, value)

    def __delitem__(self, key):
        self.remove(key)

    def __len__(self):
        return len(self._registry)

    def __contains__(self, key):
        return key in self._registry

    def __eq__(self, other):
        if not isinstance(other, Registry):
            return NotImplemented
        return (self._registry == other._registry) and (self.registry_name == other.registry_name)

    def __repr__(self):
        return f"<{self.__class__.__name__} name='{self.registry_name}', items={len(self._registry)}>"
