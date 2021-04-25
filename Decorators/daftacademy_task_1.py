"""
[TASK 1]

Przywitajmy się na początek! Stwórz dekorator greetings, który opakowuje funkcję
zwracającą stringa zawierającego imię bądź imiona oraz nazwisko. Dekorator ma
sformatować tego stringa tak, że pierwsza litera każdego z imion oraz nazwiska ma być
pisana z dużej litery. Pozostałe litery mają być z małej. 
Ponad to, dekorator ma również dodać Hello na początek string'a.
"""

def greetings(function_to_be_decorated):
    def convert_list_to_string(lst):
        return ' '.join(lst)

    def inner(*args, **kwargs):
        *names, surname = function_to_be_decorated(*args, **kwargs).split(" ")
        all_names_string = convert_list_to_string([name.capitalize() for name in names])
        return f"Hello {all_names_string} {surname.capitalize()}"
    return inner

@greetings
def name_surname():
    return "jan sebastian bach"

print(name_surname())

assert name_surname() == "Hello Jan Sebastian Bach"