# r5.py

def merge(items_1, items_2):
    if not items_1:
        return items_2
    elif not items_2:
        return items_1
    elif items_1[0] <= items_2[0]:
        return [items_1[0]] + merge(items_1[1:], items_2)
    else:
        return [items_2[0]] + merge(items_1, items_2[1:])

assert merge([1,8,9,14,15], [2,10,23]) == [1,2,8,9,10,14,15,23]
