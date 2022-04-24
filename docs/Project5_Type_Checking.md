# Project 5 - Type Checking

So far, everything you have coded has been on the "Happy Path."  We
have assumed that programs are correct.  All of the test programs in
`tests/Programs/` are correct programs.  However, most programmers make
mistakes from time to time.  It would be nice to give them some useful
error messages.  That is the goal of this project.

Basically, you are going to implement a checker that looks at a
program data model, analyzes it for errors, and reports those errors.
It will ultimately act as a filter in the compiler. After parsing a
program, you'll check it for errors.  Only if there are no errors do
you proceed to later steps such as interpreting or generating output
code.

See the file `wabbit/typecheck.py` and follow the instructions inside.

## Testing

The testing of this part of the project involves making intentional
Wabbit programming errors.  Most of these errors relate to types and
names.  Here are some examples:

```
print 2 + 3.4;       // Type error: int + float
print x;             // Error. 'x' is undefined.

const pi = 3.14159;
pi = 2.0;            // Error. pi is immutable.
```

To run a check, you might have it work as a stand-alone step. For
example:

```
bash $ python3 -m wabbit.typecheck errors.wb
Line 1: Type error: int + float
Line 2: 'x' undefined
Line 5: 'pi' is immutable.
bash $
```

The `tests/Error` directory has an assortment of programs with errors.
For Project 5, focus on `tests/Error/error_script.wb`.

## Hints and Suggestions

This part of the project is often difficult.  To do it, you need to
focus on specific programming elements in isolation.  For example,
consider an assignment statement like this:

```
location = expression;
```

Now, what is everything that could possibly go wrong with it?  Step
back and think about it:

* The expression on the right could have a type error inside of it (must check it separately).
* The type of the location on the left is different than the type of the expression on the right (you're trying to assign an `int` to a `float`).
* The location on the left doesn't exist (undefined name)
* The location on the left is immutable (const)

A lot of this is about being a language lawyer and understanding fine details.

## What are the Consequences of Bad Type Checking?

If you fail to find errors, the main consequence is that your compiler
will provide a very poor user experience to the hapless Wabbit user.
Instead of giving an informative error message, your compiler will
either crash on its own (internal compiler error) or the generated
code will crash somehow (e.g., die with a segmentation fault).
Neither of those failure modes happen to be very helpful. People will
flame Wabbit on Hacker News for its lousy error handling.

On the other hand, if you do no type checking whatsoever, your
compiler will still happily compile correct programs.  So, at least
there's still that.

## Note about Functions

When you make your type checker to handle functions, you'll need to
worry about scoping of variables (local vs. global scope) as well
as issues related to function calls themselves.  For example, making
sure the number of arguments match, the types of the arguments match,
and so forth.  There are a lot of picky details.  Expect this to take
more time.


