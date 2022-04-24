Important
=========

Make sure you are working on your own branch of the GitHub repo before
modifying any of the programs here.  For example, do this first (replace
yourname with your name of course):

```
bash $ git checkout -b yourname
```

Playing with Wabbit
===================

You're going to write a compiler for a small language called Wabbit.
This directory is a playground where you can try the language
and write some small programs.  You should do this before you
start on the main compiler project.

There are three programs here: prog1.wb, prog2.wb, and prog3.wb.  Go
to each program and follow the instructions inside. You can run each
program using the provided program `wabbit.py`.  For example::

```
$ python3 wabbit.py prog1.wb
... see the output ...
```

Don't concern yourself too much with the details of the `wabbit.py`
program (if you must know, it's running each program in an interpreter
which is sort of similar to the compiler you're going to write except
that everything runs a lot slower and it's somewhat user-hostile with
respect to error messages).

I don't guarantee that wabbit.py is entirely free of bugs--or good
error messages for that matter.  Think of this as more of a minimal
viable implementation to see how things might work.



