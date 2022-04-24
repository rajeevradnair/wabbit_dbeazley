# ex4.py

def simplify_tree(tree):
    if tree[0] == 'assign':
        return ('assign', tree[1], simplify_tree(tree[2]))
    elif tree[0] == 'binop':
        op = tree[1]
        left = simplify_tree(tree[2])
        right = simplify_tree(tree[3])
        if left[0] == 'num' and right[0] == 'num':
            leftval = left[1]
            rightval = right[1]
            if op == '+':
                return ('num', leftval + rightval)
            elif op == '*':
                return ('num', leftval * rightval)
        return ('binop', op, left, right)
    else:
        return tree

tree = ('assign', 'spam', 
        ('binop', '+', 
                  ('name', 'x'),
                  ('binop', '*', ('num', 34), ('num', 567))))

assert simplify_tree(tree) == \
    ('assign', 'spam', ('binop', '+', ('name', 'x'), ('num', 19278)))
