# model.py
#
# This file defines the data model for Wabbit programs.  The data
# model is a data structure that represents the contents of a program
# as objects, not text.  Sometimes this structure is known as an
# "abstract syntax tree" or AST.  However, the model is not
# necessarily a direct representation of the syntax of the language.
# So, we'll prefer to think of it as a more generic data model
# instead.
#
# To do this, you need to identify the different "elements" that make
# up a program and encode them into classes.  To do this, it may be
# useful to slightly "underthink" the problem. To illustrate, suppose
# you wanted to encode the idea of "assigning a value."  Assignment
# involves a location (the left hand side) and a value like this:
#
#         location = expression;
#
# To represent this idea, maybe you make a class with just those parts:
#
#     class Assignment:
#         def __init__(self, location, expression):
#             self.location = location
#             self.expression = expression
#
# Alternatively, maybe you elect to store the information in a tuple:
#
#    def Assignment(location, expression):
#        return ('assignment', location, expression)
#
# What are "location" and "expression"?  Does it matter? Maybe
# not. All you know is that an assignment operator definitely requires
# both of those parts.  DON'T OVERTHINK IT.  Further details will be
# filled in as the project evolves.
# 
# Work on this file in conjunction with the top-level
# "test_models.py" file.  Go look at that file and see what program
# samples are provided.  Then, figure out what those programs look
# like in terms of data structures.
#
# There is no "right" solution to this part of the project other than
# the fact that a program has to be represented as some kind of data
# structure that's not "text."   You could use classes. You could use 
# tuples. You could make a bunch of nested dictionaries like JSON. 
# The key point: it must be a data structure.
#
# Starting out, I'd advise against making this file too fancy. Just
# use basic data structures. You can add usability enhancements later.
# -----------------------------------------------------------------------------

NoneType = type(None)

# The following classes are used for the expression example in test_models.py.
# Feel free to modify as appropriate.  You don't even have to use classes
# if you want to go in a different direction with it.

class Node:
    def __init__(self):
        self.id = ...   # Primary-key (unique)

# Expressions represent values.   Eg. BinOp
class Expression(Node):
    pass

# Statement represents an "action". Not a value. Eg. print.
class Statement(Node):
    pass

# A declaration is a special kind of statement that additionally declares
# the existence of a name.
class Declaration(Statement):
    pass

# --- Expressions

class Integer(Expression):
    '''
    Example: 42
    '''
    def __init__(self, value):
        assert isinstance(value, str), value
        self.value = value

    def __repr__(self):
        return f'Integer({self.value})'

class Float(Expression):
    '''
    Example: 4.2
    '''
    def __init__(self, value):
        assert isinstance(value, str), value        
        self.value = value

    def __repr__(self):
        return f'Float({self.value})'

class Boolean(Expression):
    '''
    Example: true, false
    '''
    def __init__(self, value):
        assert value in {'true', 'false'}, value
        self.value = value

    def __repr__(self):
        return f'Boolean({self.value})'
    
class Name(Expression):
    '''
    Example: x
    '''
    def __init__(self, value):
        assert isinstance(value, str), value        
        self.value = value

    def __repr__(self):
        return f'Name({self.value})'
    
class BinOp(Expression):
    '''
    Example: left + right
    '''
    def __init__(self, op, left:Expression, right:Expression):
        assert isinstance(left, Expression), left
        assert isinstance(right, Expression), right
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f'BinOp({self.op}, {self.left}, {self.right})'

class RelOp(Expression):
    '''
    Example: left < right
    '''
    def __init__(self, op, left:Expression, right:Expression):
        assert isinstance(left, Expression), left
        assert isinstance(right, Expression), right
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f'RelOp({self.op}, {self.left}, {self.right})'
    
class UnaryOp(Expression):
    '''
    Example: -value
    '''
    def __init__(self, op, value):
        assert isinstance(value, Expression), value
        self.op = op
        self.value = value

    def __repr__(self):
        return f'UnaryOp({self.op}, {self.value})'

class Grouped(Expression):
    '''
    Example: ( value )
    '''
    def __init__(self, value):
        assert isinstance(value, Expression), value        
        self.value = value

    def __repr__(self):
        return f'Grouped({self.value})'


class Assignment(Expression):
    '''
    Example: x = 2 + 3
    '''
    def __init__(self, location, value):
        assert isinstance(location, Expression), location
        assert isinstance(value, Expression), value        
        self.location = location
        self.value = value

    def __repr__(self):
        return f'Assignment({self.location}, {self.value})'


class Compound(Expression):
    '''
    One-or-more statements used as an expression.
    
    x = { stmt1; stmt2; ...; expr }
    '''
    def __init__(self, statements):
        assert isinstance(statements, list) and len(statements) > 0, statements
        self.statements = statements

    def __repr__(self):
        return f'Compound({self.statements})'
    
# -- Statements


class ExprStatement(Statement):
    '''
    An expression used as a statement. Example:

    2 + 3;
    x;
    '''
    def __init__(self, value):
        assert isinstance(value, Expression), value
        self.value = value

    def __repr__(self):
        return f'ExprStatement({self.value})'
    
class PrintStatement(Statement):
    '''
    Example: print value;
    '''
    def __init__(self, value):
        assert isinstance(value, Expression), value        
        self.value = value

    def __repr__(self):
        return f'PrintStatement({self.value})'



class IfStatement(Statement):
    '''
    if test { consequence }
    if test { consequence } else { alternative }
    '''
    def __init__(self, test, consequence, alternative):
        assert isinstance(test, Expression), test
        assert isinstance(consequence, Block), consequence
        assert isinstance(alternative, (Block, NoneType)), alternative
        self.test = test
        self.consequence = consequence
        self.alternative = alternative

    def __repr__(self):
        return f'IfStatement({self.test}, {self.consequence}, {self.alternative})'

class WhileStatement(Statement):
    '''
    while test { statements }
    '''
    def __init__(self, test, body):
        assert isinstance(test, Expression), test
        assert isinstance(body, Block), body
        self.test = test
        self.body = body

    def __repr__(self):
        return f'WhileStatement({self.test}, {self.body})'
    
# -- Declarations

class ConstDeclaration(Declaration):
    '''
    Example:  const pi = 3.14159;
              const pi float = 3.14159;
              const tau = 2.0 * pi; 
    Immutable.
    '''
    def __init__(self, name, type, initializer):
        self.name = name
        self.type = type    # Optional
        self.initializer = initializer

    def __repr__(self):
        return f'ConstDeclaration({self.name}, {self.type}, {self.initializer})'

class VarDeclaration(Declaration):
    '''
    Example:  var n = 20;
              var n int;     // Initialization optional. 
    Mutable. 
    '''
    def __init__(self, name, type, initializer):
        self.name = name
        self.type = type    # Optional
        self.initializer = initializer   # Optional

    def __repr__(self):
        return f'VarDeclaration({self.name}, {self.type}, {self.initializer})'

class BreakStatement(Statement):
    def __repr__(self):
        return f'BreakStatement()'

class ContinueStatement(Statement):
    def __repr__(self):
        return f'ContinueStatement()'
    
# --- Things that don't really go anywhere else

class Block(Node):
    '''
    Zero or more statements
    '''
    def __init__(self, statements):
        self.statements = statements

class Type(Node):
    '''
    A typename like "int", "float", etc.
    '''
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'Type({self.name})'


class FnDeclaration(Statement):

    def __init__(self, name, fn_parameters,fn_return_type, fn_code_block=None):
        assert isinstance(fn_return_type, Type), fn_return_type
        #assert isinstance(fn_code_block, Block), fn_code_block
        self.name = name.value
        self.fn_parameters = fn_parameters
        self.fn_return_type = fn_return_type
        self.fn_code_block = fn_code_block

    def __repr__(self):
        return f'FunctionDeclaration({self.name})'


class FnParameters:

    def __init__(self, parameters_list):
        assert isinstance(parameters_list, list), parameters_list
        self.parameters_list = parameters_list


class FnParameter(Declaration):

    def __init__(self, param_declaration):
        assert isinstance(param_declaration, VarDeclaration), param_declaration
        self.param_declaration = param_declaration

    def __repr__(self):
        return f'FunctionParameter{self.param_declaration}'


class FnReturn(Statement):

    def __init__(self, expression):
        assert isinstance(expression, Expression), expression
        self.expression = expression


class FnCall(Expression):

    def __init__(self, name, expression):
        self.name = name
        self.expression = expression


class FnArguments():
    pass



# Debugging function to convert a model back into source code (for easier viewing)
#
# Special challenge: Write this function in a way so that it produces
# the output code with nice formatting such as having different indentation
# levels in "if" and "while" statements.

# Think about this big if-statement
# Could be Python 3.10+ pattern matching.
# Could be the "visitor pattern"  (tomorrow).

# Modify for "pretty-printing"  (indentation)

# "to_source" is separate from the model in some way

# How would you modify to auto-indent the output?
# Automatically format the code nicely (like gofmt, black, etc.)
def to_source(node):
    if isinstance(node, Integer):
        return str(node.value)

    elif isinstance(node, Float):
        return str(node.value)

    elif isinstance(node, Boolean):
        return str(node.value)
    
    elif isinstance(node, Name):
        return node.value

    elif isinstance(node, Type):
        return node.name
    
    elif isinstance(node, BinOp):
        return f'{to_source(node.left)} {node.op} {to_source(node.right)}'

    elif isinstance(node, RelOp):
        return f'{to_source(node.left)} {node.op} {to_source(node.right)}'
    
    elif isinstance(node, UnaryOp):
        return f'{node.op}{to_source(node.value)}'

    elif isinstance(node, ExprStatement):
        return f'{to_source(node.value)};'
    
    elif isinstance(node, PrintStatement):
        return f'print {to_source(node.value)};'

    elif isinstance(node, Grouped):
        return f'({to_source(node.value)})'

    elif isinstance(node, ConstDeclaration):
        if node.type:
            return f'const {node.name} {to_source(node.type)} = {to_source(node.initializer)};'
        else:
            return f'const {node.name} = {to_source(node.initializer)};'

    elif isinstance(node, VarDeclaration):
        if node.type:
            code = f'var {node.name} {to_source(node.type)}'
        else:
            code = f'var {node.name}'

        if node.initializer:
            code += f' = {to_source(node.initializer)}'
        return code + ';'

    elif isinstance(node, Assignment):
        return f'{to_source(node.location)} = {to_source(node.value)}'

    elif isinstance(node, IfStatement):
        code = f'if {to_source(node.test)} ' + '{\n'
        code += to_source(node.consequence) + '\n}'
        if node.alternative:
            code += ' else {\n'
            code += to_source(node.alternative)
            code += '\n}'
        return code

    elif isinstance(node, WhileStatement):
        code = f'while {to_source(node.test)} ' + '{\n'
        code += to_source(node.body) + '\n}'
        return code

    elif isinstance(node, BreakStatement):
        return 'break;'

    elif isinstance(node, ContinueStatement):
        return 'continue;'
    
    elif isinstance(node, Block):
        return '\n'.join([to_source(n) for n in node.statements])

    elif isinstance(node, Compound):
        return '{ ' + ' '.join([to_source(n) for n in node.statements]) + '}'

    elif isinstance(node, FnDeclaration):
        code = f'func {node.name} '
        code += '(' + ', '.join([to_source(n) for n in node.fn_parameters.parameters_list]) + ') '
        code += to_source(node.fn_return_type)
        code += ' {\n' + to_source(node.fn_code_block) + '\n}\n'
        return code

    elif isinstance(node, FnParameters):
        return ','.join([to_source(n) for n in node.parameters_list])

    elif isinstance(node, FnParameter):
        if node.param_declaration.type:
            return node.param_declaration.name.value + ' ' + to_source(node.param_declaration.type)

    elif isinstance(node, FnReturn):
        return 'return ' + to_source(node.expression) + ' ;'

    else:
        raise RuntimeError(f"Can't convert {node} to source")



    
