# Project 1 - The Model

To start the compiler project, we're going to focus on the problem of
representing programs as a proper data structure. 

## Setup

In the top-level directory, you will find the file `test_models.py`
as well as the `wabbit/` directory.  This is where you will be doing
most of your work.  However, please make sure you are working in your
own GitHub branch:

```
bash $ git checkout -b yourname
bash $ git push origin -u yourname
```

## High-level overview

The input to a compiler is a text-file sometimes referred to as the
"source."  However, a compiler doesn't like to work with your program
as text.  Instead, it builds a proper data structure representing the
contents and structure of the program.  Typically, this is a tree-like
structure known as an "Abstract Syntax Tree".  We're simply going to
call it the "model".  Programs don't necessarily have to originate
with text files--they could be constructed graphically (i.e.,
block-based programming) or generated algorithmically.  Hence, the
"model" terminology is perhaps a bit more generic.

## Your task

Go to the file `test_models.py` and follow the instructions inside.
You will mainly be editing `test_models.py` and `wabbit/model.py`.
