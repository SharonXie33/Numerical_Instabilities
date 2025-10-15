#include <stdio.h>
#include <klee/klee.h>

int main(){
    float in[2];
    klee_make_symbolic(in, sizeof(in), "input");
    volatile float a=in[0];
    volatile float b=in[1];
    volatile float r = a - b;
    printf("%a\n", r);
    return 0;
}
