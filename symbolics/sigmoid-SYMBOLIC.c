#include <stdio.h>
#include <klee/klee.h>
#include <math.h>

int main(){
    float x;
    klee_make_symbolic(&x, sizeof(x), "input");
    volatile float r = 1.0f / (1.0f + expf(-x));
    printf("%a\n", r);
    return 0;
}
