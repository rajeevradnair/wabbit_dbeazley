# Recursion Exercises

One of the main challenges faced by participants in the compilers course is the heavy use of recursion.  Recursion is a natural part of compilers because most of the underlying data structures are trees.

To prepare, you might try writing some recursive functions using a programming language that you already know such as Python.  Here is an example of counting over a range of numbers using recursion:

```
def count(start, stop):
    if start >= stop:
        return
    else:
        print(start)
        count(start+1, stop)

# Count from 0 to 9
count(0, 10)
```

Here is a classic example that computes factorials:

```
def factorial(n):
    if n <= 1:
        return 1
    else:
        return n * factorial(n - 1)
```

## Exercises

Here are some additional exercises you can try.  Again, do these in
Python or some other familiar language.

### Exercise R.1:

Write a recursive function `count_multiples(a, b)` 
that counts how many multiples of `a` are part of the
factorization of the number `b`. For example:

```
>>> count_multiples(2, 6)     # 2 * 3 = 6
1
>>> count_multiples(2, 12)    # 2 * 2 * 3 = 12
2
>>> count_multiples(3, 11664)
6
>>>
```

### Exercise R.2:

Write a recursive function that finds the maximum
value in a Python list without using any kind of
looping construct such as "for" or "while."  For example:

```
>>> maxval([1, 9, -3, 7, 13, 2, 3])
13
>>>
```

Hint: You may use slices.

### Exercise R.3:

Write a recursive function that flattens nested Python lists. For example:

```
>>> flatten([1, [2, [3, 4], 5], 6])
[1, 2, 3, 4, 5, 6]
>>>
```

### Exercise R.4:

Write a recursive function that counts the number of 
occurrences of an item in nested lists. For example:

```
>>> count_occurrences(2, [1, [4, [5, 2], 2], [8, [2, 9]]])
3
>>>
```

### Exercise R.5:

Write a recursive function that merges two sorted lists of numbers
into a single sorted list. For example:

```
>>> merge([1, 8, 9, 14, 15], [2, 10, 23])
[1, 2, 8, 9, 10, 14, 15, 23]
>>>
```

### Exercise R.6:

Write a recursive function that reverses a linked-list constructed from
Python 2-tuples. For example:

```
>>> reverse((1, (2, (3, (4, None)))))
(4, (3, (2, (1, None))))
>>>
```

## Important Note

The above exercises are only meant for recursion practice. Some are
more difficult than others, but none are essential for ultimate success in writing
a compiler.

