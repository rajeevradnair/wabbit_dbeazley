# ex2.py

def to_source(tree):
    pass
    
tree = ('assign', 'spam', 
        ('binop', '+', 
                  ('name', 'x'),
                  ('binop', '*', ('num', '34'), ('num', '567'))))

assert to_source(tree) == 'spam = x + 34 * 567'
