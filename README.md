# Write a Compiler : April 18-22, 2022

Hello! This is the course project repo for the "Write a Compiler"
course.  This project will serve as the central point of discussion, code
sharing, debugging, and other matters related to the compiler project.

Although each person will work on their own compiler, it is requested
that all participants work from this central project, but in a separate
branch.   You'll perform these setup steps:

    bash % git clone https://github.com/dabeaz-course/compilers_2022_04
    bash % cd compilers_2022_04
    bash % git checkout -b yourname
    bash % git push -u origin yourname

There are a couple of thoughts on this approach. First, it makes it
easier for me to look at your code and answer questions (you can 
point me at your code, raise an issue, etc.).   It also makes it easier
for everyone else to look at your code and to get ideas.  Writing a
compiler is difficult. Everyone is going to have different ideas about
the implementation, testing, and other matters.  By having all of the
code in one place and in different branches, it will be better.

I will also be using the repo to commit materials, solutions, and 
other things as the course nears and during the course.

Finally, the repo serves as a good historical record for everything
that happened during the course after the fact.

Best,
Dave

## Important Note

Everything in this repo is subject to change up until the course start date.
Free feel to look around now, but you may want to check back from time to
time to see what's new.  If you create your own branch, you may need to
merge from main to pick up the latest changes prior to course start.

## Live Session 

The course is conducted live from 09:30 to 17:30 US Central Time on Zoom.
The meeting will be open about 30 minutes prior to the start time. Meeting
details are as follows:

David Beazley is inviting you to a scheduled Zoom meeting.

Join Zoom Meeting
https://us02web.zoom.us/j/82028132129?pwd=aUZwNjAwVjBVT0JOTjVLZVBHMHdkdz09

Meeting ID: 820 2813 2129
Passcode: 233195

## Chat

Discussion/Chat for the course can be found on [Gitter](https://gitter.im/dabeaz-course/compilers_2022_04).

## Course Requirements

Here are some of the basic software requirements:

* Python 3.6 or newer.
* llvmlite
* Clang C/C++ compiler.
* Node-JS and WABT (for WebAssembly)

One way to get llvmlite is to install the Anaconda Python
distribution.  If you intend to write a compiler in a different
language than Python, you will need to investigate the availability of
tools for generating LLVM. There is probably some library similar to
llvmlite.

Note: You may implement the compiler in a different language if you
wish.  Just be aware that coding samples will be given in Python--you
would have to translate. 

## Preparation

To prepare for writing a compiler, there are certain background topics
that you might want to review.  First, as a general overview, you
might look at the first part of the excellent book [Crafting Interpreters](https://craftinginterpeters.com).
Writing a compiler is similar to an interpreter (in fact, we'll even be writing an
interpreter as part of the project).   As for specific topics, here
are some important facets of the project:

* Trees and recursion.  Most of the data structures in a compiler are
  based on trees and recursively defined data structures. As such,
  much of the data processing also involves recursive functions.
  Recursion is often not a part of day-to-day coding so it's something
  that you might want to review in advance.  There are some recursion
  exercises listed below that you can work.

* Computer architecture.  A compiler translates high-level programs
  into low-level "machine code" that's typically based on the von Neumann architecture
  (https://en.wikipedia.org/wiki/Von_Neumann_architecture).  I don't
  assume prior experience writing machine language, but you should
  know that computers work by executing simple arithmetic instructions,
  loading and storing values from memory, and making "goto" jumps.

* Programming language semantics.  Writing a compiler also means that
  you're implementing a programming language.  That means knowing a
  lot of the fine details about how programming languages work. This
  includes rules for variables, expression evaluation (e.g., precedence),
  function calls, control flow, type checking, and other matters.
  In this course, we're creating a very simple language.  However,
  there are still many opportunities for confusion.  One such area
  is understanding the difference between an "expression" and a
  "statement."  In Python, that can be studied further by exploring
  the difference between the `eval()` and the `exec()` built-in
  functions.  Why are these functions different?

* Working interactively from the command line. The compiler project
  is a command-line based application.  You should be able to navigate
  the file-system, write command-line based scripts, and interactively
  debug programs from the command-line.   The `python -i` option
  may be especially useful.

* Modules and Packages.  The compiler project is structured as a
  Python package (nested modules).  Many parts of the compiler
  execute using the `-m` option to the interpreter. I suggest
  the following article. (https://www.usenix.org/system/files/login/articles/12_beazley-online_0.pdf).

* String processing. Part of the project involves writing a
  parser.  This involves a certain amount of text processing.
  You should be comfortable iterating over characters, splitting
  strings apart, and performing other common string operations.

## Warmup work

If you're looking to get started, here are some starting projects.  The course starts
by working on Project 0.

* [Warmup Exercises](docs/Warmup-Exercises.md)
* [Recursion Exercises](docs/Recursion-Exercises.md)
* [Implementing an Interpreter (PyCon India)](https://www.youtube.com/watch?v=VUT386_GKI8)
* [Project 0 - The Metal](docs/Project0_The_Metal.md)
* [Project 0.5 - SillyWabbit](docs/Project0_5_SillyWabbit.md)

## The Project

We are writing a compiler for the language [Wabbit](docs/Wabbit-Specification.md).
The following links provide more information on specific project stages.

* [Project 1 - The Model](docs/Project1_The_Model.md)
* [Project 2 - The Interpreter](docs/Project2_The_Interpreter.md)
* [Project 3 - The Lexer](docs/Project3_Tokenizing.md)
* [Project 4 - The Parser](docs/Project4_Parsing.md)
* [Project 5 - Type Checking](docs/Project5_Type_Checking.md)
* [Project 6 - Transformations](docs/Project6_Transformation.md)
* [Project 7 - Wabbit VM](docs/Project7_WVM.md)
* [Project 8 - LLVM](docs/Project8_LLVM.md)
* [Project 9 - Web Assembly](docs/Project9_WASM.md)

## Resources

* [Documents & Knowledge Base](docs/README.md)

## Live Session Recordings

Videos from the live sessions will be posted here.


