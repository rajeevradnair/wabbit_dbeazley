# r4.py

def count_occurrences(x, items):
    if not items:
        return 0
    elif isinstance(items[0], list):
        return count_occurrences(x, items[0]) + count_occurrences(x, items[1:])
    else:
        return int(items[0] == x) + count_occurrences(x, items[1:])

assert count_occurrences(2, [1, [4, [5, 2], 2], [8, [2, 9]]]) == 3

