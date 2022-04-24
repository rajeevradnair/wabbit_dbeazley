# wasm.py
#
# Generate WebAssembly from the Wabbit model.  For this, you are going
# to generate output in the WebAssembly text format (WAT).  You can
# then use tools such as "wat2wasm" to convert this to the WASM binary
# encoding.  Ultimately your compiler needs to produce a file called
# "out.wasm" that will be loaded by the corresponding script "test.js"
# (found in the top level "compilers" directory).
#
# The first part of this file talks you through the process of creating
# WebAssembly and getting things to run.  Consider it to be a tutorial
# that you should try on your own first.
#
# 1. Requirements
#
# For this part, you will need to install some dependencies. Specifically,
# a recent version of "node-js" (https://nodejs.org).  You will also need
# to install "wabt" using "npm install wabt". Of particular interest is
# the script "wat2wasm" found in "nodes_modules/wabt/bin/wat2wasm".
#
# 2. Wasm Architecture
#
# WebAssembly is a stack-based architecture.  If you want to compute 2 + 3 * 4
# the sequence of instructions will look something like this:
#
#     i32.const 2         ;; push 2
#     i32.const 3         ;; push 3
#     i32.const 4         ;; push 4
#     i32.mul             ;; 3 * 4 -> 12
#     i32.add             ;; 2 + 12 -> 14
#
# There are two fundamental types of data that will be used. "i32" is a 32-bit
# integer and "f64" is a 64-bit floating point number.   The Wabbit
# types of "int", "bool", and "char" all must map to "i32".  The Wabbit "float"
# type gets mapped to "f64".
#
# 3. High-level module.
#
# WebAssembly code is placed into a module. Here is a template of the
# format that matches up with what's required by the "test.js" file:
#
#     (module
#     ;; foreign functions (imported from JavaScript)
#     ;; See the file test.js for their implementation.
#     (import "env" "_printi" (func $_printi ( param i32 )))
#     (import "env" "_printf" (func $_printf ( param f64 )))
#     (import "env" "_printb" (func $_printb ( param i32 )))
#     (import "env" "_printc" (func $_printc ( param i32 )))
#
#     (func $main (export "main")
#        ;; instructions go here
#     )  ;; end main
#     )  ;; end module
#
# Text precedure by ";;" is a comment and is not required. 
#
# 4. Compilation process
#
# Your compiler should produce a file "out.wat".  That file needs to be
# processed using the script "wat2wasm" to create "out.wasm". Here
# what it might look like with all of the steps performed manually:
#
#    bash % python3 -m wabbit.wasm prog.wb
#    Wrote 'out.wat'
#    bash % node_modules/wabt/bin/wat2wasm out.wat
#    bash % node test.js
#    ... program output ...
#    bash %
#
# Try creating an "out.wat" file by hand (copying the code above into
# it), and run the "wat2wasm" and "node" commands.  You should get no
# errors and no output.  This will let you know that the tool-chain is
# probably working.
#
# 5. "Hello World" Example
#
# You will start out by putting further instructions into the main()
# function.  Here is an example that prints "42" to the screen.
#
#    (func $main (export "main")
#         i32.const 42
#         call $_printi
#    )
#
# Add these instructions to out.wat and use wat2wasm to create out.wasm.
# Run "node test.js" and verify that 42 gets printed to the screen.
#
# 5.  Mapping of Wabbit Features to Wasm
#
# The following example shows how various wabbit features get mapped
# to WebAssembly.  It is mostly straightforward--you need to produce output
# that follows this general template.  Copy this to "out.wat" and experiment
# with it.
#
#      (module
#      (import "env" "_printi" (func $_printi ( param i32 )))
#      (import "env" "_printf" (func $_printf ( param f64 )))
#      (import "env" "_printb" (func $_printb ( param i32 )))
#      (import "env" "_printc" (func $_printc ( param i32 )))
#
#      ;; Global variables are declared outside of the main function here
#    
#      ;; const pi = 3.14159;
#      (global $pi (mut f64) (f64.const 0.0))
#
#      ;; var x int = 2 + 3;
#      (global $x (mut i32) (i32.const 0))
#     
#      (func $main (export "main")
#         ;; Initialization of "pi" global 
#         f64.const 3.14159
#         global.set $pi
#
#         ;; Initialization of "x" global
#         i32.const 2
#         i32.const 3
#         i32.add
#         global.set $x
#
#         ;; print x;
#         global.get $x
#         call $_printi
#
#         ;; if x < 3 { print 1; } else { print 2;}
#         global.get $x
#         i32.const 3
#         i32.lt_s
#         if
#            i32.const 1
#            call $_printi
#         else
#            i32.const 2
#            call $_printi
#         end
#
#         ;; while x > 0 {
#         ;;    print x;
#         ;;    x = x - 1;
#         ;; }
#         block $loop_exit
#             loop $loop_test
#                  global.get $x
#                  i32.const 0
#                  i32.le_s   ;; Note: logic is reversed to test for loop "exit"
#                  br_if $loop_exit
#                  global.get $x
#                  call $_printi
#                  global.get $x
#                  i32.const 1
#                  i32.sub
#                  global.set $x
#                  br $loop_test
#             end
#         end
#      )  ;; end main
#      )  ;; end module
#
# 6. Useful Instructions
#
# Integer operations
#
#     i32.const value      ;; Constant value
#     i32.add              ;; +
#     i32.sub              ;; -
#     i32.mul              ;; *
#     i32.div_s            ;; / (signed division)
#     i32.lt_s             ;; < (signed)
#     i32.le_s             ;; <= (signed)
#     i32.gt_s             ;; > (signed)
#     i32.ge_s             ;; >= (signed)
#     i32.eq               ;; ==
#     i32.ne               ;; !=
#     i32.and              ;; &&
#     i32.or               ;; ||
#     i32.xor              ;; Exclusive-OR
#     i32.trunc_s/f64      ;; Convert f64 to i32
#
# Floating point operations
#
#     f64.const value      ;; Constant value
#     f64.add              ;; +
#     f64.sub              ;; -
#     f64.mul              ;; *
#     f64.div              ;; / 
#     f64.lt               ;; < 
#     f64.le               ;; <= 
#     f64.gt               ;; >
#     f64.ge               ;; >=
#     f64.eq               ;; ==
#     f64.ne               ;; !=
#     f64.convert_s/i32    ;; Convert i32 to f64
#
# Global variable get/set
#
#     (global $iname (mut i32) (i32.const 0))     ;; Declare an i32
#     (global $fname (mut f64) (f64.const 0.0))   ;; Declare an f64
#     global.get $var                             ;; Get a value (put on stack) 
#     global.set $var                             ;; Set a value (store from stack)
#
# Control flow
#
#      if ... else ... end   ;; Conditional
#      block $label ... end  ;; Code block
#      loop $label ... end   ;; Loop block
#      br $label             ;; Unconditional break from enclosing block/loop label
#      br_if $label          ;; Conditional break from enclosing block/loop label
#      call $func            ;; Call function
#      return                ;; Return from function
#
# Control flow in Wasm is a little strange.   It's probably better to think of it
# in terms of "break" and "continue" statements from looping.   Basically, the
# "br" and "br_if" instructions act like a "break" statement that escape out of
# the indicated block.   For example:
#
#    block $a
#        block $b
#        ...
#        br $a          ;; Jumps to (1) below --+
#        ...                                    |
#        end  ;; $b                             |
#    end ;; $a                                  |
#    instructions       ;; (1)   <--------------|
#    ...
#
# However, loop blocks work a bit different. With a loop block, the
# "br" and "br_if" instructions jump back to the top of the loop.
#
#    block $a
#       loop $b    ;; (1) <-----------------+
#         ...                               |
#         br_if $a ;; Jumps to (2) below ---|---+
#         ...                               |   |
#         br $b    ;; Jumps to (1) above ---+   |
#         ...                                   |
#       end ;; $b                               |
#    end ;; $a                                  |
#    instructions  ;; (2) <---------------------+
#
# Using different combinations of "loop", "if", and "block" constructs,
# you can make the program jump around.  

# 7. Functions.
#
# Here's how a Wabbit function maps to a WebAssembly function.
#
#    // Wabbit
#    func add(x int, y int) int {
#         return x + y;
#    }
#
# Corresponding Wasm
#
#   (func $add (export "add")
#       (param $x i32)
#       (param $y i32)
#       (result i32)
#       (local $return i32)      ;; Storage of return value
#       block $return
#          local.get $x
#          local.get $y
#          i32.add
#          local.set $return     ;; Store return result
#          br $return            ;; Branch to the function end
#       end
#       local.get $return
#    )
#
# To call this function from elsewhere, use instructions like this.
# For example, to call add(2, 3)
#
#     i32.const 2    ;; push arguments on stack
#     i32.const 3
#     call $add
#
# 8. Implementation strategy
# 
# The overall strategy here is going to be very similar to how type
# checking works.  Recall, in type checking, there was a context
# and a top-level function:
#
#    def check(node, context):
#        if isinstance(node, Integer):
#            ...
#        elif isinstance(node, Float):
#            ...
#
# It's going to be almost exactly the same idea here. Your context
# will need to hold some information about the WebAssembly code being
# generated.  This can be as simple as storing plain-text.  Your context
# will still need to do some book-keeping with names, environments,
# and types as well.
#
# The code below provides a basic sketch of some parts that you should be
# able to extend.

from .model import *

# Mapping of Wabbit type names to Wasm types
_typemap = {
    'int': 'i32',
    'float': 'f64',
    'bool': 'i32',
    'char': 'i32',
    }

# Use this class to hold all WAT code related to an individual function
class WasmFunction:
    def __init__(self, name, parameters, ret_type):
        self.name = name
        self.parameters = parameters
        self.ret_type = ret_type
        self.locals = [ ]
        self.code = [ ]

    # Create a WAT version of the function source
    def as_wat(self):
        out = f'(func ${self.name} (export "{self.name}")\n'
        for parm in self.parameters:
            out += f'(param ${parm.name} {_typemap[parm.type]})\n'
        if self.ret_type:
            out += f'(result {_typemap[self.ret_type]})\n'
            out += f'(local $return {_typemap[self.ret_type]})\n'
        out += '\n'.join(self.locals)
        out += '\nblock $return\n'
        out += '\n'.join(self.code)
        out += '\nend\n'
        if self.ret_type:
            out += 'local.get $return\n'
        out += ')\n'
        return out
        
# Use this class to hold module-level information and context
class WasmContext:
    def __init__(self):
        # Storage for information on names/environments
        self.env = { }
        # _init function where global declarations/setup go
        self.function = WasmFunction('main', [], None)

        # Code making up the module contents. Will be extended by the code generator
        self.module = [ '(module'
                        '(import "env" "_printi" (func $_printi ( param i32 )))',
                        '(import "env" "_printf" (func $_printf ( param f64 )))',
                        '(import "env" "_printb" (func $_printb ( param i32 )))',
                        '(import "env" "_printc" (func $_printc ( param i32 )))' ]

    def as_wat(self):
        return '\n'.join(self.module) + '\n)\n'
    
# Top-level function for generating code from the model
def generate_program(program):
    context = WasmContext()
    generate(program.model, context)
    context.module.append(context.function.as_wat())
    return context.as_wat()

# Internal function for generating code on each node.  A few examples are provided.
def generate(node, context):
    if isinstance(node, Integer):
        context.function.code.append(f'i32.const {node.value}')
        return 'int'
    
    elif isinstance(node, PrintStatement):
        valtype = generate(node.eval, context)
        if valtype == 'int':
            context.function.code.append('call $_printi')
        return None

    elif isinstance(node, ConstDeclaration):
        valtype = generate(node.eval, context)

        # Declare a global variable (this happens at the module level)
        if valtype == 'float':
            context.module.append(f'(global ${node.name} (mut f64) (f64.const 0.0))')
        elif valtype in {'int', 'bool', 'char'}:
            context.module.append(f'(global ${node.name} (mut i32) (i32.const 0))')

        # Store the initial value in the global (happens in the main function)
        context.function.code.append(f'global.set ${node.name}')

        # Remember type information in the environment. Needed for subsequent lookups.
        context.env[node.name] = valtype
        return None

    elif isinstance(node, Name):
        valtype = context.env[node.eval]
        context.function.code.append(f'global.get ${node.eval}')
        return valtype
    
    else:
        raise RuntimeError(f"Can't generate {node}")
    
def main(filename):
    from .parse import parse_file
    from .typecheck import check_program
    program = parse_file(filename)
    if check_program(program):
        mod = generate_program(program)
        with open('out.wat', 'w') as file:
            file.write(mod)
        print("Wrote out.wat")

if __name__ == '__main__':
    import sys
    main(sys.argv[1])

        
        

    

                   
