# wvm.py   (Wabbit Virtual Machine)
#
# As a first compiler target, you're going to make your compiler target
# The Wabbit Virtual Machine (WVW). The WVM is meant to loosely mimic the
# behavior of a real CPU, but is simplified in that it's based on a
# stack architecture.  It will look a bit like the earlier "metal"
# project except that you don't have to worry about registers.  In that
# sense, it's probably a bit simpler.
#
# There are four distinct stages to completing this project
#
# Part 1: Evaluation of expressions.  In the first part, you'll
#         evaluate simple math expressions and relations.
#
# Part 2: Memory. You need to use load/store instructions to make
#         variables work.
#
# Part 3: Control flow.  You need to make conditionals and 
#         looping constructs work.
#
# Part 4: Functions. You need to implement support for
#         function calls.  For functions, you need to
#         worry about the distinction between local and global
#         variables.
#
# The machine itself consists of two expression stacks, one for
# integer operations and one for floating point-point operations.
# This loosely mimics the fact that actual hardware has separate
# instructions and registers for such types.
#
#      ('IPUSH', value)      # Push a value on the integer stack
#      ('IPOP',)             # Pop a value from the integer stack (discarded)
#      ('IADD',)             # Integer add
#      ('ISUB',)             # Integer sub
#      ('IMUL',)             # Integer mul
#      ('IDIV',)             # Integer div
#      ('OR',)               # Bitwise-or
#      ('AND',)              # Bitwise-and
#      ('XOR',)              # Bitwise-xor
#      ('ICMP', op)          # Integer compare. op is '==','!=','<','>','<=','>='
#      ('ITOF',)             # Convert an integer to a float
#
#      ('FPUSH', value)      # Push a value on the float stack
#      ('FPOP',)             # Pop a value from the float stack (discarded)
#      ('FADD',)             # Floating point add
#      ('FSUB',)             # Floating point sub
#      ('FMUL',)             # Floating point mul
#      ('FDIV',)             # Floating point div
#      ('FCMP', op)          # Floating point compare. op is '==','!=','<','>','<=','>='
#      ('FTOI',)             # Convert a float to an integer
#
# As an example of using these instructions, here is the instruction
# stream for computing 2 + 3 * 4
#
#      ('IPUSH', 2)
#      ('IPUSH', 3)
#      ('IPUSH', 4)
#      ('IMUL',)
#      ('IADD',)
#
# There are instructions to load/store global variables. n is an integer index
# that represents a storage slot.
#
#      ('ILOAD_GLOBAL', n)   # Push globals[n] on int stack
#      ('ISTORE_GLOBAL', n)  # Save top of int stack in globals[n]
#      ('FLOAD_GLOBAL', n)   # Push globals[n] on float stack
#      ('FSTORE_GLOBAL', n)  # Save top of float stack in globals[n]
#
# There are instructions to load/store local variables. n is an integer index
# that represents a storage slot in the function activation frame.
#
#      ('ILOAD_LOCAL', n)    # Push locals[n] on int stack
#      ('ISTORE_LOCAL', n)   # Save top of int stack in locals[n]
#      ('FLOAD_LOCAL', n)    # Push locals[n] on float stack
#      ('FSTORE_LOCAL', n)   # Save top of float stack in locals[n]
#
# There are three instructions related to control-flow
#
#      ('LABEL', name)       # Declares a label (NOP)
#      ('GOTO', name)        # Unconditionally jump to label name
#      ('BZ', name)          # Jump to label name if top of int stack is zero
#
# There are two instructions related to subroutines and function calls.
# 
#      ('CALL', name)        # Call name as a subroutine. Inputs must be on stack.
#      ('RET', )             # Return from subroutine. Result is on stack.
#
# These are different than normal control-flow in that they also manage the
# function call stack.  Each 'CALL' instruction creates a new stack frame in
# which to store local variables.  The 'RET' instruction destroys the current
# stack frame and returns to the instruction immediately following the
# associated 'CALL' instruction.
#
# There are instructions related to output
#
#      ('IPRINT',)           # Print and consume integer on top of integer stack
#      ('FPRINT',)           # Print and consume float on top of float stack
#      ('BPRINT',)           # Print an integer representing a boolean.
#      ('CPRINT',)           # Print integer on top of stack as a character
#
# The output instructions are kind of a hack. A real CPU wouldn't have I/O
# instructions, but in order to make Wabbit I/O work, we've got to have
# something to do it.  This works fine for now.

import array

class WVM:
    def __init__(self):
        self.pc = 0
        self.istack = array.array('i')
        self.fstack = array.array('d')
        self.globals = { }
        self.stack = [{ }]
        self.labels = { }

    def run(self, instructions):
        self.pc = 0
        self.running = True
        # Determine the instruction index for labels
        self.labels = { op[1]: n for n, op in enumerate(instructions)
                        if op[0] == 'LABEL' }
        while self.running:
            op, *args = instructions[self.pc]
            self.pc += 1
            getattr(self, op)(*args)

    # Integer operations
    def IPUSH(self, value):
        self.istack.append(value)

    def IPOP(self):
        return self.istack.pop()

    def IADD(self):
        right = self.IPOP()
        left = self.IPOP()
        self.IPUSH(left + right)

    def ISUB(self):
        right = self.IPOP()
        left = self.IPOP()
        self.IPUSH(left - right)

    def IMUL(self):
        right = self.IPOP()
        left = self.IPOP()
        self.IPUSH(left * right) 

    def IDIV(self):
        right = self.IPOP()
        left = self.IPOP()
        self.IPUSH(left // right)

    def AND(self):
        right = self.IPOP()
        left = self.IPOP()
        self.IPUSH(left & right)

    def OR(self):
        right = self.IPOP()
        left = self.IPOP()
        self.IPUSH(left | right)

    def XOR(self):
        right = self.IPOP()
        left = self.IPOP()
        self.IPUSH(left ^ right)
        
    def ICMP(self, op):
        right = self.IPOP()
        left = self.IPOP()
        if op == '<':
            self.IPUSH(left < right)
        elif op == '<=':
            self.IPUSH(left <= right)            
        elif op == '>':
            self.IPUSH(left > right)            
        elif op == '>=':
            self.IPUSH(left >= right)            
        elif op == '==':
            self.IPUSH(left == right)            
        elif op == '!=':
            self.IPUSH(left != right)            
            
    def ITOF(self):
        self.FPUSH(float(self.IPOP()))
        
    # Floating point operations

    def FPUSH(self, value):
        assert isinstance(value, float)
        self.fstack.append(value)

    def FPOP(self):
        return self.fstack.pop()

    def FADD(self):
        right = self.FPOP()
        left = self.FPOP()
        self.FPUSH(left + right)

    def FSUB(self):
        right = self.FPOP()
        left = self.FPOP()
        self.FPUSH(left - right)

    def FMUL(self):
        right = self.FPOP()
        left = self.FPOP()
        self.FPUSH(left * right)

    def FDIV(self):
        right = self.FPOP()
        left = self.FPOP()
        self.FPUSH(left / right)

    def FCMP(self, op):
        right = self.FPOP()
        left = self.FPOP()
        # Note: result of a comparison is an integer/bool
        if op == '<':
            self.IPUSH(left < right)
        elif op == '<=':
            self.IPUSH(left <= right)            
        elif op == '>':
            self.IPUSH(left > right)            
        elif op == '>=':
            self.IPUSH(left >= right)            
        elif op == '==':
            self.IPUSH(left == right)            
        elif op == '!=':
            self.IPUSH(left != right)            

    def FTOI(self):
        self.IPUSH(int(self.FPOP()))
        
    # Global variables
    def ILOAD_GLOBAL(self, slot):
        assert isinstance(slot, int), slot
        self.IPUSH(self.globals[slot])

    def FLOAD_GLOBAL(self, slot):
        assert isinstance(slot, int), slot        
        self.FPUSH(self.globals[slot])

    def ISTORE_GLOBAL(self, slot):
        assert isinstance(slot, int), slot        
        self.globals[slot] = self.IPOP()

    def FSTORE_GLOBAL(self, slot):
        assert isinstance(slot, int), slot        
        self.globals[slot] = self.FPOP()

    # Local variables
    def ILOAD_LOCAL(self, slot):
        assert isinstance(slot, int), slot        
        self.IPUSH(self.stack[-1][slot])

    def FLOAD_LOCAL(self, slot):
        assert isinstance(slot, int), slot        
        self.FPUSH(self.stack[-1][slot])

    def ISTORE_LOCAL(self, slot):
        assert isinstance(slot, int), slot        
        self.stack[-1][slot] = self.IPOP()

    def FSTORE_LOCAL(self, slot):
        assert isinstance(slot, int), slot        
        self.stack[-1][slot] = self.FPOP()
        
    # Control flow
    def HALT(self):
        self.running = False
        
    def LABEL(self, name):
        pass

    def GOTO(self, name):
        self.pc = self.labels[name]

    def BZ(self, name):
        if self.IPOP() == 0:
            self.pc = self.labels[name]

    def CALL(self, name):
        self.stack.append({})
        self.stack[-1]['return'] = self.pc
        self.pc = self.labels[name]

    def RET(self):
        self.pc = self.stack[-1]['return']
        self.stack.pop()

    # Output
    def IPRINT(self):
        print(self.IPOP())

    def FPRINT(self):
        print(self.FPOP())

    def BPRINT(self):
        print('true' if self.IPOP() else 'false')
        
    def CPRINT(self):
        print(chr(self.IPOP()), end='')

# -----------------------------------------------------------------------------
# Compile to the WVM
#
# To compile Wabbit to the WVW, you're going to write code that looks similar
# to what you've implemented in the interpreter and the type-checker
# project.   That is, you're going to have some kind of high-level case
# analysis that handles different kinds of model nodes.
#
# The output of this step should be a single Python list containing
# the instruction stream for the entire program.  If you feed this
# instruction stream to the WVM, it should run the program.
#
# You will need to convert control flow to branch and goto instructions.
# Here is an example of what that might look like:
#
#  // Wabbit
#  if x < 0 {
#      print 1;
#  } else {
#      print 2;
#  }
#
#  code = [
#       ('ILOAD_GLOBAL', x_slot),   # "x_slot" needs to be determined.
#       ('IPUSH', 0),
#       ('ICMP', '<'),
#       ('BZ', 'L2'),
#       ('LABEL', 'L1'),
#       ('IPUSH', 1),
#       ('IPRINT',),
#       ('GOTO', 'L3'),
#       ('LABEL', 'L2'),
#       ('IPUSH', 2),
#       ('IPRINT',)
#       ('GOTO', 'L3'),
#       ('LABEL', 'L3'),
#       ...
# ]
#
# The LABEL instructions use label names that must be uniquely
# generated (i.e., each if-statement would use a unique set of
# labels).
#
# One slightly tricky part of code generation concerns functions.
# Each function should be given its own label. For example:
#
#     func square(x int) int {
#         return x*x;
#     }
#
# Turns into something like this:
#
#     code = [
#              ...
#              ('LABEL', 'square'),
#              ...  # instructions
#              ('RET',),
#              ...
#            ]
#
# Arguments to the function should be assumed to be located on the
# integer/float stacks respectively.   You'll need to figure out
# how to take these arguments and store them in local variables.
# You'll need to figure out how to place functions into the output code
# while making everything else work. There's some amount of book-keeping
# involved. 

from .model import *

# Class that holds the environment and other information related to
# code generation.
class WVMContext:
    def __init__(self):
        self.env = { }
        self.code = [ ]
        
# Top-level function used to generate code.
def generate_wvm(program):
    context = WVMContext()
    generate(program.model, context)
    context.code.append(('HALT',))
    return context.code

# Internal function used to generate code.  As with other parts of the compiler,
# it's necessary to track type information so that correct instructions can
# generated.  Given that the pattern of propagating types has repeated itself
# severa times now, it might be an interesting thought experiment to think
# of ways to avoid that--or to reuse prior work. 

def generate(node, context):
    if isinstance(node, Integer):
        context.code.append(('IPUSH', int(node.value)))
        return 'int'

    elif isinstance(node, Float):
        context.code.append(('FPUSH', float(node.value)))
        return 'float'

    elif isinstance(node, PrintStatement):
        valtype = generate(node.eval, context)
        if valtype == 'int':
            context.code.append(('IPRINT',))
        elif valtype == 'float':
            context.code.append(('FPRINT',))
        
    else:
        raise RuntimeError(f"Couldn't generate {node}")

# Sample main program
def main(filename):
    from .typecheck import check_program
    from .parse import parse_file
    program = parse_file(filename)
    if check_program(program):
        code = generate_wvm(program)
        machine = WVM()
        machine.run(code)

if __name__ == '__main__':
    import sys
    main(sys.argv[1])

