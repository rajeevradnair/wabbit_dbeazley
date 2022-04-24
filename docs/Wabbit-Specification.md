# Introducing Wabbit

You are going to be implementing a programming language called
"Wabbit."  Wabbit is statically typed (like C, Java, Rust, etc.). The
syntax is roughly similar to Go.  Ultimately, you'll be able to
compile Wabbit programs that execute in a virtual machine, as a
stand-alone executable, or as WebAssembly in the browser.

Most parts of Wabbit are straightforward--being identical to features
of programming languages that you already know.  However, some parts
of Wabbit are significantly more challenging to understand and
implement.  For example, short-circuit evaluation. Expect to be pushed
to the limit on the project.

## 0. A Taste of Wabbit

Here is a sample Wabbit program that computes the first 30 ever-so-useful
Fibonacci numbers:

```
/* fib.wb -  Compute fibonacci numbers */

const LAST = 30;            // A constant declaration

// A function declaration
func fibonacci(n int) int {
    if n > 1 {              // Conditionals
        return fibonacci(n-1) + fibonacci(n-2);
    } else {
        return 1;
    }
}

func main() int {
    var n int = 0;            // Variable declaration
    while n < LAST {          // Looping (while)
        print fibonacci(n);   // Printing
        n = n + 1;            // Assignment
    }
    return 0;
}

main();
```

This program, although small, illustrates most of Wabbit's basic features
including variables, functions, conditionals, looping, and printing.  

## 1. Syntax

Wabbit programs consist of statements, expressions, and definitions.
Each of these is normally terminated by a semicolon.  For example:

```
print 3;
var a int = 4;
```

A single-line comment is denoted by `//`.  For example:

```
var a int = 4;    // This is a comment
```

Multiline comments can be written using `/* ... */`. For example:

```
/* 
 This is a multiline
 comment.
*/
```

An identifier is a name used to identify variables, constants, types,
and functions.  Identifiers can include letters, numbers, and the
underscore (_), but must always start with a non-numeric character
(Wabbit follows the same rules as Python).  The following reserved
words may not be used as an identifier:

```
break const continue else false func if print return true while var
```

A numeric literal such as `12345` is intepreted as an integer.  A
numeric literal involving a decimal point such as `1.2345` is
interpreted as a floating point number.  The literals `true` and
`false` are interpreted as booleans.

A character literal such as `'h'` is interpreted as a single text
character. Escape codes such as `\'`, `\n`, `\\`, and `\xhh` are to be
interpreted in the same way they are in Python.  Wabbit does not have
multi-character text strings (although it could if you made it).

Curly braces are used to enclose blocks of statements or expressions
for the purpose of expressing control flow or defining compound
expressions. For example:

```
if a < b {
   statement1;
   statement2;
} else {
   statement3;
   statement4;
}
```

## 2. Types

Wabbit implements a static type system similar to C or Java.

### 2.1 Built-in types

There are four built-in datatypes; `int`, `float`, `char`, and `bool`.

`int` is a signed 32-bit integer.  `float` is a 64-bit double
precision floating point number.  `char` is a single character.
`bool` represents the boolean values `true` and `false`.

### 2.2 Defining Variables

Variables are declared using a `var` declaration.  They must also have a type and/or an
optional initializer.  For example:

```
var a int;
var b float = 3.14159;
var c bool;  
var d char = 'h';
```

When given an initializer, the type may be omitted--in which case
the type is inferred from the initial value.  For example, these
declarations are legal:

```
var b = 3.14159;    // type float (inferred)
var d = b * 2.0;    // type float (inferred in expression)
```

Immutable variables may be declared using `const`.  `const`
declarations must include an initializer.  For example:

```
const e = 4;        // Integer constant
const f = 2.71828;  // Float constant
const g = true;     // Bool constant
const h = 'h';      // Char constant
```

A `const` declaration may include a type even though it is
redundant.  For example:

```
const e int = 4;    // Integer constant
```

A `const` declaration may be initialized by an arbitrary
expression. For example:

```
const tau = 2.0*pi;
```

## 3. Operators and Expressions

An expression represents something that evaluates to a value (i.e., an
integer, float, structure, etc.). Think of it as code that could
legally go on the right-hand-side of an assignment:

```
x = expression;
```

### 3.1 Numeric operators

Numeric types support the binary operators `+`, `-`, `*`, and `/` with
their standard mathematical meaning.  Operators require both operands
to be of the same type.  For example, `x / y` is only legal if `x` and
`y` are the same type.  The result type is always the same type as the
operands.  Note: for integer division, the result is an integer and is
truncated.

Numeric types also support the unary operators of `+` and `-`. For
example:

```
z = -y;
z = x * -y;
```

No automatic type coercion is performed.  Thus, integers and floats
can not be mixed together in any operation.  If this is desired, 
one of the values may be converted to the other using an 
explicit type cast.  For example:

```
var a = 2;
var b = 2.5;
var c float = float(a) + b;  // Explicit cast (a->float)
var d int = a + int(b);      // Explicit cast (b->int)  
```

Numbers can be compared using `<`, `<=`, `>`, `>=`,
`==`, and `!=` with their usual meaning.  The result of any comparison
is of type `bool`.

### 3.2 Character operations

Character literals support no mathematical operations whatever. A
character is simply a "character" and that's it.  However, characters
can be compared using `<`, `<=`, `>`, `>=`, `==`, and `!=`.  The
result of a comparison is based on the character's numeric
representation (i.e., ASCII code).

A character `c` can be converted into an integer using `int(c)`.  An
integer character code n can be converted into a character using `char(n)`.

### 3.3 Boolean operators

The `bool` type only supports the operators `==`, `!=`, `&&`
(logical-and), `||` (logical-or), and `!` (logical-not).  Boolean
values are NOT equivalent to integers and can not be used in
mathematical operators involving numbers.

Expressions such as the following are illegal unless `a` and `b` are
of type `bool`:

```
a && b;     // Illegal unless a,b are bools
```

Unlike Python, Wabbit is precise with booleans. If a `bool` is
expected, you must provide a `bool` and not a "truthy" value like an
`int`.

A bool `b` can be converted to an `int` using `int(b)`.  Likewise, an
integer or float `n` can be converted to a `bool` using `bool(n)`.  In this case,
0 is mapped to `false` and any other value is mapped to `true`.

### 3.4 Assignment

Assignment to a variable is considered to be an expression.  For example:

```
a = 123;
```

The value of an assignment is the right-hand side.  Assignments can be chained:

```
a = b = 123;      
```

In this case, both `a` and `b` get the value `123`.

Since assignment is an expression, it can be mixed with other operations:

```
print a = 42;      // Prints 42 and assigns the value to a
```

### 3.5 Short-circuit evaluation

The logical operators `&&` and `||` should implement short-circuit
behavior in evaluation.  That is, in the expression `a && b`, if `a`
evaluates to `false`, then `b` is not evaluated.  Similarly, if `a`
evaluates to `true`, then `a || b` does not evaluate `b`.

As an example, an expression such as this should not cause a crash:

```
const x = 0;
const y = 1;

if (x == 0 or (y / x > 0)) {  /* y/x does not evaluate */
    print 0;
} else {
    print 1;
}
```

### 3.6 Compound Expressions

Normally, an expression is defined by a single operation.  However,
arbitrary blocks of statements enclosed by `{` and `}` can also be
used as an expression.  For example:

```
var a = { 1 + 2; 3 + 4; 5 + 6; };
```

For such expressions, the value is the result of the last operation
performed which must be an expression. All other results are computed, but discarded.
So, in the above example, the value of `a` is set to `11`.   It is illegal for the
last operation to be a statement. For example:

```
var b = 2;
var c = { b = b + 1; print b; };    // Error. print is not an expression
```

Statement blocks also define a scope in which temporary variables can
be assigned. For example, you could swap the value of two variables by
writing code like this:

```
var a = 2;
var b = 3;

a = { var temp = b; b = a; temp; };
// temp variable is no longer defined here (out of scope)
```

This might look rather strange, but having compound expressions can be
useful in situations where calculations both produce values and
involve side effects such as assignments or I/O. It can also be a
useful trick for debugging.  If you wanted to inject a `print`
statement somewhere, you can do it with a compound expression.  For
example::

```
func factorial(n int) int {
    if n == 0 {
        return 1;
    } else {
        return n * factorial({print n; n-1;});
    }
}
```

### 3.7 Type Conversions

Types can be converted using the type name:

```
int(x);     // Converts x to an integer
bool(x);    // Converts integer x to a bool
char(x);    // Converts integer x to a character
float(x);   // Converts integer x to a float
```

The most complex conversion is `int(x)` which accepts any of the
other datatypes.  When converting a float, the value is truncated
to an integer.

### 3.8 Associativity and precedence rules

All binary operators except for assignment are left-associative.
The following chart shows the precedence rules from highest to lowest precedence:

```
func(args), { ... }      // Highest precedence
+, -, !, (unary)         // Right associative
*, /                     // Left associative
+, -        
<, <=, >, >=, ==, !=
&&
||
=                        // Lowest precedence, right associative
```

Relational operators may NOT be chained or associate together. For
example:

```
a < b && b < c        // OK
a < b < c             // Illegal
```

## 4. Control Flow

Wabbit has basic control-flow features in the form of `if`-statements and `while`-loops.

### 4.1. Conditionals

The `if` statement is used for a basic conditional. For example:

```
if (a < b) {
   statements;
   ...
} else {
   statements;
   ...
}
```

The conditional expression used for the test must evaluate to a `bool`.
Code such as the following is an error unless `a` has type `bool`:

```
if (a) {     // Illegal unless a is type bool
   ...
}
```

The `else` clause in a conditional is optional.

### 4.2 Looping

The `while` statement can be used to execute a loop.  For example:

```
while (n < 10) {
    statements;
    ...
}
```

This executes the enclosed statements as long as the associated
condition is `true`.   Again, the conditional expression must
evaluate to type `bool`.

The `break` statement can be used to break out of a loop early.  For
example, this code only prints the numbers 0, 1, ..., 4:

```
var n int = 0;
while n < 10 {
    statements;
    if (n == 5) {
        break;
    }
    print n;
    n = n + 1;
}
```

The `continue` statement can be used to jump back to the top of a loop, ignoring
the remainder of the loop body.

```
var n int = 0;
while n < 10 {
    statements;
    if n == 5 {
       continue;   // Skip to next iteration
    }
    print n;
    n = n + 1;
}
```

## 5. Functions

Functions can be defined using the `func` keyword as follows:

```
func fib(n int) int {
    if (n <= 2) {
       return 1;
    } else {
       return fib(n-1) + fib(n-2);
    }
}
```

Functions must supply types for the input parameters and return value
as shown.  A function can have multiple input parameters. For example:

```
func add(x int, y int) int {
    return x + y;
}
```

When calling a function, all function arguments are fully evaluated,
left-to-right prior to making the associated function call.  That is,
in a call such as `foo(a, b, c)`, the arguments `a`, `b`, and `c` are
fully evaluated to a value first. This is known as "applicative
evaluation order" or "eager evaluation."

All arguments are passed to a function by value--meaning that they are
effectively copies of the input.

Wabbit does NOT have higher-order functions.  Functions are not
special types nor can they be passed around as objects.  The only
way to refer to a function is by its name.

## 6.  Scoping rules

Wabbit uses lexical scoping to manage names. Declarations defined
outside of a function are globally visible to the entire
program. Declarations inside a function are local and not visible to
any other part of a program except for code in the same function.  For
example:

```
var a int;     // Global variable

func foo(b int) int {
    var c int;          // Local variable
    ...
}
```

Wabbit also makes use of so-called "block-scope" where variables declared
inside any block of code enclosed by curly braces (`{` ... `}`) are only
visible inside that block.  For example:

```
func bar(a int, b int) int {
    if a > b {
        var t int = b;   // Block scope variable
        b = a;
        a = t;
    }
    print t;             // Error: t not defined (not in scope)
    return a;   
}
```

Nested function definitions are NOT supported.  For example:

```
func foo(b int) int {
     func bar(c int) int { // Illegal. Nested functions not allowed
         ...
     }
     ...
}
```

Moreover, function definitions may only appear at the top-level, not within
a nested code block.  For example, this is illegal:

```
if x > 0 {
   func foo(b int) int {  // Illegal. Functions may not be declared in blocks
       ...
   }
}
```

## 7.  Execution model

Programs execute much like a script, running top-to-bottom until there are no more
statements to execute.   If there are functions defined, you must add extra steps
to invoke those functions.   For example:

```
func fact(n int) int {
     if n == 0 {
         return 1;
     } else {
         return n * fact(n-1);
     }
}

func main() int {
    var n = 1;
    while n < 10 {
        print fact(n);
	n = n + 1;
    }
    return 0;
}

// Explicit call to main() to make it run
main();
```

## 8. Printing

The built-in `print value` operation can be used for debugging
output.  It prints the value of any type given to it.  Values are
normally printed on separate lines.  However, if you print a single
character value, it is printed with no line break.

`print` is an example of a polymorphic operation in that it 
works on any kind of data.  This is different than how functions
work--where a matching datatype must be given.

## 9. Formal Grammar

The following grammar is a formal description of Wabbit syntax written
as a PEG (Parsing Expression Grammar). Tokens are specified in ALLCAPS
and are assumed to be returned by the tokenizer.  In this
specification, the following syntax is used:

```
{ symbols }   --> Zero or more repetitions of symbols
[ symbols ]   --> Zero or one occurences of symbols (optional)
( symbols )   --> Grouping
sym1 / sym2   --> First match of sym1 or sym2.
```

A program consists of zero or more statements followed by the end-of-file (EOF).
Here is the grammar:

```
program : statements EOF

statements : { statement }

statement : print_statement
          / variable_definition
          / const_definition
          / func_definition
          / if_statement
          / while_statement
          / break_statement
          / continue_statement
          / return_statement
          / expr_statement

print_statement : PRINT expression SEMI

variable_definition : VAR NAME [ type ] ASSIGN expression SEMI
                    / VAR NAME type [ ASSIGN expression ] SEMI

const_definition : CONST NAME [ type ] ASSIGN expression SEMI

func_definition : FUNC NAME LPAREN [ parameters ] RPAREN type LBRACE statements RBRACE

parameters : parameter { COMMA parameter }

parameter  : NAME type 

if_statement : IF expr LBRACE statements RBRACE [ ELSE LBRACE statements RBRACE ]

while_statement : WHILE expr LBRACE statements RBRACE

break_statement : BREAK SEMI

continue_statement : CONTINUE SEMI

return_statement : RETURN expression SEMI

expr_statement : expr SEMI

expr : logicalexpr { ASSIGN logicalexpr }

logicalexpr : orterm { LOR ortem }

orterm : andterm { LAND andterm }

andterm : sumterm [ LT/LE/GT/GE/EQ/NE sumterm ]

sumterm : multerm { PLUS/MINUS multerm }

multerm : factor { TIMES/DIVIDE factor }

factor : literal
       / LPAREN expression RPAREN
       / LBRACE statements RBRACE       
       / PLUS factor
       / MINUS factor
       / LNOT factor
       / NAME LPAREN [ exprlist ] RPAREN
       / location
       
literal : INTEGER
        / FLOAT
        / CHAR
        / TRUE
        / FALSE
        / LPAREN RPAREN
 
exprlist : expression { COMMA expression }
 
location : NAME

type      : NAME
```

