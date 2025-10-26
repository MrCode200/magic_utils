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
        raise_exception: bool = True,
    ):
        """
        A generic base registry for storing and managing objects by key.

        :param registry_name: The name of the registry. If not provided, will use "BaseRegistry".
        Registered instances are stored in a class variable `_instances`.
        :param logger: The logger instance to use for logging. If None, won't log.
        :param raise_exception: Whether to raise exceptions on errors.
        """
        if getattr(self, '_initialized', False):
            return

        self._registry: Dict[Hashable, Any] = {}
        self._initialized = True

        self.registry_name: str = registry_name
        self.logger = logger
        self.raise_exception: bool = raise_exception

    @property
    def registry(self) -> Dict[Hashable, Any]:
        """
        Access the underlying registry.

        :return: The dictionary containing all registered items.
        :rtype: Dict[Hashable, Any]
        """
        return self._registry

    def register(self, keys: Union[Hashable, list[Hashable]], value: Any) -> None:
        """
        Register one or more keys with a specified value.
        Skips registration if a key is already registered completely.

        :param keys: A single key or a list of keys(aliases) to register.
        :param value: The value to associate with the given key(s).
        :raises DuplicateError: If a key is already registered and exceptions are enabled.
        """
        if not isinstance(keys, list):
            keys = [keys]

        for key in keys:
            if key in self._registry:
                self.logger.debug(f"{self.registry_name}: `{key}` already registered.") if self.logger else None

                if self.raise_exception:
                    raise DuplicateKeyError(
                        f"{self.registry_name}: `{key}` already registered.",
                        registry_name=self.registry_name,
                        duplicate_item=key,
                    )
                return

        for key in keys:
            self._registry[key] = value
            self.logger.debug(f"{self.registry_name}: Registered `{key}` to registry") if self.logger else None

    def register_function(self, keys: Union[Hashable, list[Hashable]]) -> Any:
        """
        A decorator to register a function itself to the registry.
        This registration happens only once when the function is first defined.

        :param keys: A single key or a list of keys(aliases) to register the function with.
        :return: The decorated function.
        """
        has_registered: bool = False

        def decorator(func):
            nonlocal has_registered
            if not has_registered:
                k = func.__name__ if not keys else keys
                self.register(k, func)
                has_registered = True

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def register_class(self, keys: Union[Hashable, list[Hashable]]) -> Union[None, object]:
        """
        A decorator to register a class to the registry.

        :param keys: A single key or a list of keys(aliases) to register the class with.
        :return: The decorated class.
        """
        def decorator(cls):
            k = cls.__name__ if not keys else keys
            self.register(k, cls)
            return cls
        return decorator

    def get(
        self, key: Union[Hashable, None] = None
    ) -> Union[Dict[Hashable, Any], Any, None]:
        """
        Retrieve an item from the registry.

        :param key: The key to retrieve.
        :return: The value associated with the key, or the entire registry if `key` is `None`.
        :raises NotRegisteredError: If the key is not registered and exceptions are enabled.
        """
        if key not in self._registry:
            self.logger.warning(f"{self.registry_name}: `{key}` not registered.") if self.logger else None

            if self.raise_exception:
                raise MissingKeyError(
                    f"{self.registry_name}: `{key}` not registered.",
                    registry_name=self.registry_name,
                    missing_key=key,
                )
            return

        return self._registry[key]

    def remove(self, key: Union[Hashable, None] = None, value: Any = None, all: bool = False) -> None:
        """
        Remove an item from the registry by key or value.

        :param key: The key to remove. If `None`, removal is based on the value.
        :param value: The value to remove. If `None`, removal is based on the key.
        :param all: Whether to remove all matches. If `True`, removes all matches. Only needed if removed by value.
        :raises ValueError: If both `key` and `value` are `None`.
        :raises NotRegisteredError: If the key or value is not found and exceptions are enabled.
        """
        if key is None and value is None:
            raise ValueError("Either key or value must be provided.")
        elif key is not None and value is not None:
            raise ValueError("Only key or value can be provided.")

        if value is None:
            if key not in self._registry:
                self.logger.warning(f"{self.registry_name}: `{key}` not registered.") if self.logger else None

                if self.raise_exception:
                    raise MissingKeyError(
                        f"{self.registry_name}: `{key}` not registered.",
                        registry_name=self.registry_name,
                        missing_key=key,
                    )
                return

            del self._registry[key]

            self.logger.debug(f"{self.registry_name}: Removed `{key}` from registry") if self.logger else None

        else:
            for k, v in list(self._registry.items()):
                if v == value:
                    del self._registry[k]
                    self.logger.debug(f"{self.registry_name}: Removed `{k}` from registry") if self.logger else None

                    return

            self.logger.warning(f"{self.registry_name}: No key with value: `{value}` registered.") if self.logger else None


            if self.raise_exception:
                raise MissingKeyError(
                    f"{self.registry_name}: No key with value: `{value}` registered.",
                    registry_name=self.registry_name,
                    missing_key=value,
                )

    def update(self, key: Hashable, value: Any) -> None:
        """
        Update an item in the registry.

        :param key: The key to remove. If `None`, removal is based on the value.
        :param value: The value to remove. If `None`, removal is based on the key.
        """
        if key not in self._registry:
            self.logger.warning(f"{self.registry_name}: `{key}` not registered.") if self.logger else None

            if self.raise_exception:
                raise MissingKeyError(
                    f"{self.registry_name}: `{key}` not registered.",
                    registry_name=self.registry_name,
                    missing_key=key,
                )
            return

        self._registry[key] = value
        self.logger.debug(f"{self.registry_name}: Updated `{key}` with value `{value}` in registry") if self.logger else None

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
