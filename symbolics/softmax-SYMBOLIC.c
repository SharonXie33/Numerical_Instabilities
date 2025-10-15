#include <stdio.h>
#include <klee/klee.h>
#include <math.h>

int main() {
    float in[4];
    klee_make_symbolic(in, sizeof(in), "input");
    volatile float maxv = in[0];
    for (int i=1;i<4;i++) if (in[i]>maxv) maxv = in[i];
    volatile float exps[4];
    volatile float sum = 0.0f;
    for (int i=0;i<4;i++){
        exps[i] = expf(in[i]-maxv);
        sum += exps[i];
    }
    volatile float out0 = exps[0]/sum;
    printf("%a\n", out0);
    return 0;
}
