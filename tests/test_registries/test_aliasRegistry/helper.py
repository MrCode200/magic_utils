def set_register_alias_registry(registry, to_register: dict, aliases_dict: dict = None):
    """Helper to register items with optional aliases."""
    for key, value in to_register.items():
        alias_list = aliases_dict.get(key, []) if aliases_dict else None
        registry.register(key, value, aliases=alias_list)