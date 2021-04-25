"""
[TASK 4]

Stwórz dwa dekoratory add_class_method oraz add_instance_method
które przyjmują w parametrze klasę. Zadaniem dekoratora będzie
opakować funkcję w ten sposób, że dana funkcja stanie się metodą
zadanej klasy lub metodą jej instancji.
Zwróć szczególną uwagę na przykłady poniżej.
"""
from functools import wraps
  
def add_instance_method(cls):   
    def decorator(function_to_be_added):
        def wrapper(self, *args, **kwargs):
            return function_to_be_added(*args, **kwargs)
        setattr(cls, function_to_be_added.__name__, wrapper)
        return function_to_be_added
    return decorator

def add_class_method(cls):    
    def decorator(function_to_be_added):
        setattr(cls, function_to_be_added.__name__, function_to_be_added)
        return function_to_be_added
    return decorator

class A:
    pass

@add_class_method(A)
def foo():
    return "Hello!"

@add_instance_method(A)
def bar():
    return "Hello again!"

assert A.foo() == "Hello!"
assert A().bar() == "Hello again!"



# In one decorator:
def for_all_methods(decorator):

    def decorate(cls):

        for attr in dir(cls):
            possible_method = getattr(cls, attr)
            if not callable(possible_method):
                continue

            # staticmethod
            if not hasattr(possible_method, "__self__"):
                raw_function = cls.__dict__[attr].__func__
                decorated_method = decorator(raw_function)
                decorated_method = staticmethod(decorated_method)

            # classmethod
            elif type(possible_method.__self__) == type:
                raw_function = cls.__dict__[attr].__func__
                decorated_method = decorator(raw_function)
                decorated_method = classmethod(decorated_method)

            # instance method
            elif possible_method.__self__ is None:
                decorated_method = decorator(possible_method)

            setattr(cls, attr, decorated_method)

        return cls
    return decorate
