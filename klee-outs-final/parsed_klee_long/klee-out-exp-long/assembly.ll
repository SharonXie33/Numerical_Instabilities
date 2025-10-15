; ModuleID = 'exp-long.linked.bc'
target datalayout = "e-p:64:64:64-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v64:64:64-v128:128:128-a0:0:64-s0:64:64-f80:128:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

@.str = private unnamed_addr constant [6 x i8] c"input\00", align 1
@.str1 = private unnamed_addr constant [4 x i8] c"%a\0A\00", align 1
@switch.table = private unnamed_addr constant [5 x i32] [i32 0, i32 3073, i32 2048, i32 1024, i32 3072]
@.str2 = private unnamed_addr constant [81 x i8] c"/home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/klee_div_zero_check.c\00", align 1
@.str13 = private unnamed_addr constant [15 x i8] c"divide by zero\00", align 1
@.str24 = private unnamed_addr constant [8 x i8] c"div.err\00", align 1
@.str3 = private unnamed_addr constant [8 x i8] c"IGNORED\00", align 1
@.str14 = private unnamed_addr constant [16 x i8] c"overshift error\00", align 1
@.str25 = private unnamed_addr constant [14 x i8] c"overshift.err\00", align 1
@.str6 = private unnamed_addr constant [72 x i8] c"/home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/klee_range.c\00", align 1
@.str17 = private unnamed_addr constant [14 x i8] c"invalid range\00", align 1
@.str28 = private unnamed_addr constant [5 x i8] c"user\00", align 1
@.str9 = private unnamed_addr constant [84 x i8] c"/home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/klee_set_rounding_mode.c\00", align 1
@.str110 = private unnamed_addr constant [22 x i8] c"Invalid rounding mode\00", align 1
@.str211 = private unnamed_addr constant [1 x i8] zeroinitializer, align 1

; Function Attrs: nounwind uwtable
define i32 @main() #0 {
  %1 = alloca i32, align 4
  %input = alloca float, align 4
  %x = alloca float, align 4
  %r = alloca float, align 4
  store i32 0, i32* %1
  %2 = bitcast float* %input to i8*
  call void @klee_make_symbolic(i8* %2, i64 4, i8* getelementptr inbounds ([6 x i8]* @.str, i32 0, i32 0))
  %3 = load float* %input, align 4
  store volatile float %3, float* %x, align 4
  %4 = load volatile float* %x, align 4
  %5 = call float @expf(float %4) #6
  store volatile float %5, float* %r, align 4
  %6 = load volatile float* %r, align 4
  %7 = fpext float %6 to double
  %8 = call i32 (i8*, ...)* @printf(i8* getelementptr inbounds ([4 x i8]* @.str1, i32 0, i32 0), double %7)
  ret i32 0
}

declare void @klee_make_symbolic(i8*, i64, i8*) #1

; Function Attrs: nounwind
declare float @expf(float) #2

declare i32 @printf(i8*, ...) #1

; Function Attrs: nounwind uwtable
define void @fp_injection(i8* nocapture readonly %psrc1, i8* nocapture readonly %psrc2, i8* nocapture readonly %pdest) #3 {
  %1 = bitcast i8* %psrc1 to double*
  %2 = load double* %1, align 8, !tbaa !234
  %3 = tail call i32 @klee_internal_fpclassify(double %2) #10
  %4 = icmp eq i32 %3, 4
  %5 = bitcast i8* %psrc2 to double*
  %6 = load double* %5, align 8, !tbaa !234
  %7 = tail call i32 @klee_internal_fpclassify(double %6) #10
  %8 = icmp eq i32 %7, 4
  %9 = and i1 %4, %8
  br i1 %9, label %10, label %36

; <label>:10                                      ; preds = %0
  %11 = bitcast double %6 to i64
  %12 = bitcast double %2 to i64
  %int_cast_to_i64 = bitcast i64 52 to i64
  call void @klee_overshift_check(i64 64, i64 %int_cast_to_i64)
  %13 = lshr i64 %12, 52
  %14 = and i64 %13, 2047
  %int_cast_to_i641 = bitcast i64 52 to i64
  call void @klee_overshift_check(i64 64, i64 %int_cast_to_i641)
  %15 = lshr i64 %11, 52
  %16 = and i64 %15, 2047
  %17 = sub nsw i64 %14, %16
  %int_cast_to_i642 = bitcast i64 63 to i64
  call void @klee_overshift_check(i64 64, i64 %int_cast_to_i642)
  %18 = ashr i64 %17, 63
  %19 = add nsw i64 %18, %17
  %20 = xor i64 %19, %18
  %21 = icmp sgt i64 %20, 32
  br i1 %21, label %22, label %23

; <label>:22                                      ; preds = %10
  %putchar2 = tail call i32 @putchar(i32 49) #6
  br label %36

; <label>:23                                      ; preds = %10
  %24 = xor i64 %16, %14
  %25 = icmp ult i64 %14, %16
  %26 = select i1 %25, i64 %24, i64 0
  %27 = xor i64 %26, %14
  %28 = bitcast i8* %pdest to i64*
  %29 = load i64* %28, align 8, !tbaa !238
  %int_cast_to_i643 = bitcast i64 52 to i64
  call void @klee_overshift_check(i64 64, i64 %int_cast_to_i643)
  %30 = lshr i64 %29, 52
  %31 = and i64 %30, 2047
  %32 = sub nsw i64 %27, %31
  %33 = icmp sgt i64 %32, 40
  br i1 %33, label %34, label %35

; <label>:34                                      ; preds = %23
  %putchar1 = tail call i32 @putchar(i32 48) #6
  br label %36

; <label>:35                                      ; preds = %23
  %putchar = tail call i32 @putchar(i32 45) #6
  br label %36

; <label>:36                                      ; preds = %35, %34, %22, %0
  ret void
}

; Function Attrs: nounwind uwtable
define void @cancel_injection(i8* nocapture readonly %psrc1, i8* nocapture readonly %psrc2, i8* nocapture readonly %pdest) #3 {
  %1 = bitcast i8* %psrc1 to i64*
  %2 = load i64* %1, align 8, !tbaa !238
  %int_cast_to_i64 = bitcast i64 52 to i64
  call void @klee_overshift_check(i64 64, i64 %int_cast_to_i64)
  %3 = lshr i64 %2, 52
  %4 = and i64 %3, 2047
  %5 = bitcast i8* %psrc2 to i64*
  %6 = load i64* %5, align 8, !tbaa !238
  %int_cast_to_i641 = bitcast i64 52 to i64
  call void @klee_overshift_check(i64 64, i64 %int_cast_to_i641)
  %7 = lshr i64 %6, 52
  %8 = and i64 %7, 2047
  %9 = xor i64 %8, %4
  %10 = icmp ult i64 %4, %8
  %11 = select i1 %10, i64 %9, i64 0
  %12 = xor i64 %11, %4
  %13 = bitcast i8* %pdest to i64*
  %14 = load i64* %13, align 8, !tbaa !238
  %int_cast_to_i642 = bitcast i64 52 to i64
  call void @klee_overshift_check(i64 64, i64 %int_cast_to_i642)
  %15 = lshr i64 %14, 52
  %16 = and i64 %15, 2047
  %17 = sub nsw i64 %12, %16
  %18 = icmp sgt i64 %17, 40
  %19 = bitcast i64 %2 to double
  %20 = tail call i32 @klee_internal_fpclassify(double %19) #10
  %21 = icmp eq i32 %20, 4
  %22 = and i1 %18, %21
  %23 = bitcast i64 %6 to double
  %24 = tail call i32 @klee_internal_fpclassify(double %23) #10
  %25 = icmp eq i32 %24, 4
  %26 = and i1 %22, %25
  br i1 %26, label %27, label %28

; <label>:27                                      ; preds = %0
  %putchar1 = tail call i32 @putchar(i32 48) #6
  br label %29

; <label>:28                                      ; preds = %0
  %putchar = tail call i32 @putchar(i32 42) #6
  br label %29

; <label>:29                                      ; preds = %28, %27
  ret void
}

; Function Attrs: nounwind uwtable
define void @round_injection(i8* nocapture readonly %psrc1, i8* nocapture readonly %psrc2, i8* nocapture readnone %pdest) #3 {
  %1 = bitcast i8* %psrc1 to i64*
  %2 = load i64* %1, align 8, !tbaa !238
  %int_cast_to_i64 = bitcast i64 52 to i64
  call void @klee_overshift_check(i64 64, i64 %int_cast_to_i64)
  %3 = lshr i64 %2, 52
  %4 = and i64 %3, 2047
  %5 = bitcast i8* %psrc2 to i64*
  %6 = load i64* %5, align 8, !tbaa !238
  %int_cast_to_i641 = bitcast i64 52 to i64
  call void @klee_overshift_check(i64 64, i64 %int_cast_to_i641)
  %7 = lshr i64 %6, 52
  %8 = and i64 %7, 2047
  %9 = sub nsw i64 %4, %8
  %int_cast_to_i642 = bitcast i64 63 to i64
  call void @klee_overshift_check(i64 64, i64 %int_cast_to_i642)
  %10 = ashr i64 %9, 63
  %11 = add nsw i64 %10, %9
  %12 = xor i64 %11, %10
  %13 = icmp sgt i64 %12, 32
  %14 = bitcast i64 %2 to double
  %15 = tail call i32 @klee_internal_fpclassify(double %14) #10
  %16 = icmp eq i32 %15, 4
  %17 = and i1 %13, %16
  %18 = bitcast i64 %6 to double
  %19 = tail call i32 @klee_internal_fpclassify(double %18) #10
  %20 = icmp eq i32 %19, 4
  %21 = and i1 %17, %20
  br i1 %21, label %22, label %23

; <label>:22                                      ; preds = %0
  %putchar1 = tail call i32 @putchar(i32 49) #6
  br label %24

; <label>:23                                      ; preds = %0
  %putchar = tail call i32 @putchar(i32 35) #6
  br label %24

; <label>:24                                      ; preds = %23, %22
  ret void
}

; Function Attrs: nounwind uwtable
define void @log_sampled_fp_injection(i8* nocapture readonly %psrc1, i8* nocapture readonly %psrc2, i8* nocapture readonly %pdest, i32* nocapture %pcounter, i32 %step, i32 %injection) #3 {
  %1 = load i32* %pcounter, align 4, !tbaa !240
  %2 = icmp eq i32 %1, 2147483647
  br i1 %2, label %round_injection.exit, label %3

; <label>:3                                       ; preds = %0
  %4 = add nsw i32 %1, 1
  store i32 %4, i32* %pcounter, align 4, !tbaa !240
  %5 = sitofp i32 %4 to double
  %6 = tail call double @log10(double %5) #6
  %7 = tail call double @ceil(double %6) #10
  %8 = tail call double @pow(double 1.000000e+01, double %7) #6
  %9 = fptosi double %8 to i32
  %10 = icmp eq i32 %9, 1
  %11 = load i32* %pcounter, align 4, !tbaa !240
  %int_cast_to_i64 = zext i32 10 to i64
  call void @klee_div_zero_check(i64 %int_cast_to_i64)
  %.op = sdiv i32 %9, 10
  %12 = select i1 %10, i32 1, i32 %.op
  %13 = mul nsw i32 %12, %step
  %int_cast_to_i641 = zext i32 %13 to i64
  call void @klee_div_zero_check(i64 %int_cast_to_i641)
  %14 = srem i32 %11, %13
  %15 = icmp eq i32 %14, 0
  br i1 %15, label %16, label %round_injection.exit

; <label>:16                                      ; preds = %3
  switch i32 %injection, label %round_injection.exit [
    i32 2, label %17
    i32 0, label %18
    i32 1, label %19
  ]

; <label>:17                                      ; preds = %16
  tail call void @fp_injection(i8* %psrc1, i8* %psrc2, i8* %pdest)
  br label %round_injection.exit

; <label>:18                                      ; preds = %16
  tail call void @cancel_injection(i8* %psrc1, i8* %psrc2, i8* %pdest)
  br label %round_injection.exit

; <label>:19                                      ; preds = %16
  %20 = bitcast i8* %psrc1 to i64*
  %21 = load i64* %20, align 8, !tbaa !238
  %int_cast_to_i642 = bitcast i64 52 to i64
  call void @klee_overshift_check(i64 64, i64 %int_cast_to_i642)
  %22 = lshr i64 %21, 52
  %23 = and i64 %22, 2047
  %24 = bitcast i8* %psrc2 to i64*
  %25 = load i64* %24, align 8, !tbaa !238
  %int_cast_to_i643 = bitcast i64 52 to i64
  call void @klee_overshift_check(i64 64, i64 %int_cast_to_i643)
  %26 = lshr i64 %25, 52
  %27 = and i64 %26, 2047
  %28 = sub nsw i64 %23, %27
  %int_cast_to_i644 = bitcast i64 63 to i64
  call void @klee_overshift_check(i64 64, i64 %int_cast_to_i644)
  %29 = ashr i64 %28, 63
  %30 = add nsw i64 %29, %28
  %31 = xor i64 %30, %29
  %32 = icmp sgt i64 %31, 32
  %33 = bitcast i64 %21 to double
  %34 = tail call i32 @klee_internal_fpclassify(double %33) #10
  %35 = icmp eq i32 %34, 4
  %36 = and i1 %32, %35
  %37 = bitcast i64 %25 to double
  %38 = tail call i32 @klee_internal_fpclassify(double %37) #10
  %39 = icmp eq i32 %38, 4
  %40 = and i1 %36, %39
  br i1 %40, label %41, label %42

; <label>:41                                      ; preds = %19
  %putchar1.i = tail call i32 @putchar(i32 49) #6
  br label %round_injection.exit

; <label>:42                                      ; preds = %19
  %putchar.i = tail call i32 @putchar(i32 35) #6
  br label %round_injection.exit

round_injection.exit:                             ; preds = %42, %41, %18, %17, %16, %3, %0
  ret void
}

; Function Attrs: nounwind
declare double @pow(double, double) #4

; Function Attrs: nounwind readnone
declare double @ceil(double) #5

; Function Attrs: nounwind
declare double @log10(double) #4

; Function Attrs: nounwind uwtable
define void @uniform_sampled_fp_injection(i8* nocapture readonly %psrc1, i8* nocapture readonly %psrc2, i8* nocapture readonly %pdest, i32* nocapture %pcounter, i32 %step, i32 %injection) #3 {
  %1 = load i32* %pcounter, align 4, !tbaa !240
  %2 = icmp eq i32 %1, 2147483647
  br i1 %2, label %round_injection.exit, label %3

; <label>:3                                       ; preds = %0
  %4 = add nsw i32 %1, 1
  store i32 %4, i32* %pcounter, align 4, !tbaa !240
  %int_cast_to_i64 = zext i32 %step to i64
  call void @klee_div_zero_check(i64 %int_cast_to_i64)
  %5 = srem i32 %4, %step
  %6 = icmp eq i32 %5, 0
  br i1 %6, label %7, label %round_injection.exit

; <label>:7                                       ; preds = %3
  switch i32 %injection, label %round_injection.exit [
    i32 2, label %8
    i32 0, label %9
    i32 1, label %10
  ]

; <label>:8                                       ; preds = %7
  tail call void @fp_injection(i8* %psrc1, i8* %psrc2, i8* %pdest)
  br label %round_injection.exit

; <label>:9                                       ; preds = %7
  tail call void @cancel_injection(i8* %psrc1, i8* %psrc2, i8* %pdest)
  br label %round_injection.exit

; <label>:10                                      ; preds = %7
  %11 = bitcast i8* %psrc1 to i64*
  %12 = load i64* %11, align 8, !tbaa !238
  %int_cast_to_i641 = bitcast i64 52 to i64
  call void @klee_overshift_check(i64 64, i64 %int_cast_to_i641)
  %13 = lshr i64 %12, 52
  %14 = and i64 %13, 2047
  %15 = bitcast i8* %psrc2 to i64*
  %16 = load i64* %15, align 8, !tbaa !238
  %int_cast_to_i642 = bitcast i64 52 to i64
  call void @klee_overshift_check(i64 64, i64 %int_cast_to_i642)
  %17 = lshr i64 %16, 52
  %18 = and i64 %17, 2047
  %19 = sub nsw i64 %14, %18
  %int_cast_to_i643 = bitcast i64 63 to i64
  call void @klee_overshift_check(i64 64, i64 %int_cast_to_i643)
  %20 = ashr i64 %19, 63
  %21 = add nsw i64 %20, %19
  %22 = xor i64 %21, %20
  %23 = icmp sgt i64 %22, 32
  %24 = bitcast i64 %12 to double
  %25 = tail call i32 @klee_internal_fpclassify(double %24) #10
  %26 = icmp eq i32 %25, 4
  %27 = and i1 %23, %26
  %28 = bitcast i64 %16 to double
  %29 = tail call i32 @klee_internal_fpclassify(double %28) #10
  %30 = icmp eq i32 %29, 4
  %31 = and i1 %27, %30
  br i1 %31, label %32, label %33

; <label>:32                                      ; preds = %10
  %putchar1.i = tail call i32 @putchar(i32 49) #6
  br label %round_injection.exit

; <label>:33                                      ; preds = %10
  %putchar.i = tail call i32 @putchar(i32 35) #6
  br label %round_injection.exit

round_injection.exit:                             ; preds = %33, %32, %9, %8, %7, %3, %0
  ret void
}

; Function Attrs: nounwind
declare i32 @putchar(i32) #6

declare zeroext i1 @klee_is_infinite_float(float) #7

declare zeroext i1 @klee_is_infinite_double(double) #7

declare zeroext i1 @klee_is_infinite_long_double(x86_fp80) #7

; Function Attrs: noinline nounwind optnone uwtable
define i32 @klee_internal_isinff(float %f) #8 {
entry:
  %isinf = tail call zeroext i1 @klee_is_infinite_float(float %f) #12
  %cmp = fcmp ogt float %f, 0.000000e+00
  %posOrNeg = select i1 %cmp, i32 1, i32 -1
  %result = select i1 %isinf, i32 %posOrNeg, i32 0
  ret i32 %result
}

; Function Attrs: noinline nounwind optnone uwtable
define i32 @klee_internal_isinf(double %d) #8 {
entry:
  %isinf = tail call zeroext i1 @klee_is_infinite_double(double %d) #12
  %cmp = fcmp ogt double %d, 0.000000e+00
  %posOrNeg = select i1 %cmp, i32 1, i32 -1
  %result = select i1 %isinf, i32 %posOrNeg, i32 0
  ret i32 %result
}

; Function Attrs: noinline optnone
define i32 @klee_internal_isinfl(x86_fp80 %d) #9 {
entry:
  %isinf = tail call zeroext i1 @klee_is_infinite_long_double(x86_fp80 %d) #12
  %cmp = fcmp ogt x86_fp80 %d, 0xK00000000000000000000
  %posOrNeg = select i1 %cmp, i32 1, i32 -1
  %result = select i1 %isinf, i32 %posOrNeg, i32 0
  ret i32 %result
}

; Function Attrs: nounwind uwtable
define double @klee_internal_fabs(double %d) #3 {
  %1 = tail call double @klee_abs_double(double %d) #12, !dbg !242
  ret double %1, !dbg !242
}

declare double @klee_abs_double(double) #7

; Function Attrs: nounwind uwtable
define float @klee_internal_fabsf(float %f) #3 {
  %1 = tail call float @klee_abs_float(float %f) #12, !dbg !243
  ret float %1, !dbg !243
}

declare float @klee_abs_float(float) #7

; Function Attrs: nounwind uwtable
define x86_fp80 @klee_internal_fabsl(x86_fp80 %f) #3 {
  %1 = tail call x86_fp80 @klee_abs_long_double(x86_fp80 %f) #12, !dbg !244
  ret x86_fp80 %1, !dbg !244
}

declare x86_fp80 @klee_abs_long_double(x86_fp80) #7

; Function Attrs: nounwind readnone
declare void @llvm.dbg.value(metadata, i64, metadata) #10

; Function Attrs: nounwind uwtable
define i32 @klee_internal_fegetround() #3 {
  %1 = tail call i32 (...)* @klee_get_rounding_mode() #12, !dbg !245
  %2 = icmp ult i32 %1, 5, !dbg !246
  br i1 %2, label %switch.lookup, label %4, !dbg !246

switch.lookup:                                    ; preds = %0
  %3 = sext i32 %1 to i64, !dbg !246
  %switch.gep = getelementptr inbounds [5 x i32]* @switch.table, i64 0, i64 %3, !dbg !246
  %switch.load = load i32* %switch.gep, align 4, !dbg !246
  ret i32 %switch.load, !dbg !246

; <label>:4                                       ; preds = %0
  ret i32 -1, !dbg !247
}

declare i32 @klee_get_rounding_mode(...) #7

; Function Attrs: nounwind uwtable
define i32 @klee_internal_fesetround(i32 %rm) #3 {
  switch i32 %rm, label %5 [
    i32 0, label %1
    i32 2048, label %2
    i32 1024, label %3
    i32 3072, label %4
  ], !dbg !248

; <label>:1                                       ; preds = %0
  tail call void @klee_set_rounding_mode(i32 0) #12, !dbg !249
  br label %5, !dbg !251

; <label>:2                                       ; preds = %0
  tail call void @klee_set_rounding_mode(i32 2) #12, !dbg !252
  br label %5, !dbg !253

; <label>:3                                       ; preds = %0
  tail call void @klee_set_rounding_mode(i32 3) #12, !dbg !254
  br label %5, !dbg !255

; <label>:4                                       ; preds = %0
  tail call void @klee_set_rounding_mode(i32 4) #12, !dbg !256
  br label %5, !dbg !257

; <label>:5                                       ; preds = %4, %3, %2, %1, %0
  %.0 = phi i32 [ -1, %0 ], [ 0, %4 ], [ 0, %3 ], [ 0, %2 ], [ 0, %1 ]
  ret i32 %.0, !dbg !258
}

; Function Attrs: nounwind uwtable
define i32 @klee_internal_isnanf(float %f) #3 {
  %1 = tail call zeroext i1 @klee_is_nan_float(float %f) #12, !dbg !259
  %2 = zext i1 %1 to i32, !dbg !259
  ret i32 %2, !dbg !259
}

declare zeroext i1 @klee_is_nan_float(float) #7

; Function Attrs: nounwind uwtable
define i32 @klee_internal_isnan(double %d) #3 {
  %1 = tail call zeroext i1 @klee_is_nan_double(double %d) #12, !dbg !260
  %2 = zext i1 %1 to i32, !dbg !260
  ret i32 %2, !dbg !260
}

declare zeroext i1 @klee_is_nan_double(double) #7

; Function Attrs: nounwind uwtable
define i32 @klee_internal_isnanl(x86_fp80 %d) #3 {
  %1 = tail call zeroext i1 @klee_is_nan_long_double(x86_fp80 %d) #12, !dbg !261
  %2 = zext i1 %1 to i32, !dbg !261
  ret i32 %2, !dbg !261
}

declare zeroext i1 @klee_is_nan_long_double(x86_fp80) #7

; Function Attrs: nounwind uwtable
define i32 @klee_internal_fpclassifyf(float %f) #3 {
  %1 = tail call zeroext i1 @klee_is_nan_float(float %f) #12, !dbg !262
  br i1 %1, label %8, label %2, !dbg !262

; <label>:2                                       ; preds = %0
  %3 = tail call zeroext i1 @klee_is_infinite_float(float %f) #12, !dbg !264
  br i1 %3, label %8, label %4, !dbg !264

; <label>:4                                       ; preds = %2
  %5 = fcmp oeq float %f, 0.000000e+00, !dbg !266
  br i1 %5, label %8, label %6, !dbg !266

; <label>:6                                       ; preds = %4
  %7 = tail call zeroext i1 @klee_is_normal_float(float %f) #12, !dbg !268
  %. = select i1 %7, i32 4, i32 3, !dbg !270
  br label %8, !dbg !270

; <label>:8                                       ; preds = %6, %4, %2, %0
  %.0 = phi i32 [ 0, %0 ], [ 1, %2 ], [ 2, %4 ], [ %., %6 ]
  ret i32 %.0, !dbg !272
}

declare zeroext i1 @klee_is_normal_float(float) #7

; Function Attrs: nounwind uwtable
define i32 @klee_internal_fpclassify(double %f) #3 {
  %1 = tail call zeroext i1 @klee_is_nan_double(double %f) #12, !dbg !273
  br i1 %1, label %8, label %2, !dbg !273

; <label>:2                                       ; preds = %0
  %3 = tail call zeroext i1 @klee_is_infinite_double(double %f) #12, !dbg !275
  br i1 %3, label %8, label %4, !dbg !275

; <label>:4                                       ; preds = %2
  %5 = fcmp oeq double %f, 0.000000e+00, !dbg !277
  br i1 %5, label %8, label %6, !dbg !277

; <label>:6                                       ; preds = %4
  %7 = tail call zeroext i1 @klee_is_normal_double(double %f) #12, !dbg !279
  %. = select i1 %7, i32 4, i32 3, !dbg !281
  br label %8, !dbg !281

; <label>:8                                       ; preds = %6, %4, %2, %0
  %.0 = phi i32 [ 0, %0 ], [ 1, %2 ], [ 2, %4 ], [ %., %6 ]
  ret i32 %.0, !dbg !283
}

declare zeroext i1 @klee_is_normal_double(double) #7

; Function Attrs: nounwind uwtable
define i32 @klee_internal_fpclassifyl(x86_fp80 %ld) #3 {
  %1 = tail call zeroext i1 @klee_is_nan_long_double(x86_fp80 %ld) #12, !dbg !284
  br i1 %1, label %8, label %2, !dbg !284

; <label>:2                                       ; preds = %0
  %3 = tail call zeroext i1 @klee_is_infinite_long_double(x86_fp80 %ld) #12, !dbg !286
  br i1 %3, label %8, label %4, !dbg !286

; <label>:4                                       ; preds = %2
  %5 = fcmp oeq x86_fp80 %ld, 0xK00000000000000000000, !dbg !288
  br i1 %5, label %8, label %6, !dbg !288

; <label>:6                                       ; preds = %4
  %7 = tail call zeroext i1 @klee_is_normal_long_double(x86_fp80 %ld) #12, !dbg !290
  %. = select i1 %7, i32 4, i32 3, !dbg !292
  br label %8, !dbg !292

; <label>:8                                       ; preds = %6, %4, %2, %0
  %.0 = phi i32 [ 0, %0 ], [ 1, %2 ], [ 2, %4 ], [ %., %6 ]
  ret i32 %.0, !dbg !294
}

declare zeroext i1 @klee_is_normal_long_double(x86_fp80) #7

; Function Attrs: nounwind uwtable
define i32 @klee_internal_finitef(float %f) #3 {
  %1 = tail call zeroext i1 @klee_is_nan_float(float %f) #12, !dbg !295
  %2 = zext i1 %1 to i32, !dbg !295
  %3 = xor i32 %2, 1, !dbg !295
  %4 = tail call zeroext i1 @klee_is_infinite_float(float %f) #12, !dbg !295
  %5 = zext i1 %4 to i32, !dbg !295
  %6 = xor i32 %5, 1, !dbg !295
  %7 = and i32 %6, %3, !dbg !295
  ret i32 %7, !dbg !295
}

; Function Attrs: nounwind uwtable
define i32 @klee_internal_finite(double %f) #3 {
  %1 = tail call zeroext i1 @klee_is_nan_double(double %f) #12, !dbg !296
  %2 = zext i1 %1 to i32, !dbg !296
  %3 = xor i32 %2, 1, !dbg !296
  %4 = tail call zeroext i1 @klee_is_infinite_double(double %f) #12, !dbg !296
  %5 = zext i1 %4 to i32, !dbg !296
  %6 = xor i32 %5, 1, !dbg !296
  %7 = and i32 %6, %3, !dbg !296
  ret i32 %7, !dbg !296
}

; Function Attrs: nounwind uwtable
define i32 @klee_internal_finitel(x86_fp80 %f) #3 {
  %1 = tail call zeroext i1 @klee_is_nan_long_double(x86_fp80 %f) #12, !dbg !297
  %2 = zext i1 %1 to i32, !dbg !297
  %3 = xor i32 %2, 1, !dbg !297
  %4 = tail call zeroext i1 @klee_is_infinite_long_double(x86_fp80 %f) #12, !dbg !297
  %5 = zext i1 %4 to i32, !dbg !297
  %6 = xor i32 %5, 1, !dbg !297
  %7 = and i32 %6, %3, !dbg !297
  ret i32 %7, !dbg !297
}

; Function Attrs: nounwind uwtable
define void @klee_div_zero_check(i64 %z) #3 {
  %1 = icmp eq i64 %z, 0, !dbg !298
  br i1 %1, label %2, label %3, !dbg !298

; <label>:2                                       ; preds = %0
  tail call void @klee_report_error(i8* getelementptr inbounds ([81 x i8]* @.str2, i64 0, i64 0), i32 14, i8* getelementptr inbounds ([15 x i8]* @.str13, i64 0, i64 0), i8* getelementptr inbounds ([8 x i8]* @.str24, i64 0, i64 0)) #13, !dbg !300
  unreachable, !dbg !300

; <label>:3                                       ; preds = %0
  ret void, !dbg !301
}

; Function Attrs: noreturn
declare void @klee_report_error(i8*, i32, i8*, i8*) #11

; Function Attrs: nounwind uwtable
define i32 @klee_int(i8* %name) #3 {
  %x = alloca i32, align 4
  %1 = bitcast i32* %x to i8*, !dbg !302
  call void @klee_make_symbolic(i8* %1, i64 4, i8* %name) #12, !dbg !302
  %2 = load i32* %x, align 4, !dbg !303, !tbaa !240
  ret i32 %2, !dbg !303
}

; Function Attrs: nounwind readnone
declare void @llvm.dbg.declare(metadata, metadata) #10

; Function Attrs: nounwind uwtable
define void @klee_overshift_check(i64 %bitWidth, i64 %shift) #3 {
  %1 = icmp ult i64 %shift, %bitWidth, !dbg !304
  br i1 %1, label %3, label %2, !dbg !304

; <label>:2                                       ; preds = %0
  tail call void @klee_report_error(i8* getelementptr inbounds ([8 x i8]* @.str3, i64 0, i64 0), i32 0, i8* getelementptr inbounds ([16 x i8]* @.str14, i64 0, i64 0), i8* getelementptr inbounds ([14 x i8]* @.str25, i64 0, i64 0)) #13, !dbg !306
  unreachable, !dbg !306

; <label>:3                                       ; preds = %0
  ret void, !dbg !308
}

; Function Attrs: nounwind uwtable
define i32 @klee_range(i32 %start, i32 %end, i8* %name) #3 {
  %x = alloca i32, align 4
  %1 = icmp slt i32 %start, %end, !dbg !309
  br i1 %1, label %3, label %2, !dbg !309

; <label>:2                                       ; preds = %0
  call void @klee_report_error(i8* getelementptr inbounds ([72 x i8]* @.str6, i64 0, i64 0), i32 17, i8* getelementptr inbounds ([14 x i8]* @.str17, i64 0, i64 0), i8* getelementptr inbounds ([5 x i8]* @.str28, i64 0, i64 0)) #13, !dbg !311
  unreachable, !dbg !311

; <label>:3                                       ; preds = %0
  %4 = add nsw i32 %start, 1, !dbg !312
  %5 = icmp eq i32 %4, %end, !dbg !312
  br i1 %5, label %21, label %6, !dbg !312

; <label>:6                                       ; preds = %3
  %7 = bitcast i32* %x to i8*, !dbg !314
  call void @klee_make_symbolic(i8* %7, i64 4, i8* %name) #12, !dbg !314
  %8 = icmp eq i32 %start, 0, !dbg !316
  %9 = load i32* %x, align 4, !dbg !318, !tbaa !240
  br i1 %8, label %10, label %13, !dbg !316

; <label>:10                                      ; preds = %6
  %11 = icmp ult i32 %9, %end, !dbg !318
  %12 = zext i1 %11 to i64, !dbg !318
  call void @klee_assume(i64 %12) #12, !dbg !318
  br label %19, !dbg !320

; <label>:13                                      ; preds = %6
  %14 = icmp sge i32 %9, %start, !dbg !321
  %15 = zext i1 %14 to i64, !dbg !321
  call void @klee_assume(i64 %15) #12, !dbg !321
  %16 = load i32* %x, align 4, !dbg !323, !tbaa !240
  %17 = icmp slt i32 %16, %end, !dbg !323
  %18 = zext i1 %17 to i64, !dbg !323
  call void @klee_assume(i64 %18) #12, !dbg !323
  br label %19

; <label>:19                                      ; preds = %13, %10
  %20 = load i32* %x, align 4, !dbg !324, !tbaa !240
  br label %21, !dbg !324

; <label>:21                                      ; preds = %19, %3
  %.0 = phi i32 [ %20, %19 ], [ %start, %3 ]
  ret i32 %.0, !dbg !325
}

declare void @klee_assume(i64) #7

; Function Attrs: nounwind uwtable
define void @klee_set_rounding_mode(i32 %rm) #3 {
  switch i32 %rm, label %6 [
    i32 0, label %1
    i32 1, label %2
    i32 2, label %3
    i32 3, label %4
    i32 4, label %5
  ], !dbg !326

; <label>:1                                       ; preds = %0
  tail call void @klee_set_rounding_mode_internal(i32 0) #12, !dbg !327
  br label %7, !dbg !327

; <label>:2                                       ; preds = %0
  tail call void @klee_set_rounding_mode_internal(i32 1) #12, !dbg !329
  br label %7, !dbg !329

; <label>:3                                       ; preds = %0
  tail call void @klee_set_rounding_mode_internal(i32 2) #12, !dbg !330
  br label %7, !dbg !330

; <label>:4                                       ; preds = %0
  tail call void @klee_set_rounding_mode_internal(i32 3) #12, !dbg !331
  br label %7, !dbg !331

; <label>:5                                       ; preds = %0
  tail call void @klee_set_rounding_mode_internal(i32 4) #12, !dbg !332
  br label %7, !dbg !332

; <label>:6                                       ; preds = %0
  tail call void @klee_report_error(i8* getelementptr inbounds ([84 x i8]* @.str9, i64 0, i64 0), i32 31, i8* getelementptr inbounds ([22 x i8]* @.str110, i64 0, i64 0), i8* getelementptr inbounds ([1 x i8]* @.str211, i64 0, i64 0)) #13, !dbg !333
  unreachable, !dbg !333

; <label>:7                                       ; preds = %5, %4, %3, %2, %1
  ret void, !dbg !334
}

declare void @klee_set_rounding_mode_internal(i32) #7

; Function Attrs: nounwind uwtable
define weak i8* @memcpy(i8* %destaddr, i8* %srcaddr, i64 %len) #3 {
  %1 = icmp eq i64 %len, 0, !dbg !335
  br i1 %1, label %._crit_edge, label %.lr.ph.preheader, !dbg !335

.lr.ph.preheader:                                 ; preds = %0
  %n.vec = and i64 %len, -32
  %cmp.zero = icmp eq i64 %n.vec, 0
  %2 = add i64 %len, -1
  br i1 %cmp.zero, label %middle.block, label %vector.memcheck

vector.memcheck:                                  ; preds = %.lr.ph.preheader
  %scevgep4 = getelementptr i8* %srcaddr, i64 %2
  %scevgep = getelementptr i8* %destaddr, i64 %2
  %bound1 = icmp uge i8* %scevgep, %srcaddr
  %bound0 = icmp uge i8* %scevgep4, %destaddr
  %memcheck.conflict = and i1 %bound0, %bound1
  %ptr.ind.end = getelementptr i8* %srcaddr, i64 %n.vec
  %ptr.ind.end6 = getelementptr i8* %destaddr, i64 %n.vec
  %rev.ind.end = sub i64 %len, %n.vec
  br i1 %memcheck.conflict, label %middle.block, label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.memcheck
  %index = phi i64 [ %index.next, %vector.body ], [ 0, %vector.memcheck ]
  %next.gep = getelementptr i8* %srcaddr, i64 %index
  %next.gep103 = getelementptr i8* %destaddr, i64 %index
  %3 = bitcast i8* %next.gep to <16 x i8>*, !dbg !336
  %wide.load = load <16 x i8>* %3, align 1, !dbg !336
  %next.gep.sum279 = or i64 %index, 16, !dbg !336
  %4 = getelementptr i8* %srcaddr, i64 %next.gep.sum279, !dbg !336
  %5 = bitcast i8* %4 to <16 x i8>*, !dbg !336
  %wide.load200 = load <16 x i8>* %5, align 1, !dbg !336
  %6 = bitcast i8* %next.gep103 to <16 x i8>*, !dbg !336
  store <16 x i8> %wide.load, <16 x i8>* %6, align 1, !dbg !336
  %next.gep103.sum296 = or i64 %index, 16, !dbg !336
  %7 = getelementptr i8* %destaddr, i64 %next.gep103.sum296, !dbg !336
  %8 = bitcast i8* %7 to <16 x i8>*, !dbg !336
  store <16 x i8> %wide.load200, <16 x i8>* %8, align 1, !dbg !336
  %index.next = add i64 %index, 32
  %9 = icmp eq i64 %index.next, %n.vec
  br i1 %9, label %middle.block, label %vector.body, !llvm.loop !337

middle.block:                                     ; preds = %vector.body, %vector.memcheck, %.lr.ph.preheader
  %resume.val = phi i8* [ %srcaddr, %.lr.ph.preheader ], [ %srcaddr, %vector.memcheck ], [ %ptr.ind.end, %vector.body ]
  %resume.val5 = phi i8* [ %destaddr, %.lr.ph.preheader ], [ %destaddr, %vector.memcheck ], [ %ptr.ind.end6, %vector.body ]
  %resume.val7 = phi i64 [ %len, %.lr.ph.preheader ], [ %len, %vector.memcheck ], [ %rev.ind.end, %vector.body ]
  %new.indc.resume.val = phi i64 [ 0, %.lr.ph.preheader ], [ 0, %vector.memcheck ], [ %n.vec, %vector.body ]
  %cmp.n = icmp eq i64 %new.indc.resume.val, %len
  br i1 %cmp.n, label %._crit_edge, label %.lr.ph

.lr.ph:                                           ; preds = %.lr.ph, %middle.block
  %src.03 = phi i8* [ %11, %.lr.ph ], [ %resume.val, %middle.block ]
  %dest.02 = phi i8* [ %13, %.lr.ph ], [ %resume.val5, %middle.block ]
  %.01 = phi i64 [ %10, %.lr.ph ], [ %resume.val7, %middle.block ]
  %10 = add i64 %.01, -1, !dbg !335
  %11 = getelementptr inbounds i8* %src.03, i64 1, !dbg !336
  %12 = load i8* %src.03, align 1, !dbg !336, !tbaa !340
  %13 = getelementptr inbounds i8* %dest.02, i64 1, !dbg !336
  store i8 %12, i8* %dest.02, align 1, !dbg !336, !tbaa !340
  %14 = icmp eq i64 %10, 0, !dbg !335
  br i1 %14, label %._crit_edge, label %.lr.ph, !dbg !335, !llvm.loop !341

._crit_edge:                                      ; preds = %.lr.ph, %middle.block, %0
  ret i8* %destaddr, !dbg !342
}

; Function Attrs: nounwind uwtable
define weak i8* @memmove(i8* %dst, i8* %src, i64 %count) #3 {
  %1 = icmp eq i8* %src, %dst, !dbg !343
  br i1 %1, label %.loopexit, label %2, !dbg !343

; <label>:2                                       ; preds = %0
  %3 = icmp ugt i8* %src, %dst, !dbg !345
  br i1 %3, label %.preheader, label %18, !dbg !345

.preheader:                                       ; preds = %2
  %4 = icmp eq i64 %count, 0, !dbg !347
  br i1 %4, label %.loopexit, label %.lr.ph.preheader, !dbg !347

.lr.ph.preheader:                                 ; preds = %.preheader
  %n.vec = and i64 %count, -32
  %cmp.zero = icmp eq i64 %n.vec, 0
  %5 = add i64 %count, -1
  br i1 %cmp.zero, label %middle.block, label %vector.memcheck

vector.memcheck:                                  ; preds = %.lr.ph.preheader
  %scevgep11 = getelementptr i8* %src, i64 %5
  %scevgep = getelementptr i8* %dst, i64 %5
  %bound1 = icmp uge i8* %scevgep, %src
  %bound0 = icmp uge i8* %scevgep11, %dst
  %memcheck.conflict = and i1 %bound0, %bound1
  %ptr.ind.end = getelementptr i8* %src, i64 %n.vec
  %ptr.ind.end13 = getelementptr i8* %dst, i64 %n.vec
  %rev.ind.end = sub i64 %count, %n.vec
  br i1 %memcheck.conflict, label %middle.block, label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.memcheck
  %index = phi i64 [ %index.next, %vector.body ], [ 0, %vector.memcheck ]
  %next.gep = getelementptr i8* %src, i64 %index
  %next.gep110 = getelementptr i8* %dst, i64 %index
  %6 = bitcast i8* %next.gep to <16 x i8>*, !dbg !347
  %wide.load = load <16 x i8>* %6, align 1, !dbg !347
  %next.gep.sum586 = or i64 %index, 16, !dbg !347
  %7 = getelementptr i8* %src, i64 %next.gep.sum586, !dbg !347
  %8 = bitcast i8* %7 to <16 x i8>*, !dbg !347
  %wide.load207 = load <16 x i8>* %8, align 1, !dbg !347
  %9 = bitcast i8* %next.gep110 to <16 x i8>*, !dbg !347
  store <16 x i8> %wide.load, <16 x i8>* %9, align 1, !dbg !347
  %next.gep110.sum603 = or i64 %index, 16, !dbg !347
  %10 = getelementptr i8* %dst, i64 %next.gep110.sum603, !dbg !347
  %11 = bitcast i8* %10 to <16 x i8>*, !dbg !347
  store <16 x i8> %wide.load207, <16 x i8>* %11, align 1, !dbg !347
  %index.next = add i64 %index, 32
  %12 = icmp eq i64 %index.next, %n.vec
  br i1 %12, label %middle.block, label %vector.body, !llvm.loop !349

middle.block:                                     ; preds = %vector.body, %vector.memcheck, %.lr.ph.preheader
  %resume.val = phi i8* [ %src, %.lr.ph.preheader ], [ %src, %vector.memcheck ], [ %ptr.ind.end, %vector.body ]
  %resume.val12 = phi i8* [ %dst, %.lr.ph.preheader ], [ %dst, %vector.memcheck ], [ %ptr.ind.end13, %vector.body ]
  %resume.val14 = phi i64 [ %count, %.lr.ph.preheader ], [ %count, %vector.memcheck ], [ %rev.ind.end, %vector.body ]
  %new.indc.resume.val = phi i64 [ 0, %.lr.ph.preheader ], [ 0, %vector.memcheck ], [ %n.vec, %vector.body ]
  %cmp.n = icmp eq i64 %new.indc.resume.val, %count
  br i1 %cmp.n, label %.loopexit, label %.lr.ph

.lr.ph:                                           ; preds = %.lr.ph, %middle.block
  %b.04 = phi i8* [ %14, %.lr.ph ], [ %resume.val, %middle.block ]
  %a.03 = phi i8* [ %16, %.lr.ph ], [ %resume.val12, %middle.block ]
  %.02 = phi i64 [ %13, %.lr.ph ], [ %resume.val14, %middle.block ]
  %13 = add i64 %.02, -1, !dbg !347
  %14 = getelementptr inbounds i8* %b.04, i64 1, !dbg !347
  %15 = load i8* %b.04, align 1, !dbg !347, !tbaa !340
  %16 = getelementptr inbounds i8* %a.03, i64 1, !dbg !347
  store i8 %15, i8* %a.03, align 1, !dbg !347, !tbaa !340
  %17 = icmp eq i64 %13, 0, !dbg !347
  br i1 %17, label %.loopexit, label %.lr.ph, !dbg !347, !llvm.loop !350

; <label>:18                                      ; preds = %2
  %19 = add i64 %count, -1, !dbg !351
  %20 = icmp eq i64 %count, 0, !dbg !353
  br i1 %20, label %.loopexit, label %.lr.ph9, !dbg !353

.lr.ph9:                                          ; preds = %18
  %21 = getelementptr inbounds i8* %src, i64 %19, !dbg !354
  %22 = getelementptr inbounds i8* %dst, i64 %19, !dbg !351
  %n.vec215 = and i64 %count, -32
  %cmp.zero217 = icmp eq i64 %n.vec215, 0
  %23 = add i64 %count, -1
  br i1 %cmp.zero217, label %middle.block210, label %vector.memcheck224

vector.memcheck224:                               ; preds = %.lr.ph9
  %scevgep219 = getelementptr i8* %src, i64 %23
  %scevgep218 = getelementptr i8* %dst, i64 %23
  %bound1221 = icmp ule i8* %scevgep219, %dst
  %bound0220 = icmp ule i8* %scevgep218, %src
  %memcheck.conflict223 = and i1 %bound0220, %bound1221
  %.sum = sub i64 %19, %n.vec215
  %rev.ptr.ind.end = getelementptr i8* %src, i64 %.sum
  %.sum439 = sub i64 %19, %n.vec215
  %rev.ptr.ind.end229 = getelementptr i8* %dst, i64 %.sum439
  %rev.ind.end231 = sub i64 %count, %n.vec215
  br i1 %memcheck.conflict223, label %middle.block210, label %vector.body209

vector.body209:                                   ; preds = %vector.body209, %vector.memcheck224
  %index212 = phi i64 [ %index.next234, %vector.body209 ], [ 0, %vector.memcheck224 ]
  %.sum440 = sub i64 %19, %index212
  %.sum472 = sub i64 %19, %index212
  %next.gep236.sum = add i64 %.sum440, -15, !dbg !353
  %24 = getelementptr i8* %src, i64 %next.gep236.sum, !dbg !353
  %25 = bitcast i8* %24 to <16 x i8>*, !dbg !353
  %wide.load434 = load <16 x i8>* %25, align 1, !dbg !353
  %reverse = shufflevector <16 x i8> %wide.load434, <16 x i8> undef, <16 x i32> <i32 15, i32 14, i32 13, i32 12, i32 11, i32 10, i32 9, i32 8, i32 7, i32 6, i32 5, i32 4, i32 3, i32 2, i32 1, i32 0>, !dbg !353
  %.sum505 = add i64 %.sum440, -31, !dbg !353
  %26 = getelementptr i8* %src, i64 %.sum505, !dbg !353
  %27 = bitcast i8* %26 to <16 x i8>*, !dbg !353
  %wide.load435 = load <16 x i8>* %27, align 1, !dbg !353
  %reverse436 = shufflevector <16 x i8> %wide.load435, <16 x i8> undef, <16 x i32> <i32 15, i32 14, i32 13, i32 12, i32 11, i32 10, i32 9, i32 8, i32 7, i32 6, i32 5, i32 4, i32 3, i32 2, i32 1, i32 0>, !dbg !353
  %reverse437 = shufflevector <16 x i8> %reverse, <16 x i8> undef, <16 x i32> <i32 15, i32 14, i32 13, i32 12, i32 11, i32 10, i32 9, i32 8, i32 7, i32 6, i32 5, i32 4, i32 3, i32 2, i32 1, i32 0>, !dbg !353
  %next.gep333.sum = add i64 %.sum472, -15, !dbg !353
  %28 = getelementptr i8* %dst, i64 %next.gep333.sum, !dbg !353
  %29 = bitcast i8* %28 to <16 x i8>*, !dbg !353
  store <16 x i8> %reverse437, <16 x i8>* %29, align 1, !dbg !353
  %reverse438 = shufflevector <16 x i8> %reverse436, <16 x i8> undef, <16 x i32> <i32 15, i32 14, i32 13, i32 12, i32 11, i32 10, i32 9, i32 8, i32 7, i32 6, i32 5, i32 4, i32 3, i32 2, i32 1, i32 0>, !dbg !353
  %.sum507 = add i64 %.sum472, -31, !dbg !353
  %30 = getelementptr i8* %dst, i64 %.sum507, !dbg !353
  %31 = bitcast i8* %30 to <16 x i8>*, !dbg !353
  store <16 x i8> %reverse438, <16 x i8>* %31, align 1, !dbg !353
  %index.next234 = add i64 %index212, 32
  %32 = icmp eq i64 %index.next234, %n.vec215
  br i1 %32, label %middle.block210, label %vector.body209, !llvm.loop !355

middle.block210:                                  ; preds = %vector.body209, %vector.memcheck224, %.lr.ph9
  %resume.val225 = phi i8* [ %21, %.lr.ph9 ], [ %21, %vector.memcheck224 ], [ %rev.ptr.ind.end, %vector.body209 ]
  %resume.val227 = phi i8* [ %22, %.lr.ph9 ], [ %22, %vector.memcheck224 ], [ %rev.ptr.ind.end229, %vector.body209 ]
  %resume.val230 = phi i64 [ %count, %.lr.ph9 ], [ %count, %vector.memcheck224 ], [ %rev.ind.end231, %vector.body209 ]
  %new.indc.resume.val232 = phi i64 [ 0, %.lr.ph9 ], [ 0, %vector.memcheck224 ], [ %n.vec215, %vector.body209 ]
  %cmp.n233 = icmp eq i64 %new.indc.resume.val232, %count
  br i1 %cmp.n233, label %.loopexit, label %scalar.ph211

scalar.ph211:                                     ; preds = %scalar.ph211, %middle.block210
  %b.18 = phi i8* [ %34, %scalar.ph211 ], [ %resume.val225, %middle.block210 ]
  %a.17 = phi i8* [ %36, %scalar.ph211 ], [ %resume.val227, %middle.block210 ]
  %.16 = phi i64 [ %33, %scalar.ph211 ], [ %resume.val230, %middle.block210 ]
  %33 = add i64 %.16, -1, !dbg !353
  %34 = getelementptr inbounds i8* %b.18, i64 -1, !dbg !353
  %35 = load i8* %b.18, align 1, !dbg !353, !tbaa !340
  %36 = getelementptr inbounds i8* %a.17, i64 -1, !dbg !353
  store i8 %35, i8* %a.17, align 1, !dbg !353, !tbaa !340
  %37 = icmp eq i64 %33, 0, !dbg !353
  br i1 %37, label %.loopexit, label %scalar.ph211, !dbg !353, !llvm.loop !356

.loopexit:                                        ; preds = %scalar.ph211, %middle.block210, %18, %.lr.ph, %middle.block, %.preheader, %0
  ret i8* %dst, !dbg !357
}

; Function Attrs: nounwind uwtable
define weak i8* @mempcpy(i8* %destaddr, i8* %srcaddr, i64 %len) #3 {
  %1 = icmp eq i64 %len, 0, !dbg !358
  br i1 %1, label %15, label %.lr.ph.preheader, !dbg !358

.lr.ph.preheader:                                 ; preds = %0
  %n.vec = and i64 %len, -32
  %cmp.zero = icmp eq i64 %n.vec, 0
  %2 = add i64 %len, -1
  br i1 %cmp.zero, label %middle.block, label %vector.memcheck

vector.memcheck:                                  ; preds = %.lr.ph.preheader
  %scevgep5 = getelementptr i8* %srcaddr, i64 %2
  %scevgep4 = getelementptr i8* %destaddr, i64 %2
  %bound1 = icmp uge i8* %scevgep4, %srcaddr
  %bound0 = icmp uge i8* %scevgep5, %destaddr
  %memcheck.conflict = and i1 %bound0, %bound1
  %ptr.ind.end = getelementptr i8* %srcaddr, i64 %n.vec
  %ptr.ind.end7 = getelementptr i8* %destaddr, i64 %n.vec
  %rev.ind.end = sub i64 %len, %n.vec
  br i1 %memcheck.conflict, label %middle.block, label %vector.body

vector.body:                                      ; preds = %vector.body, %vector.memcheck
  %index = phi i64 [ %index.next, %vector.body ], [ 0, %vector.memcheck ]
  %next.gep = getelementptr i8* %srcaddr, i64 %index
  %next.gep104 = getelementptr i8* %destaddr, i64 %index
  %3 = bitcast i8* %next.gep to <16 x i8>*, !dbg !359
  %wide.load = load <16 x i8>* %3, align 1, !dbg !359
  %next.gep.sum280 = or i64 %index, 16, !dbg !359
  %4 = getelementptr i8* %srcaddr, i64 %next.gep.sum280, !dbg !359
  %5 = bitcast i8* %4 to <16 x i8>*, !dbg !359
  %wide.load201 = load <16 x i8>* %5, align 1, !dbg !359
  %6 = bitcast i8* %next.gep104 to <16 x i8>*, !dbg !359
  store <16 x i8> %wide.load, <16 x i8>* %6, align 1, !dbg !359
  %next.gep104.sum297 = or i64 %index, 16, !dbg !359
  %7 = getelementptr i8* %destaddr, i64 %next.gep104.sum297, !dbg !359
  %8 = bitcast i8* %7 to <16 x i8>*, !dbg !359
  store <16 x i8> %wide.load201, <16 x i8>* %8, align 1, !dbg !359
  %index.next = add i64 %index, 32
  %9 = icmp eq i64 %index.next, %n.vec
  br i1 %9, label %middle.block, label %vector.body, !llvm.loop !360

middle.block:                                     ; preds = %vector.body, %vector.memcheck, %.lr.ph.preheader
  %resume.val = phi i8* [ %srcaddr, %.lr.ph.preheader ], [ %srcaddr, %vector.memcheck ], [ %ptr.ind.end, %vector.body ]
  %resume.val6 = phi i8* [ %destaddr, %.lr.ph.preheader ], [ %destaddr, %vector.memcheck ], [ %ptr.ind.end7, %vector.body ]
  %resume.val8 = phi i64 [ %len, %.lr.ph.preheader ], [ %len, %vector.memcheck ], [ %rev.ind.end, %vector.body ]
  %new.indc.resume.val = phi i64 [ 0, %.lr.ph.preheader ], [ 0, %vector.memcheck ], [ %n.vec, %vector.body ]
  %cmp.n = icmp eq i64 %new.indc.resume.val, %len
  br i1 %cmp.n, label %._crit_edge, label %.lr.ph

.lr.ph:                                           ; preds = %.lr.ph, %middle.block
  %src.03 = phi i8* [ %11, %.lr.ph ], [ %resume.val, %middle.block ]
  %dest.02 = phi i8* [ %13, %.lr.ph ], [ %resume.val6, %middle.block ]
  %.01 = phi i64 [ %10, %.lr.ph ], [ %resume.val8, %middle.block ]
  %10 = add i64 %.01, -1, !dbg !358
  %11 = getelementptr inbounds i8* %src.03, i64 1, !dbg !359
  %12 = load i8* %src.03, align 1, !dbg !359, !tbaa !340
  %13 = getelementptr inbounds i8* %dest.02, i64 1, !dbg !359
  store i8 %12, i8* %dest.02, align 1, !dbg !359, !tbaa !340
  %14 = icmp eq i64 %10, 0, !dbg !358
  br i1 %14, label %._crit_edge, label %.lr.ph, !dbg !358, !llvm.loop !361

._crit_edge:                                      ; preds = %.lr.ph, %middle.block
  %scevgep = getelementptr i8* %destaddr, i64 %len
  br label %15, !dbg !358

; <label>:15                                      ; preds = %._crit_edge, %0
  %dest.0.lcssa = phi i8* [ %scevgep, %._crit_edge ], [ %destaddr, %0 ]
  ret i8* %dest.0.lcssa, !dbg !362
}

; Function Attrs: nounwind uwtable
define weak i8* @memset(i8* %dst, i32 %s, i64 %count) #3 {
  %1 = icmp eq i64 %count, 0, !dbg !363
  br i1 %1, label %._crit_edge, label %.lr.ph, !dbg !363

.lr.ph:                                           ; preds = %0
  %2 = trunc i32 %s to i8, !dbg !364
  br label %3, !dbg !363

; <label>:3                                       ; preds = %3, %.lr.ph
  %a.02 = phi i8* [ %dst, %.lr.ph ], [ %5, %3 ]
  %.01 = phi i64 [ %count, %.lr.ph ], [ %4, %3 ]
  %4 = add i64 %.01, -1, !dbg !363
  %5 = getelementptr inbounds i8* %a.02, i64 1, !dbg !364
  store volatile i8 %2, i8* %a.02, align 1, !dbg !364, !tbaa !340
  %6 = icmp eq i64 %4, 0, !dbg !363
  br i1 %6, label %._crit_edge, label %3, !dbg !363

._crit_edge:                                      ; preds = %3, %0
  ret i8* %dst, !dbg !365
}

; Function Attrs: nounwind uwtable
define double @klee_internal_sqrt(double %d) #3 {
  %1 = tail call double @klee_sqrt_double(double %d) #12, !dbg !366
  ret double %1, !dbg !366
}

declare double @klee_sqrt_double(double) #7

; Function Attrs: nounwind uwtable
define float @klee_internal_sqrtf(float %f) #3 {
  %1 = tail call float @klee_sqrt_float(float %f) #12, !dbg !367
  ret float %1, !dbg !367
}

declare float @klee_sqrt_float(float) #7

; Function Attrs: nounwind uwtable
define x86_fp80 @klee_internal_sqrtl(x86_fp80 %f) #3 {
  %1 = tail call x86_fp80 @klee_sqrt_long_double(x86_fp80 %f) #12, !dbg !368
  ret x86_fp80 %1, !dbg !368
}

declare x86_fp80 @klee_sqrt_long_double(x86_fp80) #7

attributes #0 = { nounwind uwtable "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "stack-protector-buffer-size"="8" "unsafe-fp-math"="false" "use-soft-float
attributes #1 = { "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "stack-protector-buffer-size"="8" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #2 = { nounwind "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "stack-protector-buffer-size"="8" "unsafe-fp-math"="false" "use-soft-float"="false
attributes #3 = { nounwind uwtable "less-precise-fpmad"="false" "no-frame-pointer-elim"="false" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "stack-protector-buffer-size"="8" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #4 = { nounwind "less-precise-fpmad"="false" "no-frame-pointer-elim"="false" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "stack-protector-buffer-size"="8" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #5 = { nounwind readnone "less-precise-fpmad"="false" "no-frame-pointer-elim"="false" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "stack-protector-buffer-size"="8" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #6 = { nounwind }
attributes #7 = { "less-precise-fpmad"="false" "no-frame-pointer-elim"="false" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "stack-protector-buffer-size"="8" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #8 = { noinline nounwind optnone uwtable "less-precise-fpmad"="false" "no-frame-pointer-elim"="false" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "stack-protector-buffer-size"="8" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #9 = { noinline optnone }
attributes #10 = { nounwind readnone }
attributes #11 = { noreturn "less-precise-fpmad"="false" "no-frame-pointer-elim"="false" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "stack-protector-buffer-size"="8" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #12 = { nobuiltin nounwind }
attributes #13 = { nobuiltin noreturn nounwind }

!llvm.ident = !{!0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0, !0}
!llvm.dbg.cu = !{!1, !24, !56, !101, !111, !124, !135, !147, !157, !176, !190, !204, !219}
!llvm.module.flags = !{!232, !233}

!0 = metadata !{metadata !"Ubuntu clang version 3.4.2- (branches/release_34) (based on LLVM 3.4.2)"}
!1 = metadata !{i32 786449, metadata !2, i32 1, metadata !"Ubuntu clang version 3.4.2- (branches/release_34) (based on LLVM 3.4.2)", i1 true, metadata !"", i32 0, metadata !3, metadata !3, metadata !4, metadata !3, metadata !3, metadata !""} ; [ DW_TAG_c
!2 = metadata !{metadata !"/home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/fabs.c", metadata !"/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic"}
!3 = metadata !{i32 0}
!4 = metadata !{metadata !5, metadata !12, metadata !18}
!5 = metadata !{i32 786478, metadata !2, metadata !6, metadata !"klee_internal_fabs", metadata !"klee_internal_fabs", metadata !"", i32 11, metadata !7, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 true, double (double)* @klee_internal_fabs, null, 
!6 = metadata !{i32 786473, metadata !2}          ; [ DW_TAG_file_type ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/fabs.c]
!7 = metadata !{i32 786453, i32 0, null, metadata !"", i32 0, i64 0, i64 0, i64 0, i32 0, null, metadata !8, i32 0, null, null, null} ; [ DW_TAG_subroutine_type ] [line 0, size 0, align 0, offset 0] [from ]
!8 = metadata !{metadata !9, metadata !9}
!9 = metadata !{i32 786468, null, null, metadata !"double", i32 0, i64 64, i64 64, i64 0, i32 0, i32 4} ; [ DW_TAG_base_type ] [double] [line 0, size 64, align 64, offset 0, enc DW_ATE_float]
!10 = metadata !{metadata !11}
!11 = metadata !{i32 786689, metadata !5, metadata !"d", metadata !6, i32 16777227, metadata !9, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [d] [line 11]
!12 = metadata !{i32 786478, metadata !2, metadata !6, metadata !"klee_internal_fabsf", metadata !"klee_internal_fabsf", metadata !"", i32 15, metadata !13, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 true, float (float)* @klee_internal_fabsf, nul
!13 = metadata !{i32 786453, i32 0, null, metadata !"", i32 0, i64 0, i64 0, i64 0, i32 0, null, metadata !14, i32 0, null, null, null} ; [ DW_TAG_subroutine_type ] [line 0, size 0, align 0, offset 0] [from ]
!14 = metadata !{metadata !15, metadata !15}
!15 = metadata !{i32 786468, null, null, metadata !"float", i32 0, i64 32, i64 32, i64 0, i32 0, i32 4} ; [ DW_TAG_base_type ] [float] [line 0, size 32, align 32, offset 0, enc DW_ATE_float]
!16 = metadata !{metadata !17}
!17 = metadata !{i32 786689, metadata !12, metadata !"f", metadata !6, i32 16777231, metadata !15, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [f] [line 15]
!18 = metadata !{i32 786478, metadata !2, metadata !6, metadata !"klee_internal_fabsl", metadata !"klee_internal_fabsl", metadata !"", i32 20, metadata !19, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 true, x86_fp80 (x86_fp80)* @klee_internal_fabs
!19 = metadata !{i32 786453, i32 0, null, metadata !"", i32 0, i64 0, i64 0, i64 0, i32 0, null, metadata !20, i32 0, null, null, null} ; [ DW_TAG_subroutine_type ] [line 0, size 0, align 0, offset 0] [from ]
!20 = metadata !{metadata !21, metadata !21}
!21 = metadata !{i32 786468, null, null, metadata !"long double", i32 0, i64 128, i64 128, i64 0, i32 0, i32 4} ; [ DW_TAG_base_type ] [long double] [line 0, size 128, align 128, offset 0, enc DW_ATE_float]
!22 = metadata !{metadata !23}
!23 = metadata !{i32 786689, metadata !18, metadata !"f", metadata !6, i32 16777236, metadata !21, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [f] [line 20]
!24 = metadata !{i32 786449, metadata !25, i32 1, metadata !"Ubuntu clang version 3.4.2- (branches/release_34) (based on LLVM 3.4.2)", i1 true, metadata !"", i32 0, metadata !26, metadata !3, metadata !43, metadata !3, metadata !3, metadata !""} ; [ DW_T
!25 = metadata !{metadata !"/home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/fenv.c", metadata !"/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic"}
!26 = metadata !{metadata !27, metadata !36}
!27 = metadata !{i32 786436, metadata !28, null, metadata !"KleeRoundingMode", i32 183, i64 32, i64 32, i32 0, i32 0, null, metadata !29, i32 0, null, null, null} ; [ DW_TAG_enumeration_type ] [KleeRoundingMode] [line 183, size 32, align 32, offset 0] [d
!28 = metadata !{metadata !"/home/fptesting/FPTesting/src/klee-float/include/klee/klee.h", metadata !"/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic"}
!29 = metadata !{metadata !30, metadata !31, metadata !32, metadata !33, metadata !34, metadata !35}
!30 = metadata !{i32 786472, metadata !"KLEE_FP_RNE", i64 0} ; [ DW_TAG_enumerator ] [KLEE_FP_RNE :: 0]
!31 = metadata !{i32 786472, metadata !"KLEE_FP_RNA", i64 1} ; [ DW_TAG_enumerator ] [KLEE_FP_RNA :: 1]
!32 = metadata !{i32 786472, metadata !"KLEE_FP_RU", i64 2} ; [ DW_TAG_enumerator ] [KLEE_FP_RU :: 2]
!33 = metadata !{i32 786472, metadata !"KLEE_FP_RD", i64 3} ; [ DW_TAG_enumerator ] [KLEE_FP_RD :: 3]
!34 = metadata !{i32 786472, metadata !"KLEE_FP_RZ", i64 4} ; [ DW_TAG_enumerator ] [KLEE_FP_RZ :: 4]
!35 = metadata !{i32 786472, metadata !"KLEE_FP_UNKNOWN", i64 5} ; [ DW_TAG_enumerator ] [KLEE_FP_UNKNOWN :: 5]
!36 = metadata !{i32 786436, metadata !25, null, metadata !"", i32 15, i64 32, i64 32, i32 0, i32 0, null, metadata !37, i32 0, null, null, null} ; [ DW_TAG_enumeration_type ] [line 15, size 32, align 32, offset 0] [def] [from ]
!37 = metadata !{metadata !38, metadata !39, metadata !40, metadata !41, metadata !42}
!38 = metadata !{i32 786472, metadata !"FE_TONEAREST", i64 0} ; [ DW_TAG_enumerator ] [FE_TONEAREST :: 0]
!39 = metadata !{i32 786472, metadata !"FE_DOWNWARD", i64 1024} ; [ DW_TAG_enumerator ] [FE_DOWNWARD :: 1024]
!40 = metadata !{i32 786472, metadata !"FE_UPWARD", i64 2048} ; [ DW_TAG_enumerator ] [FE_UPWARD :: 2048]
!41 = metadata !{i32 786472, metadata !"FE_TOWARDZERO", i64 3072} ; [ DW_TAG_enumerator ] [FE_TOWARDZERO :: 3072]
!42 = metadata !{i32 786472, metadata !"FE_TONEAREST_TIES_TO_AWAY", i64 3073} ; [ DW_TAG_enumerator ] [FE_TONEAREST_TIES_TO_AWAY :: 3073]
!43 = metadata !{metadata !44, metadata !51}
!44 = metadata !{i32 786478, metadata !25, metadata !45, metadata !"klee_internal_fegetround", metadata !"klee_internal_fegetround", metadata !"", i32 33, metadata !46, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 true, i32 ()* @klee_internal_feget
!45 = metadata !{i32 786473, metadata !25}        ; [ DW_TAG_file_type ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/fenv.c]
!46 = metadata !{i32 786453, i32 0, null, metadata !"", i32 0, i64 0, i64 0, i64 0, i32 0, null, metadata !47, i32 0, null, null, null} ; [ DW_TAG_subroutine_type ] [line 0, size 0, align 0, offset 0] [from ]
!47 = metadata !{metadata !48}
!48 = metadata !{i32 786468, null, null, metadata !"int", i32 0, i64 32, i64 32, i64 0, i32 0, i32 5} ; [ DW_TAG_base_type ] [int] [line 0, size 32, align 32, offset 0, enc DW_ATE_signed]
!49 = metadata !{metadata !50}
!50 = metadata !{i32 786688, metadata !44, metadata !"rm", metadata !45, i32 34, metadata !27, i32 0, i32 0} ; [ DW_TAG_auto_variable ] [rm] [line 34]
!51 = metadata !{i32 786478, metadata !25, metadata !45, metadata !"klee_internal_fesetround", metadata !"klee_internal_fesetround", metadata !"", i32 52, metadata !52, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 true, i32 (i32)* @klee_internal_fe
!52 = metadata !{i32 786453, i32 0, null, metadata !"", i32 0, i64 0, i64 0, i64 0, i32 0, null, metadata !53, i32 0, null, null, null} ; [ DW_TAG_subroutine_type ] [line 0, size 0, align 0, offset 0] [from ]
!53 = metadata !{metadata !48, metadata !48}
!54 = metadata !{metadata !55}
!55 = metadata !{i32 786689, metadata !51, metadata !"rm", metadata !45, i32 16777268, metadata !48, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [rm] [line 52]
!56 = metadata !{i32 786449, metadata !57, i32 1, metadata !"Ubuntu clang version 3.4.2- (branches/release_34) (based on LLVM 3.4.2)", i1 true, metadata !"", i32 0, metadata !58, metadata !3, metadata !66, metadata !3, metadata !3, metadata !""} ; [ DW_T
!57 = metadata !{metadata !"/home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/fpclassify.c", metadata !"/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic"}
!58 = metadata !{metadata !59}
!59 = metadata !{i32 786436, metadata !57, null, metadata !"", i32 58, i64 32, i64 32, i32 0, i32 0, null, metadata !60, i32 0, null, null, null} ; [ DW_TAG_enumeration_type ] [line 58, size 32, align 32, offset 0] [def] [from ]
!60 = metadata !{metadata !61, metadata !62, metadata !63, metadata !64, metadata !65}
!61 = metadata !{i32 786472, metadata !"FP_NAN", i64 0} ; [ DW_TAG_enumerator ] [FP_NAN :: 0]
!62 = metadata !{i32 786472, metadata !"FP_INFINITE", i64 1} ; [ DW_TAG_enumerator ] [FP_INFINITE :: 1]
!63 = metadata !{i32 786472, metadata !"FP_ZERO", i64 2} ; [ DW_TAG_enumerator ] [FP_ZERO :: 2]
!64 = metadata !{i32 786472, metadata !"FP_SUBNORMAL", i64 3} ; [ DW_TAG_enumerator ] [FP_SUBNORMAL :: 3]
!65 = metadata !{i32 786472, metadata !"FP_NORMAL", i64 4} ; [ DW_TAG_enumerator ] [FP_NORMAL :: 4]
!66 = metadata !{metadata !67, metadata !73, metadata !78, metadata !83, metadata !86, metadata !89, metadata !92, metadata !95, metadata !98}
!67 = metadata !{i32 786478, metadata !57, metadata !68, metadata !"klee_internal_isnanf", metadata !"klee_internal_isnanf", metadata !"", i32 16, metadata !69, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 true, i32 (float)* @klee_internal_isnanf, 
!68 = metadata !{i32 786473, metadata !57}        ; [ DW_TAG_file_type ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/fpclassify.c]
!69 = metadata !{i32 786453, i32 0, null, metadata !"", i32 0, i64 0, i64 0, i64 0, i32 0, null, metadata !70, i32 0, null, null, null} ; [ DW_TAG_subroutine_type ] [line 0, size 0, align 0, offset 0] [from ]
!70 = metadata !{metadata !48, metadata !15}
!71 = metadata !{metadata !72}
!72 = metadata !{i32 786689, metadata !67, metadata !"f", metadata !68, i32 16777232, metadata !15, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [f] [line 16]
!73 = metadata !{i32 786478, metadata !57, metadata !68, metadata !"klee_internal_isnan", metadata !"klee_internal_isnan", metadata !"", i32 21, metadata !74, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 true, i32 (double)* @klee_internal_isnan, nu
!74 = metadata !{i32 786453, i32 0, null, metadata !"", i32 0, i64 0, i64 0, i64 0, i32 0, null, metadata !75, i32 0, null, null, null} ; [ DW_TAG_subroutine_type ] [line 0, size 0, align 0, offset 0] [from ]
!75 = metadata !{metadata !48, metadata !9}
!76 = metadata !{metadata !77}
!77 = metadata !{i32 786689, metadata !73, metadata !"d", metadata !68, i32 16777237, metadata !9, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [d] [line 21]
!78 = metadata !{i32 786478, metadata !57, metadata !68, metadata !"klee_internal_isnanl", metadata !"klee_internal_isnanl", metadata !"", i32 26, metadata !79, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 true, i32 (x86_fp80)* @klee_internal_isnan
!79 = metadata !{i32 786453, i32 0, null, metadata !"", i32 0, i64 0, i64 0, i64 0, i32 0, null, metadata !80, i32 0, null, null, null} ; [ DW_TAG_subroutine_type ] [line 0, size 0, align 0, offset 0] [from ]
!80 = metadata !{metadata !48, metadata !21}
!81 = metadata !{metadata !82}
!82 = metadata !{i32 786689, metadata !78, metadata !"d", metadata !68, i32 16777242, metadata !21, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [d] [line 26]
!83 = metadata !{i32 786478, metadata !57, metadata !68, metadata !"klee_internal_fpclassifyf", metadata !"klee_internal_fpclassifyf", metadata !"", i32 67, metadata !69, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 true, i32 (float)* @klee_interna
!84 = metadata !{metadata !85}
!85 = metadata !{i32 786689, metadata !83, metadata !"f", metadata !68, i32 16777283, metadata !15, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [f] [line 67]
!86 = metadata !{i32 786478, metadata !57, metadata !68, metadata !"klee_internal_fpclassify", metadata !"klee_internal_fpclassify", metadata !"", i32 82, metadata !74, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 true, i32 (double)* @klee_internal
!87 = metadata !{metadata !88}
!88 = metadata !{i32 786689, metadata !86, metadata !"f", metadata !68, i32 16777298, metadata !9, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [f] [line 82]
!89 = metadata !{i32 786478, metadata !57, metadata !68, metadata !"klee_internal_fpclassifyl", metadata !"klee_internal_fpclassifyl", metadata !"", i32 98, metadata !79, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 true, i32 (x86_fp80)* @klee_inte
!90 = metadata !{metadata !91}
!91 = metadata !{i32 786689, metadata !89, metadata !"ld", metadata !68, i32 16777314, metadata !21, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [ld] [line 98]
!92 = metadata !{i32 786478, metadata !57, metadata !68, metadata !"klee_internal_finitef", metadata !"klee_internal_finitef", metadata !"", i32 114, metadata !69, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 true, i32 (float)* @klee_internal_finit
!93 = metadata !{metadata !94}
!94 = metadata !{i32 786689, metadata !92, metadata !"f", metadata !68, i32 16777330, metadata !15, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [f] [line 114]
!95 = metadata !{i32 786478, metadata !57, metadata !68, metadata !"klee_internal_finite", metadata !"klee_internal_finite", metadata !"", i32 119, metadata !74, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 true, i32 (double)* @klee_internal_finite
!96 = metadata !{metadata !97}
!97 = metadata !{i32 786689, metadata !95, metadata !"f", metadata !68, i32 16777335, metadata !9, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [f] [line 119]
!98 = metadata !{i32 786478, metadata !57, metadata !68, metadata !"klee_internal_finitel", metadata !"klee_internal_finitel", metadata !"", i32 124, metadata !79, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 true, i32 (x86_fp80)* @klee_internal_fi
!99 = metadata !{metadata !100}
!100 = metadata !{i32 786689, metadata !98, metadata !"f", metadata !68, i32 16777340, metadata !21, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [f] [line 124]
!101 = metadata !{i32 786449, metadata !102, i32 1, metadata !"Ubuntu clang version 3.4.2- (branches/release_34) (based on LLVM 3.4.2)", i1 true, metadata !"", i32 0, metadata !3, metadata !3, metadata !103, metadata !3, metadata !3, metadata !""} ; [ DW
!102 = metadata !{metadata !"/home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/klee_div_zero_check.c", metadata !"/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic"}
!103 = metadata !{metadata !104}
!104 = metadata !{i32 786478, metadata !102, metadata !105, metadata !"klee_div_zero_check", metadata !"klee_div_zero_check", metadata !"", i32 12, metadata !106, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 true, void (i64)* @klee_div_zero_check, 
!105 = metadata !{i32 786473, metadata !102}      ; [ DW_TAG_file_type ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/klee_div_zero_check.c]
!106 = metadata !{i32 786453, i32 0, null, metadata !"", i32 0, i64 0, i64 0, i64 0, i32 0, null, metadata !107, i32 0, null, null, null} ; [ DW_TAG_subroutine_type ] [line 0, size 0, align 0, offset 0] [from ]
!107 = metadata !{null, metadata !108}
!108 = metadata !{i32 786468, null, null, metadata !"long long int", i32 0, i64 64, i64 64, i64 0, i32 0, i32 5} ; [ DW_TAG_base_type ] [long long int] [line 0, size 64, align 64, offset 0, enc DW_ATE_signed]
!109 = metadata !{metadata !110}
!110 = metadata !{i32 786689, metadata !104, metadata !"z", metadata !105, i32 16777228, metadata !108, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [z] [line 12]
!111 = metadata !{i32 786449, metadata !112, i32 1, metadata !"Ubuntu clang version 3.4.2- (branches/release_34) (based on LLVM 3.4.2)", i1 true, metadata !"", i32 0, metadata !3, metadata !3, metadata !113, metadata !3, metadata !3, metadata !""} ; [ DW
!112 = metadata !{metadata !"/home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/klee_int.c", metadata !"/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic"}
!113 = metadata !{metadata !114}
!114 = metadata !{i32 786478, metadata !112, metadata !115, metadata !"klee_int", metadata !"klee_int", metadata !"", i32 13, metadata !116, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 true, i32 (i8*)* @klee_int, null, null, metadata !121, i32 13}
!115 = metadata !{i32 786473, metadata !112}      ; [ DW_TAG_file_type ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/klee_int.c]
!116 = metadata !{i32 786453, i32 0, null, metadata !"", i32 0, i64 0, i64 0, i64 0, i32 0, null, metadata !117, i32 0, null, null, null} ; [ DW_TAG_subroutine_type ] [line 0, size 0, align 0, offset 0] [from ]
!117 = metadata !{metadata !48, metadata !118}
!118 = metadata !{i32 786447, null, null, metadata !"", i32 0, i64 64, i64 64, i64 0, i32 0, metadata !119} ; [ DW_TAG_pointer_type ] [line 0, size 64, align 64, offset 0] [from ]
!119 = metadata !{i32 786470, null, null, metadata !"", i32 0, i64 0, i64 0, i64 0, i32 0, metadata !120} ; [ DW_TAG_const_type ] [line 0, size 0, align 0, offset 0] [from char]
!120 = metadata !{i32 786468, null, null, metadata !"char", i32 0, i64 8, i64 8, i64 0, i32 0, i32 6} ; [ DW_TAG_base_type ] [char] [line 0, size 8, align 8, offset 0, enc DW_ATE_signed_char]
!121 = metadata !{metadata !122, metadata !123}
!122 = metadata !{i32 786689, metadata !114, metadata !"name", metadata !115, i32 16777229, metadata !118, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [name] [line 13]
!123 = metadata !{i32 786688, metadata !114, metadata !"x", metadata !115, i32 14, metadata !48, i32 0, i32 0} ; [ DW_TAG_auto_variable ] [x] [line 14]
!124 = metadata !{i32 786449, metadata !125, i32 1, metadata !"Ubuntu clang version 3.4.2- (branches/release_34) (based on LLVM 3.4.2)", i1 true, metadata !"", i32 0, metadata !3, metadata !3, metadata !126, metadata !3, metadata !3, metadata !""} ; [ DW
!125 = metadata !{metadata !"/home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/klee_overshift_check.c", metadata !"/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic"}
!126 = metadata !{metadata !127}
!127 = metadata !{i32 786478, metadata !125, metadata !128, metadata !"klee_overshift_check", metadata !"klee_overshift_check", metadata !"", i32 20, metadata !129, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 true, void (i64, i64)* @klee_overshift
!128 = metadata !{i32 786473, metadata !125}      ; [ DW_TAG_file_type ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/klee_overshift_check.c]
!129 = metadata !{i32 786453, i32 0, null, metadata !"", i32 0, i64 0, i64 0, i64 0, i32 0, null, metadata !130, i32 0, null, null, null} ; [ DW_TAG_subroutine_type ] [line 0, size 0, align 0, offset 0] [from ]
!130 = metadata !{null, metadata !131, metadata !131}
!131 = metadata !{i32 786468, null, null, metadata !"long long unsigned int", i32 0, i64 64, i64 64, i64 0, i32 0, i32 7} ; [ DW_TAG_base_type ] [long long unsigned int] [line 0, size 64, align 64, offset 0, enc DW_ATE_unsigned]
!132 = metadata !{metadata !133, metadata !134}
!133 = metadata !{i32 786689, metadata !127, metadata !"bitWidth", metadata !128, i32 16777236, metadata !131, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [bitWidth] [line 20]
!134 = metadata !{i32 786689, metadata !127, metadata !"shift", metadata !128, i32 33554452, metadata !131, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [shift] [line 20]
!135 = metadata !{i32 786449, metadata !136, i32 1, metadata !"Ubuntu clang version 3.4.2- (branches/release_34) (based on LLVM 3.4.2)", i1 true, metadata !"", i32 0, metadata !3, metadata !3, metadata !137, metadata !3, metadata !3, metadata !""} ; [ DW
!136 = metadata !{metadata !"/home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/klee_range.c", metadata !"/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic"}
!137 = metadata !{metadata !138}
!138 = metadata !{i32 786478, metadata !136, metadata !139, metadata !"klee_range", metadata !"klee_range", metadata !"", i32 13, metadata !140, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 true, i32 (i32, i32, i8*)* @klee_range, null, null, metada
!139 = metadata !{i32 786473, metadata !136}      ; [ DW_TAG_file_type ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/klee_range.c]
!140 = metadata !{i32 786453, i32 0, null, metadata !"", i32 0, i64 0, i64 0, i64 0, i32 0, null, metadata !141, i32 0, null, null, null} ; [ DW_TAG_subroutine_type ] [line 0, size 0, align 0, offset 0] [from ]
!141 = metadata !{metadata !48, metadata !48, metadata !48, metadata !118}
!142 = metadata !{metadata !143, metadata !144, metadata !145, metadata !146}
!143 = metadata !{i32 786689, metadata !138, metadata !"start", metadata !139, i32 16777229, metadata !48, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [start] [line 13]
!144 = metadata !{i32 786689, metadata !138, metadata !"end", metadata !139, i32 33554445, metadata !48, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [end] [line 13]
!145 = metadata !{i32 786689, metadata !138, metadata !"name", metadata !139, i32 50331661, metadata !118, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [name] [line 13]
!146 = metadata !{i32 786688, metadata !138, metadata !"x", metadata !139, i32 14, metadata !48, i32 0, i32 0} ; [ DW_TAG_auto_variable ] [x] [line 14]
!147 = metadata !{i32 786449, metadata !148, i32 1, metadata !"Ubuntu clang version 3.4.2- (branches/release_34) (based on LLVM 3.4.2)", i1 true, metadata !"", i32 0, metadata !149, metadata !3, metadata !150, metadata !3, metadata !3, metadata !""} ; [ 
!148 = metadata !{metadata !"/home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/klee_set_rounding_mode.c", metadata !"/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic"}
!149 = metadata !{metadata !27}
!150 = metadata !{metadata !151}
!151 = metadata !{i32 786478, metadata !148, metadata !152, metadata !"klee_set_rounding_mode", metadata !"klee_set_rounding_mode", metadata !"", i32 16, metadata !153, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 true, void (i32)* @klee_set_roundi
!152 = metadata !{i32 786473, metadata !148}      ; [ DW_TAG_file_type ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/klee_set_rounding_mode.c]
!153 = metadata !{i32 786453, i32 0, null, metadata !"", i32 0, i64 0, i64 0, i64 0, i32 0, null, metadata !154, i32 0, null, null, null} ; [ DW_TAG_subroutine_type ] [line 0, size 0, align 0, offset 0] [from ]
!154 = metadata !{null, metadata !27}
!155 = metadata !{metadata !156}
!156 = metadata !{i32 786689, metadata !151, metadata !"rm", metadata !152, i32 16777232, metadata !27, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [rm] [line 16]
!157 = metadata !{i32 786449, metadata !158, i32 1, metadata !"Ubuntu clang version 3.4.2- (branches/release_34) (based on LLVM 3.4.2)", i1 true, metadata !"", i32 0, metadata !3, metadata !3, metadata !159, metadata !3, metadata !3, metadata !""} ; [ DW
!158 = metadata !{metadata !"/home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/memcpy.c", metadata !"/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic"}
!159 = metadata !{metadata !160}
!160 = metadata !{i32 786478, metadata !158, metadata !161, metadata !"memcpy", metadata !"memcpy", metadata !"", i32 12, metadata !162, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 true, i8* (i8*, i8*, i64)* @memcpy, null, null, metadata !169, i32
!161 = metadata !{i32 786473, metadata !158}      ; [ DW_TAG_file_type ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/memcpy.c]
!162 = metadata !{i32 786453, i32 0, null, metadata !"", i32 0, i64 0, i64 0, i64 0, i32 0, null, metadata !163, i32 0, null, null, null} ; [ DW_TAG_subroutine_type ] [line 0, size 0, align 0, offset 0] [from ]
!163 = metadata !{metadata !164, metadata !164, metadata !165, metadata !167}
!164 = metadata !{i32 786447, null, null, metadata !"", i32 0, i64 64, i64 64, i64 0, i32 0, null} ; [ DW_TAG_pointer_type ] [line 0, size 64, align 64, offset 0] [from ]
!165 = metadata !{i32 786447, null, null, metadata !"", i32 0, i64 64, i64 64, i64 0, i32 0, metadata !166} ; [ DW_TAG_pointer_type ] [line 0, size 64, align 64, offset 0] [from ]
!166 = metadata !{i32 786470, null, null, metadata !"", i32 0, i64 0, i64 0, i64 0, i32 0, null} ; [ DW_TAG_const_type ] [line 0, size 0, align 0, offset 0] [from ]
!167 = metadata !{i32 786454, metadata !158, null, metadata !"size_t", i32 42, i64 0, i64 0, i64 0, i32 0, metadata !168} ; [ DW_TAG_typedef ] [size_t] [line 42, size 0, align 0, offset 0] [from long unsigned int]
!168 = metadata !{i32 786468, null, null, metadata !"long unsigned int", i32 0, i64 64, i64 64, i64 0, i32 0, i32 7} ; [ DW_TAG_base_type ] [long unsigned int] [line 0, size 64, align 64, offset 0, enc DW_ATE_unsigned]
!169 = metadata !{metadata !170, metadata !171, metadata !172, metadata !173, metadata !175}
!170 = metadata !{i32 786689, metadata !160, metadata !"destaddr", metadata !161, i32 16777228, metadata !164, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [destaddr] [line 12]
!171 = metadata !{i32 786689, metadata !160, metadata !"srcaddr", metadata !161, i32 33554444, metadata !165, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [srcaddr] [line 12]
!172 = metadata !{i32 786689, metadata !160, metadata !"len", metadata !161, i32 50331660, metadata !167, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [len] [line 12]
!173 = metadata !{i32 786688, metadata !160, metadata !"dest", metadata !161, i32 13, metadata !174, i32 0, i32 0} ; [ DW_TAG_auto_variable ] [dest] [line 13]
!174 = metadata !{i32 786447, null, null, metadata !"", i32 0, i64 64, i64 64, i64 0, i32 0, metadata !120} ; [ DW_TAG_pointer_type ] [line 0, size 64, align 64, offset 0] [from char]
!175 = metadata !{i32 786688, metadata !160, metadata !"src", metadata !161, i32 14, metadata !118, i32 0, i32 0} ; [ DW_TAG_auto_variable ] [src] [line 14]
!176 = metadata !{i32 786449, metadata !177, i32 1, metadata !"Ubuntu clang version 3.4.2- (branches/release_34) (based on LLVM 3.4.2)", i1 true, metadata !"", i32 0, metadata !3, metadata !3, metadata !178, metadata !3, metadata !3, metadata !""} ; [ DW
!177 = metadata !{metadata !"/home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/memmove.c", metadata !"/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic"}
!178 = metadata !{metadata !179}
!179 = metadata !{i32 786478, metadata !177, metadata !180, metadata !"memmove", metadata !"memmove", metadata !"", i32 12, metadata !181, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 true, i8* (i8*, i8*, i64)* @memmove, null, null, metadata !184, 
!180 = metadata !{i32 786473, metadata !177}      ; [ DW_TAG_file_type ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/memmove.c]
!181 = metadata !{i32 786453, i32 0, null, metadata !"", i32 0, i64 0, i64 0, i64 0, i32 0, null, metadata !182, i32 0, null, null, null} ; [ DW_TAG_subroutine_type ] [line 0, size 0, align 0, offset 0] [from ]
!182 = metadata !{metadata !164, metadata !164, metadata !165, metadata !183}
!183 = metadata !{i32 786454, metadata !177, null, metadata !"size_t", i32 42, i64 0, i64 0, i64 0, i32 0, metadata !168} ; [ DW_TAG_typedef ] [size_t] [line 42, size 0, align 0, offset 0] [from long unsigned int]
!184 = metadata !{metadata !185, metadata !186, metadata !187, metadata !188, metadata !189}
!185 = metadata !{i32 786689, metadata !179, metadata !"dst", metadata !180, i32 16777228, metadata !164, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [dst] [line 12]
!186 = metadata !{i32 786689, metadata !179, metadata !"src", metadata !180, i32 33554444, metadata !165, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [src] [line 12]
!187 = metadata !{i32 786689, metadata !179, metadata !"count", metadata !180, i32 50331660, metadata !183, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [count] [line 12]
!188 = metadata !{i32 786688, metadata !179, metadata !"a", metadata !180, i32 13, metadata !174, i32 0, i32 0} ; [ DW_TAG_auto_variable ] [a] [line 13]
!189 = metadata !{i32 786688, metadata !179, metadata !"b", metadata !180, i32 14, metadata !118, i32 0, i32 0} ; [ DW_TAG_auto_variable ] [b] [line 14]
!190 = metadata !{i32 786449, metadata !191, i32 1, metadata !"Ubuntu clang version 3.4.2- (branches/release_34) (based on LLVM 3.4.2)", i1 true, metadata !"", i32 0, metadata !3, metadata !3, metadata !192, metadata !3, metadata !3, metadata !""} ; [ DW
!191 = metadata !{metadata !"/home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/mempcpy.c", metadata !"/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic"}
!192 = metadata !{metadata !193}
!193 = metadata !{i32 786478, metadata !191, metadata !194, metadata !"mempcpy", metadata !"mempcpy", metadata !"", i32 11, metadata !195, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 true, i8* (i8*, i8*, i64)* @mempcpy, null, null, metadata !198, 
!194 = metadata !{i32 786473, metadata !191}      ; [ DW_TAG_file_type ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/mempcpy.c]
!195 = metadata !{i32 786453, i32 0, null, metadata !"", i32 0, i64 0, i64 0, i64 0, i32 0, null, metadata !196, i32 0, null, null, null} ; [ DW_TAG_subroutine_type ] [line 0, size 0, align 0, offset 0] [from ]
!196 = metadata !{metadata !164, metadata !164, metadata !165, metadata !197}
!197 = metadata !{i32 786454, metadata !191, null, metadata !"size_t", i32 42, i64 0, i64 0, i64 0, i32 0, metadata !168} ; [ DW_TAG_typedef ] [size_t] [line 42, size 0, align 0, offset 0] [from long unsigned int]
!198 = metadata !{metadata !199, metadata !200, metadata !201, metadata !202, metadata !203}
!199 = metadata !{i32 786689, metadata !193, metadata !"destaddr", metadata !194, i32 16777227, metadata !164, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [destaddr] [line 11]
!200 = metadata !{i32 786689, metadata !193, metadata !"srcaddr", metadata !194, i32 33554443, metadata !165, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [srcaddr] [line 11]
!201 = metadata !{i32 786689, metadata !193, metadata !"len", metadata !194, i32 50331659, metadata !197, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [len] [line 11]
!202 = metadata !{i32 786688, metadata !193, metadata !"dest", metadata !194, i32 12, metadata !174, i32 0, i32 0} ; [ DW_TAG_auto_variable ] [dest] [line 12]
!203 = metadata !{i32 786688, metadata !193, metadata !"src", metadata !194, i32 13, metadata !118, i32 0, i32 0} ; [ DW_TAG_auto_variable ] [src] [line 13]
!204 = metadata !{i32 786449, metadata !205, i32 1, metadata !"Ubuntu clang version 3.4.2- (branches/release_34) (based on LLVM 3.4.2)", i1 true, metadata !"", i32 0, metadata !3, metadata !3, metadata !206, metadata !3, metadata !3, metadata !""} ; [ DW
!205 = metadata !{metadata !"/home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/memset.c", metadata !"/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic"}
!206 = metadata !{metadata !207}
!207 = metadata !{i32 786478, metadata !205, metadata !208, metadata !"memset", metadata !"memset", metadata !"", i32 11, metadata !209, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 true, i8* (i8*, i32, i64)* @memset, null, null, metadata !212, i32
!208 = metadata !{i32 786473, metadata !205}      ; [ DW_TAG_file_type ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/memset.c]
!209 = metadata !{i32 786453, i32 0, null, metadata !"", i32 0, i64 0, i64 0, i64 0, i32 0, null, metadata !210, i32 0, null, null, null} ; [ DW_TAG_subroutine_type ] [line 0, size 0, align 0, offset 0] [from ]
!210 = metadata !{metadata !164, metadata !164, metadata !48, metadata !211}
!211 = metadata !{i32 786454, metadata !205, null, metadata !"size_t", i32 42, i64 0, i64 0, i64 0, i32 0, metadata !168} ; [ DW_TAG_typedef ] [size_t] [line 42, size 0, align 0, offset 0] [from long unsigned int]
!212 = metadata !{metadata !213, metadata !214, metadata !215, metadata !216}
!213 = metadata !{i32 786689, metadata !207, metadata !"dst", metadata !208, i32 16777227, metadata !164, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [dst] [line 11]
!214 = metadata !{i32 786689, metadata !207, metadata !"s", metadata !208, i32 33554443, metadata !48, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [s] [line 11]
!215 = metadata !{i32 786689, metadata !207, metadata !"count", metadata !208, i32 50331659, metadata !211, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [count] [line 11]
!216 = metadata !{i32 786688, metadata !207, metadata !"a", metadata !208, i32 12, metadata !217, i32 0, i32 0} ; [ DW_TAG_auto_variable ] [a] [line 12]
!217 = metadata !{i32 786447, null, null, metadata !"", i32 0, i64 64, i64 64, i64 0, i32 0, metadata !218} ; [ DW_TAG_pointer_type ] [line 0, size 64, align 64, offset 0] [from ]
!218 = metadata !{i32 786485, null, null, metadata !"", i32 0, i64 0, i64 0, i64 0, i32 0, metadata !120} ; [ DW_TAG_volatile_type ] [line 0, size 0, align 0, offset 0] [from char]
!219 = metadata !{i32 786449, metadata !220, i32 1, metadata !"Ubuntu clang version 3.4.2- (branches/release_34) (based on LLVM 3.4.2)", i1 true, metadata !"", i32 0, metadata !3, metadata !3, metadata !221, metadata !3, metadata !3, metadata !""} ; [ DW
!220 = metadata !{metadata !"/home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/sqrt.c", metadata !"/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic"}
!221 = metadata !{metadata !222, metadata !226, metadata !229}
!222 = metadata !{i32 786478, metadata !220, metadata !223, metadata !"klee_internal_sqrt", metadata !"klee_internal_sqrt", metadata !"", i32 11, metadata !7, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 true, double (double)* @klee_internal_sqrt, 
!223 = metadata !{i32 786473, metadata !220}      ; [ DW_TAG_file_type ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/sqrt.c]
!224 = metadata !{metadata !225}
!225 = metadata !{i32 786689, metadata !222, metadata !"d", metadata !223, i32 16777227, metadata !9, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [d] [line 11]
!226 = metadata !{i32 786478, metadata !220, metadata !223, metadata !"klee_internal_sqrtf", metadata !"klee_internal_sqrtf", metadata !"", i32 15, metadata !13, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 true, float (float)* @klee_internal_sqrtf
!227 = metadata !{metadata !228}
!228 = metadata !{i32 786689, metadata !226, metadata !"f", metadata !223, i32 16777231, metadata !15, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [f] [line 15]
!229 = metadata !{i32 786478, metadata !220, metadata !223, metadata !"klee_internal_sqrtl", metadata !"klee_internal_sqrtl", metadata !"", i32 20, metadata !19, i1 false, i1 true, i32 0, i32 0, null, i32 256, i1 true, x86_fp80 (x86_fp80)* @klee_internal
!230 = metadata !{metadata !231}
!231 = metadata !{i32 786689, metadata !229, metadata !"f", metadata !223, i32 16777236, metadata !21, i32 0, i32 0} ; [ DW_TAG_arg_variable ] [f] [line 20]
!232 = metadata !{i32 2, metadata !"Dwarf Version", i32 4}
!233 = metadata !{i32 1, metadata !"Debug Info Version", i32 1}
!234 = metadata !{metadata !235, metadata !235, i64 0}
!235 = metadata !{metadata !"double", metadata !236, i64 0}
!236 = metadata !{metadata !"omnipotent char", metadata !237, i64 0}
!237 = metadata !{metadata !"Simple C/C++ TBAA"}
!238 = metadata !{metadata !239, metadata !239, i64 0}
!239 = metadata !{metadata !"long", metadata !236, i64 0}
!240 = metadata !{metadata !241, metadata !241, i64 0}
!241 = metadata !{metadata !"int", metadata !236, i64 0}
!242 = metadata !{i32 12, i32 0, metadata !5, null}
!243 = metadata !{i32 16, i32 0, metadata !12, null}
!244 = metadata !{i32 21, i32 0, metadata !18, null}
!245 = metadata !{i32 34, i32 0, metadata !44, null}
!246 = metadata !{i32 35, i32 0, metadata !44, null}
!247 = metadata !{i32 50, i32 0, metadata !44, null}
!248 = metadata !{i32 53, i32 0, metadata !51, null}
!249 = metadata !{i32 55, i32 0, metadata !250, null}
!250 = metadata !{i32 786443, metadata !25, metadata !51, i32 53, i32 0, i32 1} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/fenv.c]
!251 = metadata !{i32 56, i32 0, metadata !250, null}
!252 = metadata !{i32 66, i32 0, metadata !250, null}
!253 = metadata !{i32 67, i32 0, metadata !250, null}
!254 = metadata !{i32 69, i32 0, metadata !250, null}
!255 = metadata !{i32 70, i32 0, metadata !250, null}
!256 = metadata !{i32 72, i32 0, metadata !250, null}
!257 = metadata !{i32 73, i32 0, metadata !250, null}
!258 = metadata !{i32 79, i32 0, metadata !51, null}
!259 = metadata !{i32 17, i32 0, metadata !67, null}
!260 = metadata !{i32 22, i32 0, metadata !73, null}
!261 = metadata !{i32 27, i32 0, metadata !78, null}
!262 = metadata !{i32 69, i32 0, metadata !263, null}
!263 = metadata !{i32 786443, metadata !57, metadata !83, i32 69, i32 0, i32 0} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/fpclassify.c]
!264 = metadata !{i32 71, i32 0, metadata !265, null}
!265 = metadata !{i32 786443, metadata !57, metadata !263, i32 71, i32 0, i32 2} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/fpclassify.c]
!266 = metadata !{i32 73, i32 0, metadata !267, null}
!267 = metadata !{i32 786443, metadata !57, metadata !265, i32 73, i32 0, i32 4} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/fpclassify.c]
!268 = metadata !{i32 75, i32 0, metadata !269, null}
!269 = metadata !{i32 786443, metadata !57, metadata !267, i32 75, i32 0, i32 6} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/fpclassify.c]
!270 = metadata !{i32 76, i32 0, metadata !271, null}
!271 = metadata !{i32 786443, metadata !57, metadata !269, i32 75, i32 0, i32 7} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/fpclassify.c]
!272 = metadata !{i32 79, i32 0, metadata !83, null}
!273 = metadata !{i32 84, i32 0, metadata !274, null}
!274 = metadata !{i32 786443, metadata !57, metadata !86, i32 84, i32 0, i32 8} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/fpclassify.c]
!275 = metadata !{i32 86, i32 0, metadata !276, null}
!276 = metadata !{i32 786443, metadata !57, metadata !274, i32 86, i32 0, i32 10} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/fpclassify.c]
!277 = metadata !{i32 88, i32 0, metadata !278, null}
!278 = metadata !{i32 786443, metadata !57, metadata !276, i32 88, i32 0, i32 12} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/fpclassify.c]
!279 = metadata !{i32 90, i32 0, metadata !280, null}
!280 = metadata !{i32 786443, metadata !57, metadata !278, i32 90, i32 0, i32 14} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/fpclassify.c]
!281 = metadata !{i32 91, i32 0, metadata !282, null}
!282 = metadata !{i32 786443, metadata !57, metadata !280, i32 90, i32 0, i32 15} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/fpclassify.c]
!283 = metadata !{i32 94, i32 0, metadata !86, null}
!284 = metadata !{i32 100, i32 0, metadata !285, null}
!285 = metadata !{i32 786443, metadata !57, metadata !89, i32 100, i32 0, i32 16} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/fpclassify.c]
!286 = metadata !{i32 102, i32 0, metadata !287, null}
!287 = metadata !{i32 786443, metadata !57, metadata !285, i32 102, i32 0, i32 18} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/fpclassify.c]
!288 = metadata !{i32 104, i32 0, metadata !289, null}
!289 = metadata !{i32 786443, metadata !57, metadata !287, i32 104, i32 0, i32 20} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/fpclassify.c]
!290 = metadata !{i32 106, i32 0, metadata !291, null}
!291 = metadata !{i32 786443, metadata !57, metadata !289, i32 106, i32 0, i32 22} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/fpclassify.c]
!292 = metadata !{i32 107, i32 0, metadata !293, null}
!293 = metadata !{i32 786443, metadata !57, metadata !291, i32 106, i32 0, i32 23} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/fpclassify.c]
!294 = metadata !{i32 110, i32 0, metadata !89, null}
!295 = metadata !{i32 115, i32 0, metadata !92, null}
!296 = metadata !{i32 120, i32 0, metadata !95, null}
!297 = metadata !{i32 125, i32 0, metadata !98, null}
!298 = metadata !{i32 13, i32 0, metadata !299, null}
!299 = metadata !{i32 786443, metadata !102, metadata !104, i32 13, i32 0, i32 0} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/klee_div_zero_check.
!300 = metadata !{i32 14, i32 0, metadata !299, null}
!301 = metadata !{i32 15, i32 0, metadata !104, null}
!302 = metadata !{i32 15, i32 0, metadata !114, null}
!303 = metadata !{i32 16, i32 0, metadata !114, null}
!304 = metadata !{i32 21, i32 0, metadata !305, null}
!305 = metadata !{i32 786443, metadata !125, metadata !127, i32 21, i32 0, i32 0} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/klee_overshift_check
!306 = metadata !{i32 27, i32 0, metadata !307, null}
!307 = metadata !{i32 786443, metadata !125, metadata !305, i32 21, i32 0, i32 1} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/klee_overshift_check
!308 = metadata !{i32 29, i32 0, metadata !127, null}
!309 = metadata !{i32 16, i32 0, metadata !310, null}
!310 = metadata !{i32 786443, metadata !136, metadata !138, i32 16, i32 0, i32 0} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/klee_range.c]
!311 = metadata !{i32 17, i32 0, metadata !310, null}
!312 = metadata !{i32 19, i32 0, metadata !313, null}
!313 = metadata !{i32 786443, metadata !136, metadata !138, i32 19, i32 0, i32 1} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/klee_range.c]
!314 = metadata !{i32 22, i32 0, metadata !315, null}
!315 = metadata !{i32 786443, metadata !136, metadata !313, i32 21, i32 0, i32 3} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/klee_range.c]
!316 = metadata !{i32 25, i32 0, metadata !317, null}
!317 = metadata !{i32 786443, metadata !136, metadata !315, i32 25, i32 0, i32 4} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/klee_range.c]
!318 = metadata !{i32 26, i32 0, metadata !319, null}
!319 = metadata !{i32 786443, metadata !136, metadata !317, i32 25, i32 0, i32 5} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/klee_range.c]
!320 = metadata !{i32 27, i32 0, metadata !319, null}
!321 = metadata !{i32 28, i32 0, metadata !322, null}
!322 = metadata !{i32 786443, metadata !136, metadata !317, i32 27, i32 0, i32 6} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/klee_range.c]
!323 = metadata !{i32 29, i32 0, metadata !322, null}
!324 = metadata !{i32 32, i32 0, metadata !315, null}
!325 = metadata !{i32 34, i32 0, metadata !138, null}
!326 = metadata !{i32 19, i32 0, metadata !151, null}
!327 = metadata !{i32 21, i32 0, metadata !328, null}
!328 = metadata !{i32 786443, metadata !148, metadata !151, i32 19, i32 0, i32 0} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/klee_set_rounding_mo
!329 = metadata !{i32 23, i32 0, metadata !328, null}
!330 = metadata !{i32 25, i32 0, metadata !328, null}
!331 = metadata !{i32 27, i32 0, metadata !328, null}
!332 = metadata !{i32 29, i32 0, metadata !328, null}
!333 = metadata !{i32 31, i32 0, metadata !328, null}
!334 = metadata !{i32 33, i32 0, metadata !151, null}
!335 = metadata !{i32 16, i32 0, metadata !160, null}
!336 = metadata !{i32 17, i32 0, metadata !160, null}
!337 = metadata !{metadata !337, metadata !338, metadata !339}
!338 = metadata !{metadata !"llvm.vectorizer.width", i32 1}
!339 = metadata !{metadata !"llvm.vectorizer.unroll", i32 1}
!340 = metadata !{metadata !236, metadata !236, i64 0}
!341 = metadata !{metadata !341, metadata !338, metadata !339}
!342 = metadata !{i32 18, i32 0, metadata !160, null}
!343 = metadata !{i32 16, i32 0, metadata !344, null}
!344 = metadata !{i32 786443, metadata !177, metadata !179, i32 16, i32 0, i32 0} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/memmove.c]
!345 = metadata !{i32 19, i32 0, metadata !346, null}
!346 = metadata !{i32 786443, metadata !177, metadata !179, i32 19, i32 0, i32 1} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/memmove.c]
!347 = metadata !{i32 20, i32 0, metadata !348, null}
!348 = metadata !{i32 786443, metadata !177, metadata !346, i32 19, i32 0, i32 2} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/memmove.c]
!349 = metadata !{metadata !349, metadata !338, metadata !339}
!350 = metadata !{metadata !350, metadata !338, metadata !339}
!351 = metadata !{i32 22, i32 0, metadata !352, null}
!352 = metadata !{i32 786443, metadata !177, metadata !346, i32 21, i32 0, i32 3} ; [ DW_TAG_lexical_block ] [/home/fptesting/FPTesting/src/klee-float/build/runtime/Intrinsic//home/fptesting/FPTesting/src/klee-float/runtime/Intrinsic/memmove.c]
!353 = metadata !{i32 24, i32 0, metadata !352, null}
!354 = metadata !{i32 23, i32 0, metadata !352, null}
!355 = metadata !{metadata !355, metadata !338, metadata !339}
!356 = metadata !{metadata !356, metadata !338, metadata !339}
!357 = metadata !{i32 28, i32 0, metadata !179, null}
!358 = metadata !{i32 15, i32 0, metadata !193, null}
!359 = metadata !{i32 16, i32 0, metadata !193, null}
!360 = metadata !{metadata !360, metadata !338, metadata !339}
!361 = metadata !{metadata !361, metadata !338, metadata !339}
!362 = metadata !{i32 17, i32 0, metadata !193, null}
!363 = metadata !{i32 13, i32 0, metadata !207, null}
!364 = metadata !{i32 14, i32 0, metadata !207, null}
!365 = metadata !{i32 15, i32 0, metadata !207, null}
!366 = metadata !{i32 12, i32 0, metadata !222, null}
!367 = metadata !{i32 16, i32 0, metadata !226, null}
!368 = metadata !{i32 21, i32 0, metadata !229, null}
