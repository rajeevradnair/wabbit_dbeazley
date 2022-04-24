# r6.py

def reverse(items):
    def helper(remaining, result):
        if not remaining:
            return result
        else:
            return helper(remaining[1], (remaining[0], result))
    return helper(items, None)

assert reverse((1, (2, (3, (4, None))))) == (4, (3, (2, (1, None))))
