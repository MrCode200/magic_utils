import pytest
from magic_utils.exceptions import DuplicateKeyError


def test_register_function_with_aliases(alias_registry):
    """Test registering a function with aliases."""

    @alias_registry.register_function(key='my_func', aliases=['func_alias', 'alias_func'])
    def my_function():
        return 42

    assert 'my_func' in alias_registry
    assert 'func_alias' in alias_registry
    assert 'alias_func' in alias_registry

    assert alias_registry.get('my_func')() == 42
    assert alias_registry.get('func_alias')() == 42


def test_register_function_default_key_with_aliases(alias_registry):
    """Test registering function with function name as key and aliases."""

    @alias_registry.register_function(aliases=['test_alias'])
    def test_func():
        return "test"

    assert 'test_func' in alias_registry
    assert 'test_alias' in alias_registry
    assert alias_registry.get('test_func')() == "test"
    assert alias_registry.get('test_alias')() == "test"


def test_register_function_no_key_or_aliases(alias_registry):
    """Test registering function with only function name."""

    @alias_registry.register_function()
    def simple_func():
        return "simple"

    assert 'simple_func' in alias_registry
    assert alias_registry.get('simple_func')() == "simple"


def test_register_class_with_aliases(alias_registry):
    """Test registering a class with aliases."""

    @alias_registry.register_class(key='MyClass', aliases=['my_class', 'class_alias'])
    class MyClass:
        value = 42

    assert 'MyClass' in alias_registry
    assert 'my_class' in alias_registry
    assert 'class_alias' in alias_registry

    assert alias_registry.get('MyClass') is MyClass
    assert alias_registry.get('my_class') is MyClass


def test_register_class_default_key_with_aliases(alias_registry):
    """Test registering class with class name as key and aliases."""

    @alias_registry.register_class(aliases=['test_alias'])
    class TestClass:
        pass

    assert 'TestClass' in alias_registry
    assert 'test_alias' in alias_registry
    assert alias_registry.get('TestClass') is TestClass
    assert alias_registry.get('test_alias') is TestClass


def test_register_function_duplicate_alias(alias_registry):
    """Test that registering function with duplicate alias raises error."""

    @alias_registry.register_function(key='func1', aliases=['common'])
    def func1():
        return 1

    with pytest.raises(DuplicateKeyError):
        @alias_registry.register_function(key='func2', aliases=['common'])
        def func2():
            return 2


def test_register_class_duplicate_alias(alias_registry):
    """Test that registering class with duplicate alias raises error."""

    @alias_registry.register_class(key='Class1', aliases=['common'])
    class Class1:
        pass

    with pytest.raises(DuplicateKeyError):
        @alias_registry.register_class(key='Class2', aliases=['common'])
        class Class2:
            pass