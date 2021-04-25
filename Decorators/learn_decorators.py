from varname import nameof

"""
Functions have attributes that can be created outside the function.
"""

def hello(name):
    if hello.count is not None:
        hello.count += 1
        print('hello', name, 'count: ', hello.count)
    else:
        print('hello', name)

hello.count = 0
say_hi = hello

hello('Wojtek')
say_hi('Filip')

"""
Global variables - Immutables.
"""
a = 1
b = 101

def add_something_to_a_and_b(something):
    global a
    global b
    a += something
    b += something
    print('add_something_to_a_and_b: ', a, 'id a:', id(a))
    print('add_something_to_a_and_b: ', b, 'id b:', id(b))

add_something_to_a_and_b(3)
print(f'{a=} with id {id(a)=}')
print(f'{b=} with id {id(b)=}')

"""
Integers are immutable in Python. While incrementing a, we assing the value,
but a "new" variable with the same name is created.
"""
variable = 11
print(f"Variable {nameof(variable)} with value of {variable=} with ID {id(variable)=}")
variable += 1
print(f"Variable {nameof(variable)} with value of {variable=} with ID {id(variable)=}")


"""
Global variables - Mutables.
"""
a = [1]
print(f'Mutable list {a=} with {id(a)=}')

def add_something_to_list_a(something):
    a[0] += something
    print('add_something_to_list_a:', a, 'id a:', id(a))

add_something_to_list_a(100)
print(f'Mutable list {a=} with {id(a)=}')

"""
Python Closures. Functions in functions in ... and so on.
"""
def hey_hi_hello_factory(welcome_txt='hello'):
    def greet(name):
        print('{} {}!'.format(welcome_txt, name))
    return greet

say_hello = hey_hi_hello_factory()
say_hi = hey_hi_hello_factory('hi')

# We go deeper inside function with passing arguments.
# say_hello and say_hi are the objects of function greet() created by factory.
# Closue = nested functions have access to all scope of passed arguments to externals.
say_hello('Maciek')
say_hi('Julius')


"""
Nonlocal = access to variables defied inside external funcions.
"""
def hey_hi_hello_factory_counter(welcome_txt='hello'):
    counter = 0
    def greet(name):
        nonlocal counter
        counter += 1
        print('{} {}!\tcounter: {}'.format(welcome_txt, name, counter))
    return greet

say_hi = hey_hi_hello_factory_counter('hi')
say_hello = hey_hi_hello_factory_counter('hello')

say_hello('Marcus')
say_hi('Mathias')
say_hello('Marcus v2')
say_hi('Mathias v2')
# say_hi and say_hello have indepentend scopes so independent counters


"""
DECORATORS
"""
def blocker(function_to_be_blocked):
    print(f'Blocked: {function_to_be_blocked.__name__}')

@blocker
def play_music():
    print('Plays music...')   

# play_music() -> NoneType Object is not callable!


def better_blocker(function_to_be_blocked):
    def print_blocker_msg():
        print(f"Blocked {function_to_be_blocked.__name__}")
    return print_blocker_msg

@better_blocker
def play_music():
    print('Better plays music...')

play_music() # Works, cause better_blocker_msg returns the object of print_blocker_msg function.


"""
Pre and Post decorating - functions.
Lost information about function to be decorated.
"""
def wrapper(callable_function):
    def inner():
        print(f'Runs before {callable_function.__name__}')
        val = callable_function()
        print(f'Runs after {callable_function.__name__}')
        return val
    return inner

@wrapper
def to_be_decorated():
    print('I am decorated')

to_be_decorated()

# The disadvantage = we lost an information about the name of original function.
print(to_be_decorated.__name__)



"""
Pre and Post decorating - functions.
Keeps information about function to be decorated.
"""
from functools import wraps

def wrapper_saving_original_name(callable_function):
    @wraps(callable_function)
    def inner():
        print(f'Runs before {callable_function.__name__}')
        val = callable_function()
        print(f'Runs after {callable_function.__name__}')
        return val
    return inner

@wrapper_saving_original_name
def to_be_decorated():
    print('I am decorated')

to_be_decorated()
print(to_be_decorated.__name__)

"""
Decorating functions with arguments
Use args and kwargs. 
"""
def bumelant(szybka_funkcja):
    @wraps(szybka_funkcja)
    def inner(*args, **kwargs):
        result = szybka_funkcja(*args, **kwargs)
        print("Keep your energy.")
        return result
    return inner

@bumelant
def play(music):
    print(f"Plays music {music}")

play('Jazz')


"""
Pasing arguments to decorator.
"We can solve any problem by introduction an extra level of indirection"
We have a combination of passing arguments to decoraor,
decorator of function with multiple arguments (positional *args) and *kwargs.
We have and order of invoking.
"""
def bumelant(sentence):
    print(f'Decorator is called with an argument: {sentence}')
    def real_decorator(function_to_be_decorated):
        def inner(*args, **kwargs):
            result = function_to_be_decorated(*args, **kwargs)
            print('After decorating function.')
            print(f'Invoke passed to decorator {sentence}')
            return result
        return inner
    return real_decorator


@bumelant('To it today, not tommorow.')
def play(music):
    print('Plays music {}'.format(music))

play('Jazz')

"""
Own wrapper.
"""
def my_wraps(original_function):
    def outer_wrapper(to_be_decorated):
        def wrapper(*args, **kwargs):
            return to_be_decorated(*args, **kwargs)
        wrapper.__name__ = original.__name__
        return wrapper
    return outer_wrapper

def przodownik(wolna_funkcja):
    @my_wraps(wolna_funkcja)
    def inner(*args, **kwargs):
        print('First')
        return wolna_funkcja(*args, **kwargs)
    return inner
