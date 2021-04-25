"""
[TASK 2]

Łapał za kran, a kanarka złapał - sensu trochę brak w tym zdaniu, ale ma za ta znaną wszystkim właściwość.
Otóż jest palindromem. Kolejne zadanie to stworzenie dekoratora is_palindrome, 
opakowującego funkcję zwracającego stringa. Zadaniem tego dekoratora jest doklejenie
do wartości zwróconej przez funkcję - is palindrome lub - is not palindrome w zależności
czy to co zwróciła funkcja jest palindromem czy też nie.
Przy określaniu czy dane słowo/zdanie jest palindromem bierzemy pod uwagę tylko litery oraz cyfry.
Resztę pomijamy.
"""

def is_palindrome(function_to_be_decorated):
    import re
    def inner(*args):
        sentence = function_to_be_decorated(*args)
        pattern = '[a-zA-Z0-9]+'
        matches = re.finditer(pattern, sentence)
        alphanumeric_sentence = ""
        for match in matches:
            alphanumeric_sentence += match.group(0)
        if alphanumeric_sentence.lower() != alphanumeric_sentence[::-1].lower():
            return f"{sentence} - is not palindrome"
        return f"{sentence} - is palindrome"
    return inner


@is_palindrome
def sentence():
    return "Eva, can I see bees in a cave?"

assert sentence() == "Eva, can I see bees in a cave? - is palindrome"
