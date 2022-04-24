# typecheck.py
#
# Type Checking
# =============
#
# This file implements type checking.  But first, what is type-checking?
# In the file interp.py, you wrote an interpreter that actually executed
# Wabbit code.  In your interpreter, you were asked to check for various
# kinds of errors.  For example, undefined variable names, type mismatches,
# and other issues.
#
# A type-checker, in some sense, is an "interpreter" that *only*
# performs error checking.  Instead of literally executing a program,
# a checker looks at a program and determines what it would do *if* it
# actually executed.  As an example, suppose you had an arithmetic
# expression like this:
#
#      2 + 3
#
# Instead of literally performing that calculation, a type checker would
# view the expression as a higher-level operation like this:
#
#      int + int
#
# It would then conclude that the result of the calculation has type "int".
# This is *NOT* the same as actually performing the calculation. It's
# just reasoning about the nature of the calculation. The actual values
# don't matter (whatever they are, you know the result is still an "int").
#
# A type checker will uncover errors.  For example, if it encountered
# a fragment of code like this:
#
#      2 + true
#
# It would look at the underlying types and see:
#
#      int + bool
#
# Because the types of the left and right operands don't match up,
# an error would be reported.
#
# To implement a type-checker, you could start from your interpreter
# code--copying and pasting it here.   You could then strip the code
# down to only handling types and error messages.
#
# The directory tests/Errors has Wabbit programs with various errors.

from .model import *

# Class that holds the environment for checking.  It's almost
# like the environment for the interpreter.
class CheckContext:
    def __init__(self, program):
        self.program = program
        self.env = { }

    # Use this method to report an error message.  One challenge
    # with error messages is connecting them back with the original
    # source code.  To do this, we'll redirect errors back to
    # the original program object.
    def error(self, message):
        self.program.error(message)
        
# Top-level function used to check a program module.  module is an object that
# holds information about the program including the model.
def check_program(program):
    context = CheckContext(program)
    check(program.model, context)
    # Maybe return True/False if there are errors
    return not program.have_errors

# Internal function used to check nodes with an environment.  Critical
# point: Everything is focused on types.  The result of an expression
# is a type.  The inputs to different operations are types.

def check(node, context):
    # Carefully notice that we are only interested in the type.
    # There are no "values".
    if isinstance(node, Integer):
        return "int"

    elif isinstance(node, Float):
        return "float"

    elif isinstance(node, BinOp):
        # Note: You don't actually compute anything. You only check the types.
        left_type = check(node.left, context)
        right_type = check(node.right, context)
        if left_type != right_type:
            context.error("Type error")       # How do you report errors?

        result_type = ...     # Figure out result of doing the calculation
        return result_type
            
    elif isinstance(node, PrintStatement):
        # For other statements, you check the value, but don't actually execute anything
        valuetype = check(node.eval, context)
        
    else:
        raise RuntimeError(f"Couldn't check {node}")

# Sample main program
def main(filename):
    from .parse import parse_file
    program = parse_file(filename)
    if check_program(program):
        print("Good Wabbit!")

if __name__ == '__main__':
    import sys
    main(sys.argv[1])



        


        
