# Project 8 - Generating LLVM

It's time to take Wabbit and turn it into LLVM.  Before proceeding, you need to work through the [LLVM Tutorial](LLVM-Tutorial.md). 

Once you have completed the tutorial, go to the file `wabbit/llvm.py` and follow the instructions inside.

## Testing

To test this part of the project, you should be able to take any of
the scripts in `tests/Programs/` and turn it into LLVM output.  It might
look like this:

```
bash $ python3 -m wabbit.llvm tests/Programs/12_loop.wb
; ModuleID = "wabbit"
target triple = "unknown-unknown-unknown"
target datalayout = ""

declare void @"_printi"(i32 %".1") 

declare void @"_printf"(double %".1") 

declare void @"_printb"(i1 %".1") 

declare void @"_printc"(i32 %".1") 

define void @"main"() 
{
entry:
  store i32 1, i32* @"n"
  store i32 1, i32* @"value"
  br label %"test"
test:
  %".5" = load i32, i32* @"n"
  %".6" = icmp slt i32 %".5", 10
  br i1 %".6", label %"body", label %"exit"
body:
  %".8" = load i32, i32* @"value"
  %".9" = load i32, i32* @"n"
  %".10" = mul i32 %".8", %".9"
  store i32 %".10", i32* @"value"
  %".12" = load i32, i32* @"value"
  call void @"_printi"(i32 %".12")
  %".14" = load i32, i32* @"n"
  %".15" = add i32 %".14", 1
  store i32 %".15", i32* @"n"
  br label %"test"
exit:
  ret void
}

@"n" = global i32 0
@"value" = global i32 0
bash $
```

If you save this output to a file, you can compile it with the `clang`
compiler as long you as you also include the required runtime
functions (see below).  For example:

```
bash $ python3 -m wabbit.llvm tests/Programs/12_loop.wb >out.ll
bash $ clang out.ll runtime.c
bash $ ./a.out
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

## Runtime Library

To perform printing, you'll want to include a small C library of print
functions. For example:

```
/* runtime.c */
#include <stdio.h>

void _printi(int x) {
    printf("%i\n", x);
}
```

A complete `runtime.c` file was included in the starting `wabbit` directory.

