# ex2.py

def to_source(tree):
    if tree[0] == 'assign':
        return tree[1] + ' = ' + to_source(tree[2])
    elif tree[0] == 'binop':
        return to_source(tree[2]) + ' '+tree[1]+' ' + to_source(tree[3])
    elif tree[0] == 'num':
        return tree[1]
    elif tree[0] == 'name':
        return tree[1]
    
tree = ('assign', 'spam', 
        ('binop', '+', 
                  ('name', 'x'),
                  ('binop', '*', ('num', '34'), ('num', '567'))))

assert to_source(tree) == 'spam = x + 34 * 567'
