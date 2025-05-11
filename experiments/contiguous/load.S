
#ifdef __x86_64__
.intel_syntax noprefix
#endif

.global benchmark

benchmark:
#ifdef __aarch64__
        cbz     x1, .LBB11_2
.LBB11_1:

        ldr     w8, [x0]
        subs    x1, x1, #1

        str     w8, [x0], #4
        b.ne    .LBB11_1
.LBB11_2:
        ret
#endif
