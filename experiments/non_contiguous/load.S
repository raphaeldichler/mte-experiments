
#ifdef __x86_64__
.intel_syntax noprefix
#endif

.global benchmark

benchmark:
#ifdef __aarch64__
        cbz     x1, .LBB2_2
.LBB2_1:
        subs    x1, x1, #1

        ldr     x0, [x0]

        b.ne    .LBB2_1
.LBB2_2:
        ret
#endif
