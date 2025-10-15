#include <stdio.h>
#include <klee/klee.h>
#include <math.h>

int main(){
    float x[3];
    float y[3];
    klee_make_symbolic(x, sizeof(x), "x");
    klee_make_symbolic(y, sizeof(y), "y");
    volatile float dot=0.0f, nx=0.0f, ny=0.0f;
    for(int i=0;i<3;i++){
        dot += x[i]*y[i];
        nx += x[i]*x[i];
        ny += y[i]*y[i];
    }
    volatile float denom = sqrtf(nx)*sqrtf(ny);
    volatile float r = denom==0.0f ? 0.0f : dot/denom;
    printf("%a\n", r);
    return 0;
}
