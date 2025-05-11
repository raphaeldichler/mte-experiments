
.global benchmark_store

benchmark_store:
  /*
        cbz     x1, .LBB2_3
        mov     x8, xzr
        sub     x9, x1, #1
.LBB2_2:
        and     x10, x8, x9
        subs    x1, x1, #1
        add     x8, x8, #4

        str     w10, [x0, x10, lsl #2]

        b.ne    .LBB2_2
.LBB2_3:
        ret
  */
        cbz     x1, .LBB8_2
.LBB8_1:
        subs    x1, x1, #1

        str     w2, [x0]
        add     x0, x0, #4

        b.ne    .LBB8_1
.LBB8_2:
        ret
