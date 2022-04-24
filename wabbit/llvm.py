# wabbit/llvm.py
#
# In this file you will have your compiler generate LLVM output.  Don't
# start this unless you have first worked through the LLVM Tutorial in
#
#     docs/LLVM-Tutorial.md
#
# Once you have done that, come back here.
#
# The overall strategy here is going to be very similar to how type
# checking works. Recall, in type checking, there was a context
# and functions like this:
#
#    def check(node, context):
#        ...
#
# It's going to be almost exactly the same idea here. You'll make a
# special LLVMContext class.  Inside that class, you'll include
# the usual details such as the environment, but also set up
# objects related to LLVM generation. For example:
#
#    class LLVMContext:
#        def __init__(self):
#            # Tracking of variables (similar to type-checking)
#            self.env = { }
#
#            # LLVM Code generation
#            self.module = ir.Module('wabbit')
#            self.function = ir.Function(self.module,
#                                        ir.FunctionType(VoidType(), []),
#                                        name='main')
#            self.block = self.function.append_basic_block()
#            self.builder = ir.IRBuilder(self.block)
#
# Subsequent code generation will primarily interact with the "builder"
# object.   For example,
#
#    def generate(node, context):
#        if isinstance(node, Integer):
#             return ('int', ir.Constant(int_type, int(node.value)))
#
#        elif isinstance(node, BinOp):
#            left_type, left_val = generate(node.left, context)
#            right_type, right_val = generate(node.right, context)
#            if left_type == 'float':
#                if node.op == '+':
#                    return ('float', context.builder.fadd(left_val, right_val))
#                ...
#            elif left_type == 'int':
#                if node.op == '+':
#                    return ('int', context.builder.add(left_val, right_val))
#            ...
#
# Unlike code for a stack machine, LLVM is based on registers.  Each operation
# needs to return a type along with the result "register."   In the above
# code, carefully notice how types and values are being used together in the
# various operations.  For example:
#
#           left_type, left_var = generate(node.left, context)
#
# On the surface, this looks very similar to the interpreter that you
# wrote.  However, LLVM is not an interpreter. It is a code generator.
# The "left_var" in this example is the location where a value was
# placed during code generation.  LLVM is not actually running the code.
# 
# Again, it's critical to read the LLVM tutorial at docs/LLVM_Tutorial.md.
# Also, there are some notes about LLVM control-flow at docs/Control-Flow.md.  

from llvmlite import ir
from .model import *

# Define LLVM types corresponding to Wabbit types
int_type = ir.IntType(32)
float_type = ir.DoubleType()
bool_type = ir.IntType(1)
char_type = ir.IntType(8)
void_type = ir.VoidType()

# Mapping of Wabbit types to LLVM types
_typemap = {
    'int': int_type,
    'float': float_type,
    'bool': bool_type,
    'char': char_type,
    }

# The LLVM module/environment hat Wabbit is populating
class LLVMContext:
    def __init__(self):
        self.env = { }
        self.module = ir.Module('wabbit')
        self.function = ir.Function(self.module,
                                    ir.FunctionType(void_type, []),
                                    name='main')
        self.block = self.function.append_basic_block('entry')
        self.builder = ir.IRBuilder(self.block)

        # Declaration of runtime functions (see runtime.c)
        self._printi = ir.Function(self.module,
                                   ir.FunctionType(void_type, [int_type]),
                                   name='_printi')
        self._printf = ir.Function(self.module,
                                   ir.FunctionType(void_type, [float_type]),
                                   name='_printf')
        self._printb = ir.Function(self.module,
                                   ir.FunctionType(void_type, [bool_type]),
                                   name='_printb')
        self._printc = ir.Function(self.module,
                                   ir.FunctionType(void_type, [char_type]),
                                   name='_printc')

    def __str__(self):
        return str(self.module)
    
    
# Top-level function
def generate_program(program):
    context = LLVMContext()
    generate(program.model, context)
    context.builder.ret_void()
    return str(context)

# Internal function to to generate code for each node type
def generate(node, context):
    if isinstance(node, Integer):
        return ('int', ir.Constant(int_type, int(node.value)))

    elif isinstance(node, PrintStatement):
        ty, var = generate(node.eval, context)
        if ty == 'int':
            context.builder.call(context._printi, [var])
        return None

    else:
        raise RuntimeError(f"Can't generate code for {node}")

# Sample main program that runs the compiler
def main(filename):
    from .parse import parse_file
    from .typecheck import check_program

    program = parse_file(filename)
    if check_program(program):
        code = generate_program(program)
        with open('out.ll', 'w') as file:
            file.write(code)
        print('Wrote out.ll')

if __name__ == '__main__':
    import sys
    main(sys.argv[1])



