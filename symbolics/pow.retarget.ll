; ModuleID = 'pow-SYMBOLIC.linked.bc'
source_filename = "llvm-link"
target datalayout = "e-m:e-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

@.str = private unnamed_addr constant [6 x i8] c"input\00", align 1, !dbg !0
@.str.1 = private unnamed_addr constant [4 x i8] c"%a\0A\00", align 1, !dbg !7

; Function Attrs: noinline nounwind optnone ssp uwtable(sync)
define i32 @main() #0 !dbg !23 {
  %1 = alloca i32, align 4
  %2 = alloca [2 x float], align 4
  %3 = alloca float, align 4
  %4 = alloca float, align 4
  %5 = alloca float, align 4
  store i32 0, ptr %1, align 4
    #dbg_declare(ptr %2, !28, !DIExpression(), !33)
  %6 = getelementptr inbounds [2 x float], ptr %2, i64 0, i64 0, !dbg !34
  call void @klee_make_symbolic(ptr noundef %6, i64 noundef 8, ptr noundef @.str), !dbg !35
    #dbg_declare(ptr %3, !36, !DIExpression(), !38)
  %7 = getelementptr inbounds [2 x float], ptr %2, i64 0, i64 0, !dbg !39
  %8 = load float, ptr %7, align 4, !dbg !39
  store volatile float %8, ptr %3, align 4, !dbg !38
    #dbg_declare(ptr %4, !40, !DIExpression(), !41)
  %9 = getelementptr inbounds [2 x float], ptr %2, i64 0, i64 1, !dbg !42
  %10 = load float, ptr %9, align 4, !dbg !42
  store volatile float %10, ptr %4, align 4, !dbg !41
    #dbg_declare(ptr %5, !43, !DIExpression(), !44)
  %11 = load volatile float, ptr %3, align 4, !dbg !45
  %12 = load volatile float, ptr %4, align 4, !dbg !46
  %13 = call float @llvm.pow.f32(float %11, float %12), !dbg !47
  store volatile float %13, ptr %5, align 4, !dbg !44
  %14 = load volatile float, ptr %5, align 4, !dbg !48
  %15 = fpext float %14 to double, !dbg !48
  %16 = call i32 (ptr, ...) @printf(ptr noundef @.str.1, double noundef %15), !dbg !49
  ret i32 0, !dbg !50
}

declare void @klee_make_symbolic(ptr noundef, i64 noundef, ptr noundef) #1

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare float @llvm.pow.f32(float, float) #2

declare i32 @printf(ptr noundef, ...) #1

; Function Attrs: nounwind uwtable
define void @fp_injection(ptr nocapture readonly %psrc1, ptr nocapture readonly %psrc2, ptr nocapture readonly %pdest) #3 {
  %1 = bitcast ptr %psrc1 to ptr
  %2 = load double, ptr %1, align 8, !tbaa !51
  %3 = tail call i32 @__fpclassify(double %2) #7
  %4 = icmp eq i32 %3, 4
  %5 = bitcast ptr %psrc2 to ptr
  %6 = load double, ptr %5, align 8, !tbaa !51
  %7 = tail call i32 @__fpclassify(double %6) #7
  %8 = icmp eq i32 %7, 4
  %9 = and i1 %4, %8
  br i1 %9, label %10, label %36

10:                                               ; preds = %0
  %11 = bitcast double %6 to i64
  %12 = bitcast double %2 to i64
  %13 = lshr i64 %12, 52
  %14 = and i64 %13, 2047
  %15 = lshr i64 %11, 52
  %16 = and i64 %15, 2047
  %17 = sub nsw i64 %14, %16
  %18 = ashr i64 %17, 63
  %19 = add nsw i64 %18, %17
  %20 = xor i64 %19, %18
  %21 = icmp sgt i64 %20, 32
  br i1 %21, label %22, label %23

22:                                               ; preds = %10
  %putchar2 = tail call i32 @putchar(i32 49) #5
  br label %36

23:                                               ; preds = %10
  %24 = xor i64 %16, %14
  %25 = icmp ult i64 %14, %16
  %26 = select i1 %25, i64 %24, i64 0
  %27 = xor i64 %26, %14
  %28 = bitcast ptr %pdest to ptr
  %29 = load i64, ptr %28, align 8, !tbaa !55
  %30 = lshr i64 %29, 52
  %31 = and i64 %30, 2047
  %32 = sub nsw i64 %27, %31
  %33 = icmp sgt i64 %32, 40
  br i1 %33, label %34, label %35

34:                                               ; preds = %23
  %putchar1 = tail call i32 @putchar(i32 48) #5
  br label %36

35:                                               ; preds = %23
  %putchar = tail call i32 @putchar(i32 45) #5
  br label %36

36:                                               ; preds = %35, %34, %22, %0
  ret void
}

; Function Attrs: nounwind memory(none)
declare i32 @__fpclassify(double) #4

; Function Attrs: nounwind
declare i32 @putchar(i32) #5

; Function Attrs: nounwind uwtable
define void @cancel_injection(ptr nocapture readonly %psrc1, ptr nocapture readonly %psrc2, ptr nocapture readonly %pdest) #3 {
  %1 = bitcast ptr %psrc1 to ptr
  %2 = load i64, ptr %1, align 8, !tbaa !55
  %3 = lshr i64 %2, 52
  %4 = and i64 %3, 2047
  %5 = bitcast ptr %psrc2 to ptr
  %6 = load i64, ptr %5, align 8, !tbaa !55
  %7 = lshr i64 %6, 52
  %8 = and i64 %7, 2047
  %9 = xor i64 %8, %4
  %10 = icmp ult i64 %4, %8
  %11 = select i1 %10, i64 %9, i64 0
  %12 = xor i64 %11, %4
  %13 = bitcast ptr %pdest to ptr
  %14 = load i64, ptr %13, align 8, !tbaa !55
  %15 = lshr i64 %14, 52
  %16 = and i64 %15, 2047
  %17 = sub nsw i64 %12, %16
  %18 = icmp sgt i64 %17, 40
  %19 = bitcast i64 %2 to double
  %20 = tail call i32 @__fpclassify(double %19) #7
  %21 = icmp eq i32 %20, 4
  %22 = and i1 %18, %21
  %23 = bitcast i64 %6 to double
  %24 = tail call i32 @__fpclassify(double %23) #7
  %25 = icmp eq i32 %24, 4
  %26 = and i1 %22, %25
  br i1 %26, label %27, label %28

27:                                               ; preds = %0
  %putchar1 = tail call i32 @putchar(i32 48) #5
  br label %29

28:                                               ; preds = %0
  %putchar = tail call i32 @putchar(i32 42) #5
  br label %29

29:                                               ; preds = %28, %27
  ret void
}

; Function Attrs: nounwind uwtable
define void @round_injection(ptr nocapture readonly %psrc1, ptr nocapture readonly %psrc2, ptr nocapture readnone %pdest) #3 {
  %1 = bitcast ptr %psrc1 to ptr
  %2 = load i64, ptr %1, align 8, !tbaa !55
  %3 = lshr i64 %2, 52
  %4 = and i64 %3, 2047
  %5 = bitcast ptr %psrc2 to ptr
  %6 = load i64, ptr %5, align 8, !tbaa !55
  %7 = lshr i64 %6, 52
  %8 = and i64 %7, 2047
  %9 = sub nsw i64 %4, %8
  %10 = ashr i64 %9, 63
  %11 = add nsw i64 %10, %9
  %12 = xor i64 %11, %10
  %13 = icmp sgt i64 %12, 32
  %14 = bitcast i64 %2 to double
  %15 = tail call i32 @__fpclassify(double %14) #7
  %16 = icmp eq i32 %15, 4
  %17 = and i1 %13, %16
  %18 = bitcast i64 %6 to double
  %19 = tail call i32 @__fpclassify(double %18) #7
  %20 = icmp eq i32 %19, 4
  %21 = and i1 %17, %20
  br i1 %21, label %22, label %23

22:                                               ; preds = %0
  %putchar1 = tail call i32 @putchar(i32 49) #5
  br label %24

23:                                               ; preds = %0
  %putchar = tail call i32 @putchar(i32 35) #5
  br label %24

24:                                               ; preds = %23, %22
  ret void
}

; Function Attrs: nounwind uwtable
define void @log_sampled_fp_injection(ptr nocapture readonly %psrc1, ptr nocapture readonly %psrc2, ptr nocapture readonly %pdest, ptr nocapture %pcounter, i32 %step, i32 %injection) #3 {
  %1 = load i32, ptr %pcounter, align 4, !tbaa !57
  %2 = icmp eq i32 %1, 2147483647
  br i1 %2, label %round_injection.exit, label %3

3:                                                ; preds = %0
  %4 = add nsw i32 %1, 1
  store i32 %4, ptr %pcounter, align 4, !tbaa !57
  %5 = sitofp i32 %4 to double
  %6 = tail call double @log10(double %5) #5
  %7 = tail call double @ceil(double %6) #7
  %8 = tail call double @pow(double 1.000000e+01, double %7) #5
  %9 = fptosi double %8 to i32
  %10 = icmp eq i32 %9, 1
  %11 = load i32, ptr %pcounter, align 4, !tbaa !57
  %.op = sdiv i32 %9, 10
  %12 = select i1 %10, i32 1, i32 %.op
  %13 = mul nsw i32 %12, %step
  %14 = srem i32 %11, %13
  %15 = icmp eq i32 %14, 0
  br i1 %15, label %16, label %round_injection.exit

16:                                               ; preds = %3
  switch i32 %injection, label %round_injection.exit [
    i32 2, label %17
    i32 0, label %18
    i32 1, label %19
  ]

17:                                               ; preds = %16
  tail call void @fp_injection(ptr %psrc1, ptr %psrc2, ptr %pdest)
  br label %round_injection.exit

18:                                               ; preds = %16
  tail call void @cancel_injection(ptr %psrc1, ptr %psrc2, ptr %pdest)
  br label %round_injection.exit

19:                                               ; preds = %16
  %20 = bitcast ptr %psrc1 to ptr
  %21 = load i64, ptr %20, align 8, !tbaa !55
  %22 = lshr i64 %21, 52
  %23 = and i64 %22, 2047
  %24 = bitcast ptr %psrc2 to ptr
  %25 = load i64, ptr %24, align 8, !tbaa !55
  %26 = lshr i64 %25, 52
  %27 = and i64 %26, 2047
  %28 = sub nsw i64 %23, %27
  %29 = ashr i64 %28, 63
  %30 = add nsw i64 %29, %28
  %31 = xor i64 %30, %29
  %32 = icmp sgt i64 %31, 32
  %33 = bitcast i64 %21 to double
  %34 = tail call i32 @__fpclassify(double %33) #7
  %35 = icmp eq i32 %34, 4
  %36 = and i1 %32, %35
  %37 = bitcast i64 %25 to double
  %38 = tail call i32 @__fpclassify(double %37) #7
  %39 = icmp eq i32 %38, 4
  %40 = and i1 %36, %39
  br i1 %40, label %41, label %42

41:                                               ; preds = %19
  %putchar1.i = tail call i32 @putchar(i32 49) #5
  br label %round_injection.exit

42:                                               ; preds = %19
  %putchar.i = tail call i32 @putchar(i32 35) #5
  br label %round_injection.exit

round_injection.exit:                             ; preds = %42, %41, %18, %17, %16, %3, %0
  ret void
}

; Function Attrs: nounwind
declare double @log10(double) #6

; Function Attrs: nounwind memory(none)
declare double @ceil(double) #4

; Function Attrs: nounwind
declare double @pow(double, double) #6

; Function Attrs: nounwind uwtable
define void @uniform_sampled_fp_injection(ptr nocapture readonly %psrc1, ptr nocapture readonly %psrc2, ptr nocapture readonly %pdest, ptr nocapture %pcounter, i32 %step, i32 %injection) #3 {
  %1 = load i32, ptr %pcounter, align 4, !tbaa !57
  %2 = icmp eq i32 %1, 2147483647
  br i1 %2, label %round_injection.exit, label %3

3:                                                ; preds = %0
  %4 = add nsw i32 %1, 1
  store i32 %4, ptr %pcounter, align 4, !tbaa !57
  %5 = srem i32 %4, %step
  %6 = icmp eq i32 %5, 0
  br i1 %6, label %7, label %round_injection.exit

7:                                                ; preds = %3
  switch i32 %injection, label %round_injection.exit [
    i32 2, label %8
    i32 0, label %9
    i32 1, label %10
  ]

8:                                                ; preds = %7
  tail call void @fp_injection(ptr %psrc1, ptr %psrc2, ptr %pdest)
  br label %round_injection.exit

9:                                                ; preds = %7
  tail call void @cancel_injection(ptr %psrc1, ptr %psrc2, ptr %pdest)
  br label %round_injection.exit

10:                                               ; preds = %7
  %11 = bitcast ptr %psrc1 to ptr
  %12 = load i64, ptr %11, align 8, !tbaa !55
  %13 = lshr i64 %12, 52
  %14 = and i64 %13, 2047
  %15 = bitcast ptr %psrc2 to ptr
  %16 = load i64, ptr %15, align 8, !tbaa !55
  %17 = lshr i64 %16, 52
  %18 = and i64 %17, 2047
  %19 = sub nsw i64 %14, %18
  %20 = ashr i64 %19, 63
  %21 = add nsw i64 %20, %19
  %22 = xor i64 %21, %20
  %23 = icmp sgt i64 %22, 32
  %24 = bitcast i64 %12 to double
  %25 = tail call i32 @__fpclassify(double %24) #7
  %26 = icmp eq i32 %25, 4
  %27 = and i1 %23, %26
  %28 = bitcast i64 %16 to double
  %29 = tail call i32 @__fpclassify(double %28) #7
  %30 = icmp eq i32 %29, 4
  %31 = and i1 %27, %30
  br i1 %31, label %32, label %33

32:                                               ; preds = %10
  %putchar1.i = tail call i32 @putchar(i32 49) #5
  br label %round_injection.exit

33:                                               ; preds = %10
  %putchar.i = tail call i32 @putchar(i32 35) #5
  br label %round_injection.exit

round_injection.exit:                             ; preds = %33, %32, %9, %8, %7, %3, %0
  ret void
}

attributes #0 = { noinline nounwind optnone ssp uwtable(sync) "frame-pointer"="non-leaf" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+altnzcv,+ccdp,+ccidx,+ccpp,+complxnum,+crc,+dit,+dotprod,+flagm,+fp-armv8,+fp16fml,+fptoint,+fullfp16,+jsconv,+lse,+neon,+pauth,+perfmon,+predres,+ras,+rcpc,+rdm,+sb,+sha2,+sha3,+specrestrict,+ssbs,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8a,+zcm,+zcz" }
attributes #1 = { "frame-pointer"="non-leaf" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+altnzcv,+ccdp,+ccidx,+ccpp,+complxnum,+crc,+dit,+dotprod,+flagm,+fp-armv8,+fp16fml,+fptoint,+fullfp16,+jsconv,+lse,+neon,+pauth,+perfmon,+predres,+ras,+rcpc,+rdm,+sb,+sha2,+sha3,+specrestrict,+ssbs,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8a,+zcm,+zcz" }
attributes #2 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #3 = { nounwind uwtable "frame-pointer"="none" "less-precise-fpmad"="false" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "stack-protector-buffer-size"="8" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #4 = { nounwind memory(none) "frame-pointer"="none" "less-precise-fpmad"="false" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "stack-protector-buffer-size"="8" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #5 = { nounwind }
attributes #6 = { nounwind "frame-pointer"="none" "less-precise-fpmad"="false" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "stack-protector-buffer-size"="8" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #7 = { nounwind memory(none) }

!llvm.dbg.cu = !{!12}
!llvm.ident = !{!14, !15}
!llvm.module.flags = !{!16, !17, !18, !19, !20, !21, !22}

!0 = !DIGlobalVariableExpression(var: !1, expr: !DIExpression())
!1 = distinct !DIGlobalVariable(scope: null, file: !2, line: 7, type: !3, isLocal: true, isDefinition: true)
!2 = !DIFile(filename: "pow-SYMBOLIC.c", directory: "/Users/xieyushan/Documents/code/Numerical_instabilities/symbolics", checksumkind: CSK_MD5, checksum: "9865dc500cf6a741e920f56375e4e434")
!3 = !DICompositeType(tag: DW_TAG_array_type, baseType: !4, size: 48, elements: !5)
!4 = !DIBasicType(name: "char", size: 8, encoding: DW_ATE_signed_char)
!5 = !{!6}
!6 = !DISubrange(count: 6)
!7 = !DIGlobalVariableExpression(var: !8, expr: !DIExpression())
!8 = distinct !DIGlobalVariable(scope: null, file: !2, line: 11, type: !9, isLocal: true, isDefinition: true)
!9 = !DICompositeType(tag: DW_TAG_array_type, baseType: !4, size: 32, elements: !10)
!10 = !{!11}
!11 = !DISubrange(count: 4)
!12 = distinct !DICompileUnit(language: DW_LANG_C11, file: !2, producer: "Homebrew clang version 20.1.4", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, globals: !13, splitDebugInlining: false, nameTableKind: Apple, sysroot: "/Library/Developer/CommandLineTools/SDKs/MacOSX15.sdk", sdk: "MacOSX15.sdk")
!13 = !{!0, !7}
!14 = !{!"Homebrew clang version 20.1.4"}
!15 = !{!"Ubuntu clang version 3.4.2- (branches/release_34) (based on LLVM 3.4.2)"}
!16 = !{i32 2, !"SDK Version", [2 x i32] [i32 15, i32 5]}
!17 = !{i32 7, !"Dwarf Version", i32 5}
!18 = !{i32 2, !"Debug Info Version", i32 3}
!19 = !{i32 1, !"wchar_size", i32 4}
!20 = !{i32 8, !"PIC Level", i32 2}
!21 = !{i32 7, !"uwtable", i32 1}
!22 = !{i32 7, !"frame-pointer", i32 1}
!23 = distinct !DISubprogram(name: "main", scope: !2, file: !2, line: 5, type: !24, scopeLine: 5, spFlags: DISPFlagDefinition, unit: !12, retainedNodes: !27)
!24 = !DISubroutineType(types: !25)
!25 = !{!26}
!26 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!27 = !{}
!28 = !DILocalVariable(name: "in", scope: !23, file: !2, line: 6, type: !29)
!29 = !DICompositeType(tag: DW_TAG_array_type, baseType: !30, size: 64, elements: !31)
!30 = !DIBasicType(name: "float", size: 32, encoding: DW_ATE_float)
!31 = !{!32}
!32 = !DISubrange(count: 2)
!33 = !DILocation(line: 6, column: 11, scope: !23)
!34 = !DILocation(line: 7, column: 24, scope: !23)
!35 = !DILocation(line: 7, column: 5, scope: !23)
!36 = !DILocalVariable(name: "x", scope: !23, file: !2, line: 8, type: !37)
!37 = !DIDerivedType(tag: DW_TAG_volatile_type, baseType: !30)
!38 = !DILocation(line: 8, column: 20, scope: !23)
!39 = !DILocation(line: 8, column: 24, scope: !23)
!40 = !DILocalVariable(name: "y", scope: !23, file: !2, line: 9, type: !37)
!41 = !DILocation(line: 9, column: 20, scope: !23)
!42 = !DILocation(line: 9, column: 24, scope: !23)
!43 = !DILocalVariable(name: "r", scope: !23, file: !2, line: 10, type: !37)
!44 = !DILocation(line: 10, column: 20, scope: !23)
!45 = !DILocation(line: 10, column: 29, scope: !23)
!46 = !DILocation(line: 10, column: 32, scope: !23)
!47 = !DILocation(line: 10, column: 24, scope: !23)
!48 = !DILocation(line: 11, column: 20, scope: !23)
!49 = !DILocation(line: 11, column: 5, scope: !23)
!50 = !DILocation(line: 12, column: 5, scope: !23)
!51 = !{!52, !52, i64 0}
!52 = !{!"double", !53, i64 0}
!53 = !{!"omnipotent char", !54, i64 0}
!54 = !{!"Simple C/C++ TBAA"}
!55 = !{!56, !56, i64 0}
!56 = !{!"long", !53, i64 0}
!57 = !{!58, !58, i64 0}
!58 = !{!"int", !53, i64 0}
