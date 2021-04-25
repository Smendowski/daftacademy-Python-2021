"""
[TASK 3]

Napisz dekorator format_output, który przyjmuje argumenty pozycyjne w postaci
stringów oraz opakowuję funkcję zwracającą dict'a. Zadaniem dekoratora jest
przeformatowanie dict'a pozostawiając tylko kluczę z argumentów dekoratora i
odpowiadające im wartości. Uwaga! Jednakże niektóre klucze w argumentach dekoratora
są dosyć nietypowe, gdyż mogą składać się z kilku pojedynczych kluczy. Wtedy takie
klucze są połączone podwójną podłogą __, wartością nowo utworzonego klucza będą
wartośi kluczy składowych połączone pojedynczą spacją. W przypadku podania
nieistniejącego klucza lub klucza źle zdefiniowanego, dekorator ma rzucić wyjątkiem ValueError.
"""
import pytest 


def format_output(*keys):
    def inner(wrapped):
        def wrapper(*args, **kwargs):
            wrapped_dict = wrapped(*args, **kwargs)
            wd_keys = wrapped_dict.keys()

            new_dict = {}
            for key in keys:
                if key not in wrapped_dict.keys():
                    if '__' not in key:
                        raise ValueError
                    else:
                        multiple_keys = key.split('__')
                        for mkey in multiple_keys:
                            if mkey not in wd_keys:
                                raise ValueError
                        new_dict[key] = ' '.join([wrapped_dict[mkey] for mkey in multiple_keys])
                else:
                    new_dict[key] = wrapped_dict[key]

            return new_dict
        return wrapper
    return inner


# Positional Arguments (*args) test 
args = ("first_name__last_name", "city")
print(args)
print(*args)

@format_output("first_name__last_name", "city")
def first_func():
    return {
        "first_name": "Jan",
        "last_name": "Kowalski",
        "city": "Warszawa",
    }

@format_output("first_name", "age")
def second_func():
    return {
        "first_name": "Jan",
        "last_name": "Kowalski",
        "city": "Warszawa",
    }

assert first_func() == {"first_name__last_name": "Jan Kowalski", "city": "Warszawa"}

with pytest.raises(ValueError):
    second_func()