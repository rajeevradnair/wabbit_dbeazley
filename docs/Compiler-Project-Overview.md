# Compiler Project Overview

You are going to be implementing the core of a simple programming
language called "Wabbit."  Wabbit supports the following features:

- Evaluation of expressions (math)
- Integers, floats, characters, and bools.
- Assignment to variables
- Printing
- Basic control flow (if, while)
- User-defined functions

Although the language is simple, you are going to have to write all of
the core components of an actual compiler, including all of the
parsing, type checking, control-flow analysis, and code generation.

The implementation approach is going to be incremental, but strongly
focused on understanding the problem, design, and testing.  We'll
start by focused on the internal data models and evaluation rules.
From there, we'll build the lexer and parser.  This we be expanded
to include a type system, code generation, and more.

By the end of the project, you will have several different compiler
targets including an interpreter, a virtual machine, LLVM,
and possibly WebAssembly.  All of these targets will give you a rich
flavor of what a compiler can do and how different things work.

## A Taste of Wabbit

Here is a sample of a simple Wabbit program that computes the ever-so-useful
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
    var n int = 0;           // Variable declaration
    while n < LAST {         // Looping (while)
        print fibonacci(n);   // Printing
        n = n + 1;            // Assignment
    }
    return 0;
}
```

The `fib.wb` program above can be found in the directory
`Tests/fib.wb`.

## Running and Compiling Programs

Ultimately the `wabbit` compiler will allow programs to be compiled
and executed in a variety of ways.  First, you'll be able to interpret
Wabbit source directly.

```
bash % python3 -m wabbit.interp fib.wb
1
1
2
3
5
8
13
21
34
55
...
bash %
```

You should see output similar to the above being generated, albeit
very slowly.  This is the most portable execution technique as it is simply
interpreted in the compiler which is pure Python.

You'll also be able to compile Wabbit code to run on a small virtual machine. This
works in almost the same way:

```
bash % python3 -m wabbit.wvm fib.wb
Created out.py
bash % python out.py
1
1
2
3
5
8
13
21
34
55
...
bash %
```

Instead of running on a VM, the `fib.wb` program can also be compiled to LLVM.

```
bash % python3 -m wabbit.llvm fib.wb
Wrote out.ll
bash % clang out.ll wabbit/runtime.c
bash % ./a.out
1
1
2
3
5
...
bash %
```

Compiling in this way requires the `clang` C/C++ compiler.  If you don't have
it installed correctly, compilation will probably fail.  The performance should be
be quite fast.

The final target for Wabbit is WebAssembly.  You'll be able to create a `.wasm`
file as follows:

```
bash % python3 -m wabbit.wasm fib.wb
Wrote out.wasm
bash % 
```

This creates a file `out.wasm`.   To run this program in the browser, copy the file to the `html/` directory,
go to that directory and launch a web server:

```
bash % cp out.wasm html
bash % cd html
bash % python3 -m http.server
```

Next, go to your browser and load http://localhost:8000/test.html.
You should see the output the program appearing on a web page.
Refer to the file `test.html` to see how it's done.

## Wabbit Language Reference

[Wabbit Language Reference](Wabbit-Specification.md) contains an official specification for the language.

