# Project 3 - Tokenizing

This project starts the process of building a parser that can take
Wabbit source text and turn it into the data model you created in
Project 1.

Go to the file `wabbit/tokenize.py` and follow the instructions inside.

## Testing

Once you have written a tokenizer, you should be able to test it on
various sample input programs in the `tests/Parser` and `tests/Programs/` directory.  For
example:

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

bash $ python3 -m wabbit.tokenize tests/Programs/12_loop.wb
Token(type='VAR', value='var', lineno=3)
Token(type='NAME', value='n', lineno=3)
Token(type='NAME', value='int', lineno=3)
Token(type='ASSIGN', value='=', lineno=3)
Token(type='INTEGER', value='1', lineno=3)
Token(type='SEMI', value=';', lineno=3)
Token(type='VAR', value='var', lineno=4)
Token(type='NAME', value='value', lineno=4)
Token(type='NAME', value='int', lineno=4)
Token(type='ASSIGN', value='=', lineno=4)
Token(type='INTEGER', value='1', lineno=4)
Token(type='SEMI', value=';', lineno=4)
Token(type='WHILE', value='while', lineno=6)
Token(type='NAME', value='n', lineno=6)
Token(type='LT', value='<', lineno=6)
Token(type='INTEGER', value='10', lineno=6)
Token(type='LBRACE', value='{', lineno=6)
Token(type='NAME', value='value', lineno=7)
Token(type='ASSIGN', value='=', lineno=7)
Token(type='NAME', value='value', lineno=7)
Token(type='TIMES', value='*', lineno=7)
Token(type='NAME', value='n', lineno=7)
Token(type='SEMI', value=';', lineno=7)
Token(type='PRINT', value='print', lineno=8)
Token(type='NAME', value='value', lineno=8)
Token(type='SEMI', value=';', lineno=8)
Token(type='NAME', value='n', lineno=9)
Token(type='ASSIGN', value='=', lineno=9)
Token(type='NAME', value='n', lineno=9)
Token(type='PLUS', value='+', lineno=9)
Token(type='INTEGER', value='1', lineno=9)
Token(type='SEMI', value=';', lineno=9)
Token(type='RBRACE', value='}', lineno=10)
```

Your output might vary slight depending on how you implement things,
but it should roughly look like that--a stream of tokens representing
the input program.


