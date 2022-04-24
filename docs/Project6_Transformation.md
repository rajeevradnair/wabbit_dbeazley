# Project 6 : Transformation

One of the most critical parts of the whole compiler is the data model
that you use to represent programs.  For example, to represent an
expression such as `2 + 3 * 4`, you might have a data structure like
this:

```
BinOp('+', Integer(2), BinOp('*', Integer(3), Integer(4)))
```

However, when generating low-level code, the compiler might do too much
work.  For example, perhaps the compiler could just precompile the
value and replace the `BinOp` with a node such as `Integer('14')`.
This kind of optimization is known as constant-folding.

There are other kinds of simplications that you could make as well.
For example, most unary operations could be replaced by a binary
operation or a no-op.  For example:

```
UnaryOp('+', Integer(3))
```

Could become:

```
Integer(3)
```

Similarly,

```
UnaryOp('-', LoadVar('x'))
```

Could become:

```
BinOp('-', Integer('0'), LoadVar('x')
```

Your task in this project is to see if you can apply various transformations
to the model that result in a simplified model.

More instructions can be found in the file `wabbit/transform.py`.

## This project is optional

Applying transformations to the model can result in simplified compiler
output.  However, it's purely optional.  If you're pressed for time
or want to work on other things, you can skip this project.


