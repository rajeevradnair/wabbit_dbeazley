# r1.py
def count_multiples(a, b):
    if b % a == 0:
        return 1 + count_multiples(a, b // a)
    else:
        return 0

assert count_multiples(2, 6) == 1
assert count_multiples(2, 12) == 2
assert count_multiples(3, 11664) == 6

    
