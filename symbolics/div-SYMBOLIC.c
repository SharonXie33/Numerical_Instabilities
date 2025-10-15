#include <stdio.h>
#include <klee/klee.h>

int main() {
    float input[2];
    klee_make_symbolic(input, sizeof(input), "input");
    volatile float a = input[0];
    volatile float b = input[1];
    volatile float r = a / b;
    // Prevent optimizer removing computations
    printf("%a\n", r);
    return 0;
}
