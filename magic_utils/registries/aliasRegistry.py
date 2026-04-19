from functools import wraps
from logging import Logger
from typing import Hashable, Optional, Any

from magic_utils.exceptions import MissingKeyError, DuplicateKeyError
from .registry import Registry


class AliasRegistry(Registry):
    def __init__(
        self,
        registry_name: str = "BaseRegistry",
        logger: Optional[Logger] = None,
    ):
        """
        An extension of the base Registry that supports aliases.

        :param registry_name: The name of the registry.
        :param logger: Optional logger instance.
        """
        super().__init__(registry_name, logger)
        self._alias_to_canonical: dict[Hashable, Hashable] = {}
        self._canonical_to_aliases: dict[Hashable, set[Hashable]] = {}

    @property
    def aliases(self) -> dict[Hashable, Hashable]:
        """Return mapping of alias -> canonical."""
        return self._alias_to_canonical

    @property
    def canonicals(self) -> dict[Hashable, set[Hashable]]:
        """Return mapping of canonical -> aliases."""
        return self._canonical_to_aliases

    def resolve_key_to_canonical(self, key: Hashable) -> Hashable:
        """Resolve a key or alias to its canonical key."""
        return self._alias_to_canonical.get(key, key)

    def resolve_value_to_canonicals(self, value: Any) -> set[Hashable]:
        """Resolve a value to its canonical keys."""
        canonicals: list[Hashable] = []
        for k, v in self._registry.items():
            if v == value:
                canonicals.append(k)
        return set(canonicals)

    def add_alias(self, key: Hashable, alias: Hashable) -> None:
        """
        Add an alias to an existing canonical key.

        :param key: A canonical key or alias.
        :param alias: The new alias.
        :raises DuplicateKeyError: If alias already exists.
        """
        canonical = self.resolve_key_to_canonical(key)

        if canonical not in self._registry:
            raise MissingKeyError(f"{self.registry_name}: `{key}` not found")

        if alias in self._registry or alias in self._alias_to_canonical:
            raise DuplicateKeyError(
                f"{self.registry_name}: Alias `{alias}` already exists"
            )

        self._alias_to_canonical[alias] = canonical
        self._canonical_to_aliases.setdefault(canonical, set()).add(alias)

    def remove_alias(self, key: Hashable, alias: Hashable) -> None:
        """
        Remove an alias from a canonical key.

        :param key: A canonical key or alias.
        :param alias: The alias to remove.
        :raises MissingKeyError: If key or alias not found.
        """
        canonical = self.resolve_key_to_canonical(key)

        if canonical not in self._registry:
            raise MissingKeyError(f"{self.registry_name}: `{key}` not found")

        if alias not in self._alias_to_canonical:
            raise MissingKeyError(f"{self.registry_name}: Alias `{alias}` not found")

        self._canonical_to_aliases.get(canonical, set()).discard(alias)
        del self._alias_to_canonical[alias]

    def register(
            self,
            canonical: Hashable,
            value: Any,
            aliases: Optional[list[Hashable]] = None,
    ) -> None:
        """
        Register a canonical key with optional aliases.

        Ensures that the canonical and all aliases are globally unique
        across both canonical keys and aliases.

        :param canonical: The primary key.
        :param value: Value to store.
        :param aliases: Optional list of aliases.
        :raises DuplicateKeyError: On duplicate canonical or alias.
        """
        aliases = aliases or []

        identifiers = set(aliases)
        identifiers.add(canonical)

        if len(identifiers) != len(aliases) + 1:
            raise DuplicateKeyError(
                f"{self.registry_name}: Duplicate values in canonical/aliases: {identifiers}"
            )

        for identifier in identifiers:
            if identifier in self._registry or identifier in self._alias_to_canonical:
                raise DuplicateKeyError(
                    f"{self.registry_name}: `{identifier}` already exists as canonical or alias"
                )

        super().register(canonical, value)
        self._canonical_to_aliases[canonical] = set(aliases)
        for alias in aliases:
            self._alias_to_canonical[alias] = canonical

    def register_function(
        self,
        key: Optional[Hashable] = None,
        aliases: Optional[list[Hashable]] = None,
    ) -> Any:
        """
        Decorator to register a function with optional aliases.

        :param key: Canonical key.
        :param aliases: Optional aliases.
        """
        has_registered = False

        def decorator(func):
            nonlocal has_registered
            if not has_registered:
                canonical = func.__name__ if key is None else key
                self.register(canonical, func, aliases)
                has_registered = True

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def register_class(
        self,
        key: Optional[Hashable] = None,
        aliases: Optional[list[Hashable]] = None,
    ) -> object:
        """
        Decorator to register a class with optional aliases.

        :param key: Canonical key.
        :param aliases: Optional aliases.
        """

        def decorator(cls):
            canonical = cls.__name__ if key is None else key
            self.register(canonical, cls, aliases)
            return cls

        return decorator

    def get(self, key: Hashable) -> Any:
        """
        Retrieve a value by key or alias.

        :param key: Canonical key or alias.
        """
        canonical = self.resolve_key_to_canonical(key)
        return super().get(canonical)

    def remove(
        self,
        key: Optional[Hashable] = None,
        value: Any = None,
        rmv_all: bool = False,
    ) -> None:
        """
        Remove an entry and all its aliases.

        :param key: Key or alias.
        :param value: Value.
        :param rmv_all: Passed to base class.
        """
        canonical = self.resolve_key_to_canonical(key) if key is not None else None

        canonicals = []
        if canonical is None:
            canonicals = self.resolve_value_to_canonicals(value)
        else:
            canonicals.append(canonical)

        super().remove(canonical, value, rmv_all)

        for c in canonicals:
            aliases = self._canonical_to_aliases.get(c, set()).copy()

            self._canonical_to_aliases.pop(c, None)
            for alias in aliases:
                self._alias_to_canonical.pop(alias, None)

    def update(self, key: Hashable, value: Any) -> None:
        """
        Update a value by key or alias.

        :param key: Canonical key or alias.
        :param value: New value.
        """
        canonical = self.resolve_key_to_canonical(key)
        super().update(canonical, value)

    def reset(self) -> None:
        """Clear registry and all aliases."""
        self._alias_to_canonical.clear()
        self._canonical_to_aliases.clear()
        super().reset()

    def __contains__(self, key):
        return key in self._registry or key in self._alias_to_canonical

    def __setitem__(self, key, value):
        canonical = self.resolve_key_to_canonical(key)
        if canonical in self._registry:
            self.update(key, value)
        else:
            self.register(key, value)

    def __eq__(self, other):
        if not isinstance(other, AliasRegistry):
            return NotImplemented
        return (
            self._registry == other._registry
            and self.registry_name == other.registry_name
            and self._canonical_to_aliases == other._canonical_to_aliases
        )

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} "
            f"name='{self.registry_name}', "
            f"items={len(self._registry)}, "
            f"canonical={len(self._canonical_to_aliases)}>"
        )