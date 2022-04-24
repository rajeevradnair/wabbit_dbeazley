# ex3.py

def convert_numbers(tree):
    if tree[0] == 'assign':
        return ('assign', tree[1], convert_numbers(tree[2]))
    elif tree[0] == 'binop':
        return ('binop', tree[1], convert_numbers(tree[2]), convert_numbers(tree[3]))
    elif tree[0] == 'name':
        return tree
    elif tree[0] == 'num':
        return ('num', int(tree[1]))

tree = ('assign', 'spam', 
        ('binop', '+', 
                  ('name', 'x'),
                  ('binop', '*', ('num', '34'), ('num', '567'))))

assert convert_numbers(tree) == \
    ('assign', 'spam', ('binop', '+', ('name', 'x'), ('binop', '*', ('num', 34), ('num', 567))))    
