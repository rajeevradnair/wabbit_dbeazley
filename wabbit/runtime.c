/* For LLVM, you need some runtime functions to produce ouput.  Use
   these and include them in final compilation with clang. */

#include <stdio.h>

void _printi(int x) {
  printf("Out: %i\n", x);
}

void _printf(double x) {
  printf("Out: %lf\n", x);
}

void _printb(int x) {
  if (x) {
    printf("Out: true\n");
  } else {
    printf("Out: false\n");
  }
}

void _printc(char c) {
  printf("%c", c);
  fflush(stdout);
}

void _printu() {
  printf("Out: ()\n");
}
