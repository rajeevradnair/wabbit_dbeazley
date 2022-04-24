# Project 7 - Targeting the Wabbit VM

Sometimes programming languages are compiled to run an abstract
virtual machine (e.g., Python, Java JVM, etc.).  A virtual
machine is low level like an actual CPU, but is also simplified
in many ways.   For example, the machine could provide support
for high-level operations like printing.  Similarly, a machine
might simplify the use of memory and CPU registers.

The basic idea of this project is as follows. Wabbit programs
are represented by a model.  For example, if you write this:

```
print 2 + 3 * 4;
```

There is an abstract syntax tree such as this:

```
PrintStatement(BinOp('+', Integer('2'), BinOp('*', Integer('3'), Integer('4'))))
```

In an earlier project, you wrote a definitional interpreter that
directly executed the model.  This project is somewhat similar except
that you're going to turn the model into instructions that run
on a simple stack machine.  For example, the above
Wabbit statement will become something like this:

```
code = [ ('IPUSH', 2),
         ('IPUSH', 3),
	 ('IPUSH', 4),
	 ('IMUL',),
	 ('IADD',),
	 ('IPRINT',) ]
```

These instructions will then run on a small virtual machine.

Go to the file `wabbit/wvm.py` and follow the instructions inside for
more information.  A few more specific details are described below.

## Expression Evaluation

To start out, you should focus on getting simple expressions to evaluate.
For example, can you run programs such as the print statement shown
earlier:

```
print 2 + 3 * 4;
```

## Variables

The second step of the project should focus on global variables and
constants.  Specifically, you should be able to run code such
as this:

```
const pi = 3.14159;
var tau float;
tau = 2.0 * pi;
print tau;
```

## Control Flow

After you have variables working, move on to control flow.   Specifically, you
might try programs such as this:

```
var a = 2;
var b = 3;
var maxval int;

if a < b {
   maxval = b;
} else {
   maxval = a;
}
print a;
```

Or this:

```
var n = 10;
while n > 0 {
    print n;
    n = n - 1;
}
```

For both of these programs, you need to decompose the control flow
into branches and gotos.   The WVM has the following instructions:

```
('LABEL', name)      # Declare a label (NOP)
('GOTO', name)       # Unconditionally jump to label name
('BZ', name)         # Jump to label name if top of the int stack is zero
```

You'll need to figure out how to decompose `if` and `while` statements
into gotos.  For example, here is some pseudocode for the above programs
using `goto`.

```
var a = 2;
var b = 3;
var maxval int;

var t1 = a < b;
if t1 == 0: GOTO L2

L1:
   maxval = b;
   GOTO L3;
L2:
   maxval = a;
   GOTO L3;

L3:
print a;
```

Or this:

```
var n = 10;
L1:
    t1 = n > 0;
    if t1 == 0: GOTO L3
L2:
    print n;
    n = n - 1;
    GOTO L1;
L3:
    # Done
```


## Functions

The final part of the project involves functions. This could involve a substantial amount of work
depending on what other parts of the compiler still need to be implemented.

Here are some specific issues you will need to address:

### Labeling

Functions represent a labeled block of code.  For a function such as this:

```
func square(x int) int {
    return x * x;
}
```

You'll need to emit instructions like this:

```
code = [
    ...
    ('LABEL', 'square'),
    ... # instructions for the function
    ('RET',),
]
```

To call a function from elsewhere, you'll use an instruction like `('CALL', 'square')`.

### Scoping Rules

Variables defined inside a function are local to that
function.  For example, if you define:

```
func foo(x int) int {
    var a = 2;
    var b = 3;
    ...
}
```

Then the variables `x`, `a` and `b` are local to that 
function.  If there are global variables with the same name,
there are no conflicts.  Moreover, calling the function
won't overwrite the global values.

### Activation Frames

Every time you call a function, a new stack frame (or activation
frame) gets created.  The stack frame is a storage area for all of the
local variables defined inside the function.

The Wabbit VM already takes care of this step for you when you use
the `CALL` instruction.   There are also special instructions `ILOAD_LOCAL`,
`ISTORE_LOCAL`, `FLOAD_LOCAL`, and `FSTORE_LOCAL` for accessing local
variables.  The `RET` instruction destroys the stack frame and returns
to the instruction immediately after the last `CALL` instruction.

### Argument passing

You'll need to figure out some way to pass input arguments to 
called functions.  Prior to calling a function, these arguments are
found on the evaluation stack.  You'll need to have some way to
move the arguments from the stack to the activation frame. You'll
also need some way to access these variables from within the
function itself.

Probably the easiest way to handle this is to start each function
by immediately copying the arguments to locals.  For example,
if generating code for `square(x)` shown earlier, you'd do this:

```
code = [
    ...
    ('LABEL', 'square'),
    ('ISTORE_LOCAL', 0),      # Store "x" in a local
    ('ILOAD_LOCAL', 0),       # load 'x'
    ('ILOAD_LOCAL', 0),       # load 'x'
    ('IMUL',),                # x*x    		   
    ('RET',),
]
```

It might look kind of inefficient and clumsy, but that's often
the case with low-level code generation.  You should be more
concerned with it producing the right answer at this stage.

### Return values

You'll need to figure out how to return a value from a function.
The return value of a function ultimately ends up on the evaluation
stack.  You'll need to be careful with your handling of types (remember
that WVM has separate stacks for integers and floats).

