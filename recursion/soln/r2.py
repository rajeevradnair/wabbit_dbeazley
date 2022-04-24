# r2.py

def maxval(items):
    if len(items) == 1:
        return items[0]
    else:
        mv = maxval(items[1:])
        return items[0] if items[0] > mv else mv

assert maxval([1, 9, -3, 7, 13, 2, 3]) == 13
