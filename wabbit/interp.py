# interp.py
#
# In order to write a compiler for a programming language, it helps to
# have some kind of understanding of how programs written in the
# programming language are actually supposed to work. A language is
# more than just "syntax" or a data model.  There have to be some kind
# of semantics that describe what happens when a program in the
# language executes.
#
# One way to specify the semantics is to write a so-called
# "definitional interpreter" that directly executes the data
# model. This might seem like cheating--after all, our final goal is
# not to write an interpreter, but a compiler. However, if you can't
# write an interpreter, chances are you can't write a compiler either.
# So, the purpose of doing this is to pin down fine details as well as
# our overall understanding of what needs to happen when programs run.
# Writing an interpreter will also help understand things that are
# *NOT* supposed to happen (i.e., programming errors).
#
# The process of writing an interpreter is mostly straightforward.
# You'll write a top-level function called "interpret()". 
# For each class in the model.py file, you'll then write a 
# a conditional check and some code that executes the model:
#
#    def interpret(node, context):
#        ...
#        if isinstance(node, ModelClass):
#            # Execute "node" in the environment "context"
#            ...
#            return (result_type, result_value)
#        ...
#   
# The input to the interpret() will be an object from model.py (node)
# along with an object respresenting the execution environment
# (context).  In executing the node, the environment might be
# modified (for example, when executing assignment expressions,
# making variable definitions, etc.).  The return result will
# consist of a type along with a value.   These types and values
# are from Wabbit, not Python.   For example, a result might 
# look like ('int', 34) or ('float', 3.4).
#
# In addition to executing the code, you should try to check for
# as many programming errors as possible.   For example, Wabbit
# does NOT allow mixed-type operations (e.g., 2 + 3.5 is a type
# error).   If you encounter an error, have your interpreter
# stop with a RuntimeError exception.  Better yet, have it produce
# a nice error message that indicates exactly what's wrong.
#
# For testing, try running your interpreter on the models you
# created in the test_models.py file.   Verify that their output
# is what you expect it to be.   Later, when you have written
# a parser, you should continue to check your interpreter against
# various programs in the tests/Programs/ directory.
#
# The most difficult parts of writing the interpreter concern
# unusual control flow.  For example, the handling of "break"
# and "continue" statements inside a while loop. 
#
# The handling of function calls is tricky.  For functions,
# you need to worry about the delicate matter of variable scoping.
# Specifically, each call to a function needs to create a new
# environment in which local variables created inside that function
# can live.  Moreover, the function still needs to be able to
# access variables defined in the global scope. To do this,
# you'll probably need multiple dictionaries.  You'll need to
# link those dictionaries together in some manner.

from .model import *

_default_type_values = {
    'int': 0,
    'float': 0.0,
    'bool': False,
    'char': '\x00'
}


class FunctionReturnFlowBreaker(Exception):

    def __init__(self, return_type, return_value, message=None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.return_type = return_type
        self.return_value = return_value

    def get_payload(self):
        if self.return_type == 'int':
            return self.return_type, int(self.return_value)
        elif self.return_type == 'float':
            return self.return_type, float(self.return_value)
        elif self.return_type == 'char':
            return self.return_type, eval(self.return_value)
        elif self.return_type == 'bool':
            _r = True if self.return_value == 'true' else False
            return self.return_type, _r


# Class representing the execution environment of the interpreter.
class Context:

    # create a context from scratch
    def __init__(self, parent=None):
        self.env = {}  # Storage for all scoped variables
        self.parent = parent  # Pointer to parent' scope

    # spawn a child context, passing the current scope as the parent
    def spawn_child_context(self):
        return Context(parent=self)

    # Lookup const, var in the current scope. And if not found, search recursively in the parent scope
    def lookup(self, name):
        if name in self.env:
            return self.env[name]
        else:
            # print('recursing through parent context looking for ', name)
            if self.parent:
                return self.parent.lookup(name)
            else:
                raise RuntimeError("Variable " + name + " not defined")

    # Define new const, vars always in the current scope
    def define(self, name, initializer):
        # self.display_stack()
        if name in self.env:
            kind, _2, _3 = self.env[name]
            if kind == 'func':
                raise RuntimeError(f"Function {name}() already defined")
            else:
                self.display_stack()
                raise RuntimeError(f"Variable {name} already declared")
        self.env[name] = initializer

    # Assign value to a const, var in the current scope. And if not found, search recursively in the parent scope
    def assign(self, name, value):
        if name not in self.env:
            if self.parent:
                self.parent.assign(name, value)
            else:
                raise RuntimeError("Variable not defined")
        self.env[name] = value

    def display_stack(self, lvl=1):
        print('--' * lvl + '>[Stack]: <' + str(self.env))
        if self.parent is not None:
            self.parent.display_stack(lvl+1)

    def display_stack_nr(self, lvl=1, ctxt=None):
        if ctxt:
            print('--' * lvl + '>[Stack]:' + str(ctxt.env))
            self.display_stack_nr(ctxt=self.parent)
        else:
            return None

# Top level function that interprets an entire program. It creates the
# initial environment that's used for storing variables.

def interpret_program(model):
    # Make the initial environment (a dict).  The environment is
    # where you will create and store variables.
    context = Context(parent=None)
    return interpret(model, context)


# Internal function to interpret a node in the environment.  You need
# to expand to cover all of the classes in the model.py file. 

def interpret(node, context):

    # returning wabbit-type, actual pythonic value

    if isinstance(node, Integer):
        return ('int', int(node.value))

    elif isinstance(node, Float):
        return ('float', float(node.value))

    elif isinstance(node, PrintStatement):
        # print("Interpreting PrinStatement", node.value)

        valuetype, value = interpret(node.value, context)
        # print (valuetype, value)
        # The type is useful if you need to carry out special processing.
        if valuetype == 'char':
                print(value, end='')
        elif valuetype == 'bool':
            # print(value)
            print('true' if value else 'false')
        elif valuetype == 'int':
            print(value)
        elif valuetype == 'float':
            print(value)
        else:
            print(value)

    elif isinstance(node, Boolean):
        # this is the code which killed me in the mandelbrot set diagram creation
        # remember tokenization process gives back 'true' and 'false' as python strings
        # you need to convert from python string into python boolean - True False
        return 'bool', node.value == 'true'

    elif isinstance(node, Char):
        return 'char', eval(node.value)

    elif isinstance(node, Name):

        kind, value_type, value = context.lookup(node.value)
        k = (value_type, value)
        if node.value == 'in_mandel':
            pass
            # print('in_mandel',k)
        return k

    elif isinstance(node, BinOp):

        # Note: all values are tagged with a Wabbit type.
        # See the code for "Integer" and "Float" above.
        # Knowing the type is essential for type-checking.
        left_type, left_value = interpret(node.left, context)
        right_type, right_value = interpret(node.right, context)
        if left_type != right_type:
            raise RuntimeError("Type error in binary operator")
        if left_type in {'int', 'float'}:
            if node.op == '+':
                return left_type, left_value + right_value
            elif node.op == '-':
                return left_type, left_value - right_value
            elif node.op == '*':
                return left_type, left_value * right_value
            elif node.op == '/':
                if left_type == 'int':
                    return left_type, left_value // right_value
                else:
                    return left_type, left_value / right_value
        raise RuntimeError(f"Unsupported operation {node.op}")

    elif isinstance(node, RelOp):
        left_type, left_value = interpret(node.left, context)
        right_type, right_value = interpret(node.right, context)
        if left_type != right_type:
            raise RuntimeError("Type error in relational operator")
        # print ('RelOp -->', left_type, left_value, right_type, right_value)
        if left_type in {'int', 'float', 'char'}:
            if node.op == '<':
                return 'bool', left_value < right_value
            elif node.op == '<=':
                return 'bool', left_value <= right_value
            elif node.op == '==':
                return 'bool', left_value == right_value
            elif node.op == '>=':
                return 'bool', left_value >= right_value
            elif node.op == '>':
                return 'bool', left_value > right_value
            elif node.op == '!=':
                return 'bool', left_value != right_value
        elif left_type in {'bool'}:
            if node.op == '==':
                return 'bool', left_value == right_value
            elif node.op == '!=':
                return 'bool', left_value != right_value
        raise RuntimeError(f"Unsupported operation {node.op} for {left_type}")

    elif isinstance(node, UnaryOp):
        value_type, value = interpret(node.value, context)
        if value_type in {'int', 'float'}:
            if node.op == '-':
                value *= (-1)
            return value_type, value
        if value_type in {'bool'}:
            # print(value_type, value)
            value = (not value)
            return value_type, value
        raise RuntimeError(f"Unsupported operation {node.op}")

    elif isinstance(node, Grouped):
        # print('interp.py --> Grouped.value is ', node.value)
        return interpret(node.value, context)

    elif isinstance(node, ConstDeclaration):
        kind = 'const'
        value_type, value = interpret(node.initializer, context)
        if value_type in {'int', 'float', 'bool', 'char'}:
            context.define(node.name, (kind, value_type, value))
            # context.display_stack()
        else:
            raise RuntimeError(f"Unsupported type in constant declaration - {value_type} in {node.name}")
        return None

    elif isinstance(node, VarDeclaration):
        kind = 'var'
        if node.initializer and node.initializer is not NoneType:
            value_type, value = interpret(node.initializer, context)
        else:
            value_type, value = node.type.name, _default_type_values[node.type.name]
        # print('interp.py -->defining variable', node.name, node)
        context.define(node.name, (kind, value_type, value))
        return None

    # function definition
    elif isinstance(node, FunctionDefinition):
        kind = 'func'
        context.define(node.name.value, (kind, node.fn_return_type, node))
        # context.display_stack()

        return None

    # function application (i.e. function call)
    elif isinstance(node, FunctionApplication):

        # save off the current context for future restoration
        fd = context.lookup(node.name.value)[2]
        save_current_context = context

        # print('fn node, defn node being evaluated', node.name, fd.name)
        # if fd.fn_code_block:
        #    if fd.fn_code_block.statements:
        #        for statement in fd.fn_code_block.statements:
        #            print('--->fn defn statements to be evaluated', statement)

        # create a new context
        context = context.spawn_child_context()
        # context.display_stack()

        # retrieve the function definition
        assert isinstance(fd, FunctionDefinition), fd   # Being a bit defensive here
        assert isinstance(fd.fn_code_block.statements, list) and fd.fn_code_block.statements is not None, fd.fn_code_block

        # initialize the context from function definition
        if fd.fn_parameters:
            kind = 'var'
            placement_order=[]
            for parameter in fd.fn_parameters.parameters_list:
                assert isinstance(parameter, FunctionParameter), parameter
                if parameter.initializer and not (parameter.initializer in {None, NoneType}):
                    value_type, value = interpret(parameter.initializer, context)
                else:
                    value_type, value = parameter.type.name, _default_type_values[parameter.type.name]
                context.define(parameter.name, (kind, value_type, value))
                placement_order.append(parameter.name)

        # initialize with values from function call
        if fd.fn_parameters and node.fn_arguments and (len(fd.fn_parameters.parameters_list) == len(node.fn_arguments.arguments_list)):
            for counter, argument in enumerate(node.fn_arguments.arguments_list):

                _ts, _vs =  interpret(argument, save_current_context)

                _kd = context.lookup(placement_order[counter])[0]
                _td = context.lookup(placement_order[counter])[1]
                _vd = None

                if _ts == _td == 'int':
                    _vd = int(_vs)
                elif _ts == _td == 'float':
                    _vd = float(_vs)
                elif _ts == _td == 'char':
                    _vd = eval(_vs)
                elif _ts == _td == 'bool':
                    _vd = True if argument.value == 'true' else False
                else:
                    raise RuntimeError(f'interp.py --> Type mismatch in {node.name.value}() func call. Expected {_td} type in argument {placement_order[counter]}')
                # over-write the values in the stack with the values from the argument list
                context.assign(placement_order[counter],  (_kd, _td, _vd))
        else:
            raise RuntimeError(f'interp.py --> Number of arguments in the call to func {node.name.value}() mismatches the func definition')

        # execute statement(s) in the code block
        for statement in fd.fn_code_block.statements:
            if statement:

                # Special case for handling Wabbit Return statement
                if isinstance(statement, FunctionReturn):

                    assert isinstance(statement.expression, Expression), statement.expression
                    return_type, return_value = interpret(statement.expression, context)

                    # restore the saved context into current
                    context = save_current_context

                    # print('stack after restore, before the return statement')
                    # context.display_stack()

                    return return_type, return_value

                # Process regular statements
                else:

                    return_type, return_value = None, None

                    try:
                        interpret(statement, context)
                    except FunctionReturnFlowBreaker as e0:
                        return_type, return_value = e0.get_payload()
                        # print('unpacked from e0 ==>', return_type, return_value)
                        return return_type, return_value

            else:
                raise RuntimeError(f'interp.py --> Encountered a None statement in {fd.name}() function definition! Check AST')

        # restore the saved context into current
        context = save_current_context

        # Function had no Return statement
        # Is this acceptable?
        return None

    elif isinstance(node, FunctionReturn):

        assert isinstance(node.expression, Expression), node.expression
        return_type, return_value = interpret(node.expression, context)
        raise FunctionReturnFlowBreaker(return_type, return_value)

    elif isinstance(node, LogicalOp):
        left_type, left_val = interpret(node.left, context)
        if left_type != 'bool':
            raise RuntimeError(f'Type error in logical operator')

        # you could add left_type, right_type check, but commenting the code to allow for short-circuit
        # right_type, right_val = interpret(node.right, context)
        # if left_type ! = right_type:
        #   raise RuntimeError(f'Types do not match in logical operator')

        # revised code with short-circuit
        if node.op == '||':
            return (left_type, left_val) if left_val else interpret(node.right, context)
        elif node.op == '&&':
            return interpret(node.right, context) if left_val else (left_type, left_val)
        else:
            raise RuntimeError("Bad logical op")

    elif isinstance(node, Assignment):
        right_type, right_value = interpret(node.value, context)
        # print('Assignment right side =>', right_type, right_value)
        left_kind, left_type, left_value = context.lookup(node.location.value)
        if left_kind == 'const':
            raise RuntimeError(f"Constant values cannot be changed - {node.location.value}")
        if left_type != right_type:
            raise RuntimeError(f"Type mismatch in assignment operation - {node.location.value}")
        # print('Left side before the assignment =>', node.location.value, left_kind, left_type, right_value)
        context.assign(node.location.value, (left_kind, left_type, right_value))
        # print('Left side after the assignment =>', node.location.value, left_kind, left_type, right_value)
        # context.display_stack()
        return left_type, left_value

    elif isinstance(node, IfStatement):

        condition_test_type, condition_test_value = interpret(node.test, context)
        if condition_test_type != 'bool':
            raise RuntimeError("Test in an If-statement must be a bool")

        if condition_test_value:
            interpret(node.consequence, context.spawn_child_context())
        else:
            if node.alternative:
                if node.alternative.statements:
                    interpret(node.alternative, context.spawn_child_context())

        return None

    elif isinstance(node, ExprStatement):
        # returning value is especially helpful if you enclose a compound statement within ExprStatement
        return interpret(node.value, context)

    elif isinstance(node, WhileStatement):
        # nc = context.spawn_child_context()
        while True:
            condition_test_type, condition_test_value = interpret(node.test, context)
            if condition_test_type != 'bool':
                raise RuntimeError("Test in a While-statement must be a bool")
            if condition_test_value:
                try:
                    interpret(node.body, context)
                except Break:
                    break
                except Continue:
                    continue
            else:
                break
        return None

    elif isinstance(node, BreakStatement):
        raise Break()

    elif isinstance(node, ContinueStatement):
        raise Continue()

    elif isinstance(node, Compound):
        # print('Entered compound statement')
        child_context=context.spawn_child_context()
        statements = node.statements

        for statement in statements[:-1]:
            interpret(statement, child_context)

        # last statement should be an expression returning values. Therefore, ensure last statement of
        # a compound statement is never within an ExprStatement
        return interpret(statements[-1], child_context)

    elif isinstance(node, Block):
        if node.statements:
            for statement in node.statements:
                if statement:
                    interpret(statement, context)
                else:
                    raise RuntimeError('interp.py --> encountered a None statement')
        else:
            raise RuntimeError(f"Nothing to interpret in Block {node}")
        return None

    else:

        raise RuntimeError(f"No interp handler for {node} of type {str(type(node))}")


def interpret_assignment_lhs(node, context, assigned_value):
    if isinstance(node, Name):
        valtype, value = assigned_value
        kind, decltype, _ = context.lookup(node.value)
        if kind == 'const':
            raise RuntimeError("Can't assign to const")
        if valtype != decltype:
            raise RuntimeError(f"Type error in assignment. {decltype} = {valtype}")
        context.assign(node.value, (kind, valtype, value))
        return (valtype, value)
        ...
    # elif isinstance(node, Array):
    #    ...
    else:
        raise RuntimeError(f"Can't assign to {node}")

class Break(Exception):
    pass


class Continue(Exception):
    pass


# Making interpret a first-class program here

if __name__ == '__main__':
    import sys
    from .parse import parse_file
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python3 -m wabbit.parse filename')
    program = parse_file(sys.argv[1])

    print(f'\nMODEL pretty print ...')
    print(to_source_pp(program.model,DisplayContext()))

    print(f'\nINTERPRETER initiated ...')
    interpret_program(program.model)
    print(f'\nINTERPRETER finished execution')

