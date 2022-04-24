# Project 4 - Parsing

In this project, we write a proper parser for Wabbit
This will allow us to build data
models directly from source code as opposed to having to build them by
hand as we did in `test_models.py`.

Go to the file `wabbit/parse.py` and follow the instructions inside.

See the document [WabbitSyntax](WabbitSyntax.pdf) for syntax diagrams.

## Testing

Implementing the parser is probably the most difficult part of the
project.  It is important to have a plan.  The directory `tests/Parser`
has a series of parsing tests in increasing order of difficulty. A
good strategy is to start here and work your way through the
tests one-by-one.

When you are done with the basic parsing tests, move on to the various
programs in `tests/Programs`.   Here is an example of what it might
look like to run the parser and see the resulting output:

```
bash $ cat tests/Programs/12_loop.wb
/* 12_loop.wb

   Test of a while-loop
*/

var n int = 1;
var value int = 1;

/* Prints out the first 10 factorials */
while n < 10 {
    value = value * n;
    print value ;
    n = n + 1;
}

bash $ python3 -m wabbit.parse tests/Programs/12_loop.wb
[Variable(n, int, Integer(1)), Variable(value, int, Integer(1)), While(BinOp(<, Load(NamedLocation(n)),
 Integer(10)), [Assignment(NamedLocation(value), BinOp(*, Load(NamedLocation(value)), Load(NamedLocation(n)))), 
Print(Load(NamedLocation(value))), Assignment(NamedLocation(n), BinOp(+, Load(NamedLocation(n)), Integer(1)))])]
```

Again, your output might vary depending on how you defined your data
model.  Reading that is not always so easy. You might want to add some
debugging functions to make it easier to view.  For example, the
`to_source()` function in the `wabbit/model.py` file.

## Interpretation

If you are feeling lucky, modify your `wabbit/interp.py` file so that
it can run programs. Have it read source code, parse it into a model,
and run it.  For example:

```
bash $ python3 -m wabbit.interp tests/Programs/12_loop.wb
1
2
6
24
120
720
5040
40320
362880
bash $
```

If this works, you should be able to run all of the programs
in `tests/Programs`.   Congratulations! You just wrote the
core of a scripting language--albeit a really slow one.




