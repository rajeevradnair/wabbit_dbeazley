# LLVM Code Generation Tutorial

This is tutorial on how to generate LLVM intermediate code.  For this
tutorial, we're going to consider the following code fragment:

```
var x int = 4;
var y int = 5;
var d int = x * x + y * y;
print d;
```

We'll see how to translate it to LLVM.  A few additional LLVM features
will be covered as well.

## LLVM Overview

LLVM is intermediate code that serves as a kind of generic machine
language that can be translated into many different targets.  LLVM is
used in a number of major projects such as the clang C/C++ compiler.
It's also used to implement various so-called JIT (Just in Time)
compilation features.

LLVM is an extremely large project that can be daunting to jump into.
However, using it in a simple manner is not so bad. To explore the
basics, we're going to use the `llvmlite` package.  This is available
in the Anaconda Python distribution so if you're using that, you
should already have it.

## LLVM Preliminaries

Your first task is to make sure Anaconda Python and the clang C/C++
compiler have been installed on your machine. 

## Hello World

The first step in using LLVM is to make a LLVM module which contains
all of the code you will be generating.  Create a file
`hellollvm.py` and put this code into it:

```
# hellollvm.py
from llvmlite import ir

mod = ir.Module('hello')
print(mod)
```

Run the program and you should get some output like this:

```
bash % python3 hellollvm.py
; ModuleID = "hello"
target triple = "unknown-unknown-unknown"
target datalayout = ""

bash %
```

The output you're seeing is LLVM low-level code--a kind of architecture
independent assembly language. At this point, it's not too
interesting.  However, let's declare a function to put in the module.
Change the program to the following to declare a function with the C
prototype `int hello()`:

```
# hellollvm.py

from llvmlite import ir

mod = ir.Module('hello')
int_type = ir.IntType(32)
hello_func = ir.Function(mod, ir.FunctionType(int_type, []), name='hello')
print(mod)
```

Running the program, you should now get the following:

```
bash % python3 hellollvm.py
; ModuleID = "hello"
target triple = "unknown-unknown-unknown"
target datalayout = ""

declare i32 @"hello"() 

bash %
```

Again, it's not too interesting yet.  However, you can see
how a function declaration was placed in the module output. The LLVM
statement `declare i32 @"hello"()` is declaring a function that
returns a 32-bit integer and takes no arguments.

Let's add some code to the function.  To do this, you first need to
create a basic block. A basic block is a container that holds
low-level instructions.  Add the following to the program:

```
# hellollvm.py

from llvmlite import ir

mod = ir.Module('hello')
int_type = ir.IntType(32)
hello_func = ir.Function(mod, ir.FunctionType(int_type, []), name='hello')
block = hello_func.append_basic_block('entry')
builder = ir.IRBuilder(block)
builder.ret(ir.Constant(ir.IntType(32), 37))
print(mod)
```

Running the program should now produce this:

```
; ModuleID = "hello"
target triple = "unknown-unknown-unknown"
target datalayout = ""
    
define i32 @"hello"() 
{
entry:
  ret i32 37
}
```

There you are---a complete LLVM function that does nothing but return
the value 37. Now, a question arises: How do you go about getting it to run?

## Compilation to a Standalone Executable

If you want to run your LLVM generated code, one approach is to feed it
to a LLVM-based compiler such as `clang`.  Save your generated
code to a file `hello.ll`:

```
bash % python3 hellollvm.py > hello.ll
bash % 
```

Now, write a short C program to bootstrap the function:

```
/* main.c */
#include <stdio.h>

extern int hello(); 

int main() {
    printf("hello() returned %i\n", hello());
}
```

Compile this program together with `hello.ll` to make an executable:

```
bash % clang main.c hello.ll
bash % ./a.out
hello() returned 37
bash %
```

This basic technique for invoking your code and creating stand-alone
programs will be useful for testing and development.  You also get the
advantage of being able to use C library functions such as
`printf()`.  Without this, you'd have to figure out how to perform
I/O directly using low-level LLVM instructions--which would not be
fun.

## Just in Time Compilation

In our example, we are creating LLVM instructions, writing them to a
file, and using the `clang` compiler to produce an executable. 
It's possible that this won't work due to the local setup on
your machine (maybe you don't have clang installed correctly).
One feature of LLVM is that it can compile it's own code to executable
machine instructions without ever going to a file or using clang.  
You can do this entirely in Python and have Python call the resulting
function.

This part is rather tricky and obscure, but add the following code to
`hellollvm.py`:

```
# hellollvm.py 

... keep earlier LLVM example here ...

def run_jit(module):
    import llvmlite.binding as llvm

    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    target = llvm.Target.from_default_triple()
    target_machine = target.create_target_machine()
    compiled_mod = llvm.parse_assembly(str(module))
    engine = llvm.create_mcjit_compiler(compiled_mod, target_machine)

    # Look up the function pointer (a Python int)
    func_ptr = engine.get_function_address("hello")

    # Turn into a Python callable using ctypes
    from ctypes import CFUNCTYPE, c_int
    hello = CFUNCTYPE(c_int)(func_ptr)

    res = hello()
    print('hello() returned', res)

# Run it!
run_jit(mod)
```

If you run this, you should see the program run the code, and
produce output such as this:

```
bash % python3 hellollvm.py
hello() returned 37
bash %
```

This version runs entirely inside an active Python interpreter process. 
If you can't get clang to work, you can always use this as a fallback.

## Local Variables and Math Operations

To do more with LLVM, you need to use more instructions on the
`builder` object in the example.   To declare a local variable "x",
you use this method:

```
x = builder.alloca(int_type, name="x")
```

To load and store values, you use these instructions:

```
r = builder.load(x)        # Load a value from x into r
builder.store(r, x)        # Store r into y
```

To perform arithmetic, you use instructions such as these:

```  
r3 = builder.add(r1, r2)   # r3 = r1 + r2
r3 = builder.mul(r1, r2)   # r3 = r1 + r2
```

Here is an example that implements the program given at the start
of this exercise:

```
# hellollvm.py
from llvmlite import ir

mod = ir.Module('hello')
int_type = ir.IntType(32)

hello_func = ir.Function(mod, ir.FunctionType(int_type, []), name='hello')
block = hello_func.append_basic_block('entry')
builder = ir.IRBuilder(block)

x = builder.alloca(int_type, name='x')
y = builder.alloca(int_type, name='y')
builder.store(ir.Constant(int_type, 4), x)
builder.store(ir.Constant(int_type, 5), y)
r1 = builder.load(x)
r2 = builder.mul(r1, r1)
r3 = builder.load(y)
r4 = builder.mul(r3, r3)
r5 = builder.add(r2, r4)
d = builder.alloca(int_type, name='d')
builder.store(r5, d)
builder.ret(builder.load(d))

print(mod)
```

An important thing about LLVM is that it is based
on registers and Single Static Assignment (SSA).  Basically, every operation
produces a new variable that can only be assigned once.  It also requires explicit
load/store instructions to go between local variables and registers.  In the 
above example, you can't do an instruction such as `builder.add(x, y)` between
local variables.  You have to load the variables into registers first and
perform the instruction on the registers.

Try compiling the above program and running you code again:

```
bash % python3 hellollvm.py > hello.ll
bash % clang main.c hello.ll
bash % ./a.out
hello() returned 41
bash %
```

## Functions with Arguments

Let's make a more interesting function.  This function takes two
arguments `x` and `y` and computes the value `x**2 + y**2`.  To
do this, we're going to follow similar steps as above. First, declare
the function, add a basic block, and make a new builder.  Once the
builder is obtained, we'll create some instructions to compute and
return the result. Add the following code to your `hellollvm.py`
program:

```
# hellollvm.py
...

# A user-defined function
from llvmlite import ir

ty_double = ir.DoubleType()
dsquared_func = ir.Function(mod, 
                         ir.FunctionType(ty_double, [ty_double, ty_double]), 
                         name='dsquared')
block = dsquared_func.append_basic_block('entry')
builder = ir.IRBuilder(block)

# Get the function args
x, y = dsquared_func.args

# Compute temporary values for x*x and y*y
xsquared = builder.fmul(x, x)
ysquared = builder.fmul(y, y)

# Sum the values and return the result
d2 = builder.fadd(xsquared, ysquared)
builder.ret(d2)

# Output the final module
print(mod)
```

One thing to notice is that you use the builder to carry out the steps
needed to perform the calculation that you're trying to perform. Python
variables such as `x`, `xsquared`, and `d2` are being used to
hold intermediate results.

If you run this program, you should output similar to the following:

```
; ModuleID = "hello"
...

define double @"dsquared"(double %".1", double %".2") 
{
entry:
  %".4" = fmul double %".1", %".1"
  %".5" = fmul double %".2", %".2"
  %".6" = fadd double %".4", %".5"
  ret double %".6"
}
```

To test it, modify the C bootstrap code as follows:

```
/* main.c */
#include <stdio.h>

extern int hello();
extern double dsquared(double, double);

int main() {
  printf("Hello returned: %i\n", hello());
  printf("dsquared(3, 4) = %f\n", dsquared(3.0, 4.0));
}
```

Compile as follows:

```  
bash % python3 hellollvm.py > hello.ll
bash % clang main.c hello.ll
bash % ./a.out
Hello returned: 41
dsquared(3, 4) = 25.000000
bash %
```

## Calling an external function

Even though you're emitting low-level assembly code, there's no need
to completely reinvent the wheel from scratch.  One problem concerns
printing.  In our IR code, there is an instruction to print a value
to the screen.  How do you do that in LLVM?  The short answer is that
you don't (well, unless you're some kind of masochist).  You do printing
in C.  Make a new file `runtime.c` and put a
a `_print_int()` function in it like this:

```
/* runtime.c */
#include <stdio.h>

void _print_int(int x) {
    printf("out: %i\n", x);
}
```

Now, suppose you wanted to call that function from LLVM.  To do it,
you need to declare it:

```
# hellollvm.py
...
from llvmlite import ir

void_type = ir.VoidType()
int_type = ir.IntType(32)

_print_int = ir.Function(mod, 
                     ir.FunctionType(void_type, [int_type]), 
                     name='_print_int')
```

To call the function, you use the `builder.call()` instruction:

```
r2 = builder.call(_print_int, [r1])
```

Change your `hellollvm.py` program so that it looks like this:

```
# hellollvm.py

from llvmlite import ir

mod = ir.Module('hello')

int_type = ir.IntType(32)
void_type = ir.VoidType()

_print_int = ir.Function(mod, 
                      ir.FunctionType(void_type, [int_type]), 
                      name='_print_int')

hello_func = ir.Function(mod, ir.FunctionType(int_type, []), name='hello')
block = hello_func.append_basic_block('entry')
builder = ir.IRBuilder(block)

x = builder.alloca(int_type, name='x')
y = builder.alloca(int_type, name='y')
builder.store(ir.Constant(int_type, 4), x)
builder.store(ir.Constant(int_type, 5), y)
t1 = builder.load(x)
t2 = builder.load(x)
t3 = builder.mul(t1, t2)
t4 = builder.load(y)
t5 = builder.load(y)
t6 = builder.mul(t4, t5)
t7 = builder.add(t3, t6)
d = builder.alloca(int_type, name='d')
builder.store(t7, d)
builder.call(_print_int, [builder.load(d)])     # Call _print_int()
builder.ret(ir.Constant(int_type, 37))             # Return 37
print(mod)
```

Compile and run (note inclusion of `runtime.c`):

```
bash % python3 hellollvm.py > hello.ll
bash % clang main.c runtime.c hello.ll
bash % ./a.out
out: 41
hello() returned 41
bash %
```

Notice that there is output from the `_print_int()` function as well as
the return value from the `hello()` function itself.  

As an aside, you can implement almost anything that you want in C and
link it as library code into your output assembly code.  Printing,
memory access, and all sorts of other things could potentially be
written in this way.  You'll have to do some of this in the project.

## Global Variables and State

You might want to define a variable that keeps its state.  Let's make
a global variable `x`:

```
# hellollvm.py
...
from llvmlite import ir
x_var = ir.GlobalVariable(mod, ty_double, 'x')
x_var.initializer = ir.Constant(ty_double, 0.0)
```

Now, let's write a function that increments the variable and 
prints its new value.  To do this, you use `load` and `store`
instructions to manipulate the variable state:

```
# hellollvm.py
...

from llvmlite import ir

incr_func = ir.Function(mod, 
                     ir.FunctionType(ir.VoidType(), []), 
                     name='incr')
block = incr_func.append_basic_block('entry')
builder = ir.IRBuilder(block)
tmp1 = builder.load(x_var)
tmp2 = builder.fadd(tmp1, ir.Constant(ty_double, 1.0))
builder.store(tmp2, x_var)
builder.ret_void()
```

Modify the `main.c` file as follows:

```
/* main.c */
#include <stdio.h>

extern int hello();
extern double dsquared(double, double);
extern double x;
extern void incr();

int main() {
  printf("Hello returned: %i\n", hello());
  printf("dsquared(3, 4) = %f\n", dsquared(3.0, 4.0));
  printf("x is %f\n", x);
  incr();
  printf("x is now %f\n", x);
}
```

Compile and run the program again::

```
bash % python3 hellollvm.py > hello.ll
bash % clang main.c hello.ll -lm
bash % ./a.out
out: 41
Hello returned: 41
dsquared(3, 4) = 25.000000
x is 0.000000
x is now 1.000000
bash %
```

## Compiling to LLVM

In building your compiler, you'll need to figure out how to translate
programs into the appropriate low-level LLVM operations.  
You need to keep track of variables. You need some way to keep track of LLVM values.

## A LLVM Mini-Reference

This section aims to provide a mini-reference for using LLVM in the
next part of the project.   It summarizes some of the critical bits.

For creating LLVM code, use the following import:

```
from llvmlite import ir
```

All LLVM code is placed in a module.  You create one like this:

```
mod = ir.Module("modname")
```

You declare functions like this:

```
func = ir.Function(mod, 
                ir.FunctionType(rettype, [argtypes]),
                name="funcname")
```

The following basic datatypes are used heavily in declarations:

``` 
ir.IntType(32)             # A 32-bit integer
ir.DoubleType()            # A double-precision float
ir.IntType(1)              # A 1-bit boolean
ir.IntType(8)              # An 8-bit byte
```

It is usually easier to make aliases for the types:

```
int_type = ir.IntType(32)
float_type = ir.DoubleType()
```

To define constants corresponding to the above types, do this:

```  
c = ir.Constant(int_type, value)
d = ir.Constant(float_type, value)
```

To start adding code to a function, you must add a basic block
and create a builder.  For example:

```
block = func.append_basic_block('entry')
builder = ir.IRBuilder(block)
```

Builder objects have a variety of useful methods for adding
instructions.  These include:

```
# Returning values
builder.ret(value)            
builder.ret_void()            

# Integer math
result = builder.add(left, right)
result = builder.sub(left, right)
result = builder.mul(left, right)
result = builder.sdiv(left, right)    

# Integer Comparison
builder.icmp_signed('<', left, right)   # left < right
builder.icmp_signed('<=', left, right)  # left <= right
builder.icmp_signed('>', left, right)   # left > right
builder.icmp_signed('>=', left, right)  # left >= right
builder.icmp_signed('==', left, right)  # left == right
builder.icmp_signed('!=', left, right)  # left != right

# Floating point math
result = builder.fadd(left, right)
result = builder.fsub(left, right)
result = builder.fmul(left, right)
result = builder.fdiv(left, right)

# Float point compares:

builder.fcmp_ordered('<', left, right)  # left < right
builder.fcmp_ordered('<=', left, right) # left <= right
builder.fcmp_ordered('>', left, right)  # left > right
builder.fcmp_ordered('>=', left, right) # left >= right
builder.fcmp_ordered('==', left, right) # left == right
builder.fcmp_ordered('!=', left, right) # left != right

# Comparison operations always return `IntType(1)`.  Use
# this to cast to a different integer size:
builder.zext(value, IntType(32))     # Zero-extend value to 32-bits

# To truncate an integer down to a bool use
builder.trunc(value, IntType(1))     # Truncate an int to a bool

# For boolean operations, use the following
builder.and_(left, right)             # left && right
builder.or_(left, right)              # left || right
builder.xor(left, right)              # left ^ right (exclusive-or)

# Function call
result = builder.call(func, args)
```

When using the builder, it is important to emphasize that you must
save the results of the above operations and use them in subsequent
calls.  For example:

```
t1 = builder.fmul(a, b)
t2 = builder.fmul(c, d)
t3 = builder.fadd(t1, t2)
...
```

To declare a local variable do something like this:

```
name_var = builder.alloca(int_type, name='varname')
```

To declare a global variable do something like this:

```
x_var = ir.GlobalVariable(mod, ty_double, 'x')
x_var.initializer = ir.Constant(ty_double, 0.0)
```

To access either kind of variable, use load and store instructions:

```
tmp = builder.load(name_var)
builder.store(tmp, name_var)
```
