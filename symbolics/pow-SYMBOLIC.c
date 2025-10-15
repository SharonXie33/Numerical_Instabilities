#include <stdio.h>
#include <klee/klee.h>
#include <math.h>

int main() {
    float in[2];
    klee_make_symbolic(in, sizeof(in), "input");
    volatile float x = in[0];
    volatile float y = in[1];
    volatile float r = powf(x, y);
    printf("%a\n", r);
    return 0;
}
