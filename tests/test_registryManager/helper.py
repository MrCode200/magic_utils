def set_register_registry(registry, to_register: dict):
    for key, value in to_register.items():
        registry.register(key, value)