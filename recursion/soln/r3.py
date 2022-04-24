# r3.py

def flatten(items):
    result = []
    for it in items:
        if isinstance(it, list):
            result.extend(flatten(it))
        else:
            result.append(it)
    return result

assert flatten([1, [2, [3,4], 5,], 6]) == [1,2,3,4,5,6]

