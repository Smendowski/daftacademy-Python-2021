import re

search = re.compile(r'[^\W\d]', re.UNICODE)

def calculate_day_offset(*args, **kwargs):
    length = 0
    for name in args:
        length += len(search.findall(name))

    return length
    