#include <stdio.h>
#include <klee/klee.h>
#include <math.h>

int main() {
    float input;
    klee_make_symbolic(&input, sizeof(input), "input");
    volatile float x = input;
    volatile float r = expf(x);
    printf("%a\n", r);
    return 0;
}
