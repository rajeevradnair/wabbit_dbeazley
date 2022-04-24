# A Guide to Control Flow

A sequence of simple operations where there is a single entry and
exit point with no changes in control flow is known as a basic block.
For example:

```
// Example of a basic block
a = 2;
b = 3;
c = a + b;
```

Programs tend to consist of many basic blocks joined together
by various control-flow statements such as conditions and loops.
For example:

```
a = 2;
b = 3;
if a < b {
    c = a + b;
} else {
    c = a - b;
}
print c;
```

In this code, there are four basic blocks:

```
b1:    a = 2;
       b = 3;
       a < b;

b2:    c = a + b;

b3:    c = a - b;

b4:    print(c);
```

The conditional causes the code to branch to either block b2 or block b3.  
One way to view this is as a control-flow graph:

```
                 |--------------|
                 |  b1:  a = 2; |
                 |       b = 3; |
                 |       a < b; |
                 |--------------|
               /                 \
              / True         False\
             /                     \
    |------------------|       |-----------------|
    |  b2:  c = a + b; |       |  b3: c = a - b; |
    |------------------|       |-----------------|
                 \              /
                  \            /
                  |--------------|
                  | b4: print(c);|
                  |--------------|
```

The nodes of the graph represent basic blocks--which are just simple
instruction sequences.  Edges of the graph represent jumps to to a
different basic block.  Sometimes an edge depends on the result
of a condition or relation.   An edge might also be an unconditional
jump.

Internally, a compiler might construct a control flow graph in order
to further analyze the structure of the program (e.g., detecting when
variables are no longer needed, finding dead code, performing certain
optimizations, etc.).

## Expressing Control Flow with Jump Instructions

When generating code, there are different ways to express the
control flow graph.  One approach is to serialize the instruction
stream and to insert explicit jump instructions that link the blocks.
For example, like this:

```
	 |--------------|
	 |  b1:  a = 2  |
	 |       b = 3  |
	 |       a < b  |
	 |--------------|
	 | JMP_FALSE b3 |
	 |--------------|
	 | b2: c = a +b |
	 |--------------|
	 | JMP b4       |
	 |--------------|
	 | b3: c = a-b  |
	 |--------------|
	 | b4: print(c) |
	 |--------------|
```

This is how Python generates control-flow for its low-level instructions.
Take a look at this:

```
>>> def foo(a,b):					   
         if a < b:					   
             print("yes")				   
         else:						   
             print("no")				   
      							   
>>> import dis						   
>>> dis.dis(foo)					   
       2           0 LOAD_FAST                0 (a) 		   
                   3 LOAD_FAST                1 (b) 		   
                   6 COMPARE_OP               0 (<) 		   
                   9 POP_JUMP_IF_FALSE       25 		   
     							   
       3          12 LOAD_GLOBAL              0 (print) 	   
                  15 LOAD_CONST               1 ('yes') 	   
                  18 CALL_FUNCTION            1 		   
                  21 POP_TOP              			   
                  22 JUMP_FORWARD            10 (to 35) 	   
     							   
       5     >>   25 LOAD_GLOBAL              0 (print) 	   
                  28 LOAD_CONST               2 ('no') 	   
                  31 CALL_FUNCTION            1 		   
                  34 POP_TOP              			   
             >>   35 LOAD_CONST               0 (None) 	   
                  38 RETURN_VALUE                               
>>>
```

Carefully study the code.  Can you identify the basic blocks?
How does control flow of the if-statement pass from block to block?

Try disassembling a while-loop:

```
>>> def countdown(n):					    
        while n > 0:					    
            print("T-minus",n)				    
            n -= 1					    
     							    
>>> dis.dis(countdown)					    
      2           0 SETUP_LOOP              39 (to 42) 	    
            >>    3 LOAD_FAST                0 (n) 		    
                  6 LOAD_CONST               1 (0) 		    
                  9 COMPARE_OP               4 (>) 		    
                 12 POP_JUMP_IF_FALSE       41 		    
    							    
      3          15 LOAD_GLOBAL              0 (print) 	    
                 18 LOAD_CONST               2 ('T-minus') 	    
                 21 LOAD_FAST                0 (n) 		    
                 24 CALL_FUNCTION            2 		    
                 27 POP_TOP              			    
    							    
      4          28 LOAD_FAST                0 (n) 		    
                 31 LOAD_CONST               3 (1) 		    
                 34 INPLACE_SUBTRACT     			    
                 35 STORE_FAST               0 (n) 		    
                 38 JUMP_ABSOLUTE            3 		    
            >>   41 POP_BLOCK            			    
            >>   42 LOAD_CONST               0 (None) 	    
                 45 RETURN_VALUE         			    
>>>                                                         
```

Again, study the disassembly.  Can you identify the basic blocks?
What is the control flow between blocks?  

## Structured Control Flow

Instead of using jump instructions, an alternative approach is to use
what's known as structured control flow.  This is basically the
same approach as expressed in high-level languages like Python.
It's what you are doing by indenting blocks of code.

IR code with structured-control flow might look like this:

```
	 |--------------|
	 |  a = 2       |
	 |  b = 3       |
	 |  a < b       |
	 |--------------|
	 | IF           |
	 |--------------|
	 | c = a +b     |
	 |--------------|
	 | ELSE         |
	 |--------------|
	 | c = a-b      |
	 |--------------|
	 | ENDIF        |
	 |--------------|
	 | print(c)     |
	 |--------------|
```

Notice, instead of emitting labels, you emit `IF`, `ELSE`, and
`ENDIF` instructions to mark blocks.  

For looping constructs, structured control flow is often a bit counter-intuitive.
Suppose you have a while loop like this:

```
while n > 0 {
     print(n);
     n = n - 1;
}
print("Done")
```

This can be translated into the following code which is equivalent. Notice
the use of an infinite-loop and `break` statement.

```
while true {
    if n > 0:
        break;
    print(n)
    n = n - 1
}
print("Done")
```

The low-level instruction stream would then look like this:

```
	 |--------------|
	 | LOOP         |
	 |--------------|
	 | not n > 0    |
	 |--------------|
	 | CBREAK       |   (Conditional Break)
	 |--------------|
	 | print(n)     |
	 | n = n - 1    |
	 |--------------|
	 | ENDLOOP      |
	 |--------------|
	 | print("Done")|
	 |--------------|
```

The idea here is that the loop cycles endlessly until a conditional
break instruction makes it stop.  The placement of the `CBREAK`
allows different kinds of looping constructs (e.g., do-while loops and
other variants).

## Control flow in Wabbit

Wabbit supports an `if-else` statement:

```
if relation {
    statements
} else {
    statements
}
```

and a `while`-loop:

```
while relation {
    statements
}
```

For loops, the `break` statement exits a loop early.  The `continue` statement
skips to the next iteration (jumps back to the top of the loop).


## Wasm Code Generation

WebAssembly uses structured control flow.  There are special instructions
for conditionals that are straightforward. 

Loops in Wasm are slightly more tricky.  For this, you
need to enclose the loop both in an outer block and by an inner loop
instruction.  In pseudocode, it looks like this:

```
block {
  loop {
      # Evaluate the loop test
      ...
      br_if 1     # Break to enclosing block if eval stack is true
      # Evaluate the loop body
      ...
      br 0        # Go back to top of loop
  }
  # The br_if 1 targets this position
  ...
}
```

All of these elements (`block`, `loop`, `br_if`, and `br`) are
Wasm instructions.  See pg. 90 of the WebAssembly Specification, v1.0 
for the precise encoding.

## Generating LLVM

The following code example shows how to generate code for conditional:

```
# Example 1 : LLVM code for the following function
#
#     func f(a int, b int) int {
#          var c int;
#          if a < b {
#               c = a + b;
#          } else {
#               c = a - b;
#          }
#          return c;
#     }
#

from llvmlite.ir import (
    Module, IRBuilder, IntType, Function, FunctionType
    )

mod = Module('example')
f_func = Function(mod,
                  FunctionType(IntType(32), [IntType(32), IntType(32)]),
                  name='f')

block = f_func.append_basic_block("entry")
builder = IRBuilder(block)

# Get the arguments
a_var, b_var = f_func.args

# Allocate the result variable
c_var = builder.alloca(IntType(32), name='c')

# Perform the comparison
testvar = builder.icmp_signed('<', a_var, b_var)

# Make three blocks
then_block = f_func.append_basic_block('then')
else_block = f_func.append_basic_block('else')
merge_block = f_func.append_basic_block('merge')

# Emit the branch instruction
builder.cbranch(testvar, then_block, else_block)

# Generate code in the then-branch
builder.position_at_end(then_block)
result = builder.add(a_var, b_var)
builder.store(result, c_var)
builder.branch(merge_block)

# Generate code in the else-branch
builder.position_at_end(else_block)
result = builder.sub(a_var, b_var)
builder.store(result, c_var)
builder.branch(merge_block)

# Emit code after the if-else
builder.position_at_end(merge_block)
builder.ret(builder.load(c_var))
```

The following sample shows how to generate code for a loop in LLVM:

```
# Example : LLVM code for the following function
#
#     func f(n int) int {
#          var total int = 0;
#          while n > 0 {
#               total = total + n;
#               n = n - 1;
#          }
#          return total;
#     }
#

from llvmlite.ir import (
    Module, IRBuilder, IntType, Function, FunctionType, Constant
    )

mod = Module('example')

# Declare the f function with our loop
f_func = Function(mod,
                  FunctionType(IntType(32), [IntType(32)]),
                  name='f')

block = f_func.append_basic_block("entry")
builder = IRBuilder(block)

# Copy the argument to a local variable.  For reasons, that are 
# complicated, we copy the function argument to a local variable
# allocated on the stack (this makes mutations of the variable
# easier when looping).

n_var = builder.alloca(IntType(32), name='n')
builder.store(f_func.args[0], n_var)

# Allocate the result variable
total_var = builder.alloca(IntType(32), name='total')
builder.store(Constant(IntType(32), 0), total_var)

# Make a new basic-block for the loop test
loop_test_block = f_func.append_basic_block('looptest')
builder.branch(loop_test_block)
builder.position_at_end(loop_test_block)

# Perform the comparison
testvar = builder.icmp_signed('>', builder.load(n_var), Constant(IntType(32), 0))

# Make three blocks
loop_body_block = f_func.append_basic_block('loopbody')
loop_exit_block = f_func.append_basic_block('loopexit')

# Branch based on the test var
builder.cbranch(testvar, loop_body_block, loop_exit_block)

builder.position_at_end(loop_body_block)
tmp = builder.add(builder.load(total_var), builder.load(n_var))
builder.store(tmp, total_var)
tmp2 = builder.sub(builder.load(n_var), Constant(IntType(32), 1))
builder.store(tmp2, n_var)
builder.branch(loop_test_block)

# Emit code in the loop-exit
builder.position_at_end(loop_exit_block)
builder.ret(builder.load(total_var))
```

It is critical that every LLVM block be terminated by a branch. So,
when generating code, you need to make sure approach branch
instructions are generated to get control flow to jump.  If you forget
this, you'll get crazy error messages. You'll also get an error if you
attempt to put more than one branch in the same block or if you put
instructions after a branch.

