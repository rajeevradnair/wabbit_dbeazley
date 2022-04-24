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

# The following classes are used for the expression example in test_models.py.
# Feel free to modify as appropriate.  You don't even have to use classes
# if you want to go in a different direction with it.

class Node:

    def __init__(self, uuid):
        self.id = uuid
    pass


class Expression(Node):
    pass


class Statement(Node):
    pass


class Print(Statement):
    def __init__(self, message):
        self.message = str(message)

    def execute(self):
        print(self.message)


class PrintStatement(Statement):
    def __init__(self, node):
        self.node=node

    def __repr__(self):
        return f'print {self.node};'


class AssignmentOp(Statement):
    def __init__(self, op, identifier, expression):
        self.op = '='
        self.identifier = identifier
        self.expression = expression

    def __repr__(self):
        return f'{self.identifier} {self.op} {self.expression}'

    def __repr__c(self):
        return f'AssignmentOp({self.identifier} {self.op} {self.expression})'


class ConstantDeclaration(Statement):

    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression

    def __repr__c(self):
        return f'ConstantDeclaration({self.identifier} = {self.expression})'

    def __repr__(self):
        return f'const {self.identifier} = {self.expression};'

    def __str__(self):
        return f'ConstantDeclaration({self.identifier} = {self.expression})'

    def value(self):
        return self.__str__()


class VariableDeclaration(Statement):

    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.type=expression.type
        self.value=expression.value

    def __repr__c(self):
        return f'{self.identifier}={self.value}'

    def __repr__(self):
        return f'var {self.identifier} {self.type or ""} = {self.value or ""};'

    def __repr__c(self):
        return f'VariableDeclaration({self.identifier}[{self.type}]={self.value})'

    def value(self):
        return self.__repr__()


class IfThenElseBlock:

    def __init__(self, if_condition, then_block, elif_blocks=None, else_block=None):
        self.if_condition = if_condition
        self.then_block = then_block
        self.elif_blocks = elif_blocks
        self.else_block = else_block

    def __repr__(self):
        return f'if ({self.if_condition}) then {self.then_block} else {self.else_block} '


class Condition:

    def __init__(self, op, left_condition,right_condition):
        self.left_condition = left_condition
        self.op = op
        self.right_condition = right_condition

    def build_source_string(self, condition):
        if isinstance(condition, RelOp):
            return f'({condition})'
        elif isinstance(condition, TrueCondition):
            return f'{condition}'
        elif isinstance(condition, FalseCondition):
            return f'{condition}'
        elif isinstance(condition, Condition):
            return f'{condition.left_condition} {condition.op} {condition.right_condition}'
        else:
            raise RuntimeError(f"Can't convert {condition} to source")

    def __repr__(self):
        return self.build_source_string(self)


class TrueCondition:

    def __init__(self):
        self.value = True

    def __repr__(self):
        return 'true'


class FalseCondition:

    def __init__(self):
        self.value = False

    def __repr__(self):
        return 'false'


class ThenBlock:

    def __init__(self, block):
        self.block = block

    def __repr__(self):
        return f'{self.block}'


class ElseBlock:

    def __init__(self, block):
        self.block = block

    def __repr__(self):
        return f'{self.block}'


class WhileBlock:

    def __init__(self, while_condition, block):
        self.while_condition = while_condition
        self.block = block

    def __repr__(self):
        return f'while ({self.while_condition}) {self.block} '


class BreakStatement:

    def __repr__(self):
        return 'break'


class ContinueStatement:

    def __repr__(self):
        return 'continue'


class Block:

    def __init__(self,statements):
        self.statements=statements

    def __repr__(self):
        s = "{"
        for statement in self.statements:
            s = s + str(statement) + ";"
        s = s+"}"
        return s


class Variable:

    def __init__(self, name, type=None, value=None):
        self.name = name
        self.type = type
        self.value = value

    def __repr__(self):
        return f'{self.name}'

    def __repr__c(self):
        return f'Variable({self.name}[{self.type}]={self.value})'


class Constant:

    def __init__(self, name, type=None, value=None):
        self.name = name
        self.type = type
        self.value = value

    def __repr__(self):
        return f'{self.name}'

    def __repr__c(self):
        return f'Constant({self.name}[{self.type}]={self.value})'


class Literal:

    def __init__(self, value, type=None):
        self.value = value
        self.type = type

    def __repr__c(self):
        return f'Literal[{self.type}]({self.value})'

    def __repr__(self):
        return f'{self.value}'


class Name:
    #
    # something that needs to be bound to a constant or variable and ultimately a literal
    #
    def __init__(self, name):
        self.name=name

    def __repr__c(self):
        return f'Name({self.name})'

    def __repr__(self):
        return f'{self.name}'


class Type:

    def __init__(self, type):
        self.type = type

    def __repr__c(self):
        return f'DataType({self.type})'

    def __repr__(self):
        return f'{self.type}'


class Integer():
    '''
    Example: 42
    '''

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'{self.value}'

    def __repr__c(self):
        return f'Integer({self.value})'

    def value(self):
        return int(self.value)


class Float:
    '''
    Example: -3.14
    '''

    def __init__(self, value):
        self.value = value

    def __repr__c(self):
        return f'Float({self.value})'

    def __repr__(self):
        return f'{self.value}'

    def value(self):
        return float(self.value)


class Group(Expression):
    def __init__(self, code):
        self.code = code

    def __repr__(self):
        return f'( {self.code} )'  #


class BinOp(Expression):
    '''
    Example: left + right
    '''

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f'{self.left} {self.op} {self.right}'

    def __repr__c(self):
        return f'BinOp({self.op}, {self.left}, {self.right})'

    def eval(self):
        return f'{self.left.eval()} {self.op} {self.right.eval()})'


class RelOp(Expression):

    def __init__(self,op,left,right):
        self.left=left
        self.op=op
        self.right=right

    def __repr__c(self):
        return f'RelOp({self.left} {self.op} {self.right})'

    def __repr__(self):
        return f'{self.left} {self.op} {self.right}'


class Function(Expression):

    def __init__(self, name, fn_parameters,fn_return_type, fn_code_block):
        self.name = name
        self.fn_parameters = fn_parameters
        self.fn_return_type = fn_return_type
        self.fn_code_block = fn_code_block

    def __repr__(self):
        s = ""
        s = s + "func " + str(self.name) + "("
        if self.fn_parameters is not None and self.fn_parameters.parameters_list is not None:
            for counter, parameter in enumerate(self.fn_parameters.parameters_list):
                if counter != 0:
                    s = s + ","
                s = s + str(parameter)
        s = s + ") "
        s = s + str(self.fn_return_type) + " "
        s = s + str(self.fn_code_block)
        return s


class FnParameters:

    def __init__(self, parameters_list):
        assert isinstance(parameters_list, list), parameters_list
        self.parameters_list = parameters_list


class FnParameter:

    def __init__(self, declaration):
        if isinstance(declaration, VariableDeclaration):
            self.name=declaration.identifier
            self.value=declaration.value
            self.type=declaration.type

    def __repr__(self):
        return f'{self.name} {self.type}'


class FnReturnType:

    def __init__(self, return_type):
        assert isinstance(return_type, Type), return_type
        self.return_type = return_type

    def __repr__(self):
        return f'{self.return_type}'


class FnReturnStatement:

    def __init__(self, expression):
        assert  isinstance(expression, Expression), expression
        self.expression = expression

    def __repr__(self):
        return f'return {self.expression}'


class FnCall:

    def __init__(self, fn_name, fn_arguments):
        assert isinstance(fn_arguments,FnArguments), fn_arguments
        self.fn_name = fn_name
        self.fn_arguments = fn_arguments

    def __repr__ (self):
        s = ""
        s = s + self.fn_name + "( "
        if self.fn_arguments is not None and self.fn_arguments.arguments_list is not None:
            for counter, argument in enumerate(self.fn_arguments.arguments_list):
                if counter != 0:
                    s = s + ","
                s = s + str(argument)
        s = s + " )"
        return s


class FnArguments:

    def __init__(self, arguments_list):
        assert isinstance(arguments_list, list), arguments_list
        self.arguments_list = arguments_list


class FnArgument:

    def __init__(self, argument):
        self.argument = argument

    def __repr__(self):
        return f'{self.argument}'


class ExprStatement:

    def __init__(self, block):
        self.block=block

    def __repr__(self):
        s = "{"
        for statement in self.block.statements:
            s = s + str(statement) + ";"
        s = s+"}"
        return s


class ReturnVal:

    def __init__(self,node):
        assert (isinstance(node, (Name, Literal, Constant, Variable)), node)
        self.node=node

    def __repr__(self):
        return f'{self.node}'


# Debugging function to convert a model back into source code (for easier viewing)
#
# Special challenge: Write this function in a way so that it produces
# the output code with nice formatting such as having different indentation
# levels in "if" and "while" statements.

def to_source01(node):
    if isinstance(node,Integer):
        return str(node)
    elif isinstance(node, Name):
        return str(node)
    elif isinstance(node, Float):
        return str(node)
    elif isinstance(node, Print):
        node.execute()
        return ""
    elif isinstance(node,Group):
        return str(node)
    elif isinstance(node,BinOp):
        return str(node)
    elif isinstance(node, list):
        for n in node:
            to_source01(n)
    elif isinstance(node, Variable):
        return str(node)
    elif isinstance(node, Constant):
        return str(node)
    elif isinstance(node, Literal):
        return str(node)
    elif isinstance(node, ConstantDeclaration):
        return str(node)
    elif isinstance(node, VariableDeclaration):
        return str(node)
    elif isinstance(node, RelOp):
        return str(node)
    elif isinstance(node, AssignmentOp):
        return str(node)
    else:
        print(type(node))
        raise RuntimeError(f"Can't convert {node} to source")


def to_source(node):
    if isinstance(node, Integer):
        return str(node.value)

    elif isinstance(node, BinOp):
        return f'{to_source(node.left)} {node.op} {to_source(node.right)}'

    else:
        raise RuntimeError(f"Can't convert {node} to source")
