        
.global benchmark_load

benchmark_load:
  /*
        cbz     x2, .LBB4_3
        mov     x8, xzr
        sub     x9, x1, #1
.LBB4_2:
        and     x10, x8, x9
        add     x8, x8, #1
        lsl     x9, x10, #2
        cmp     x2, x8

        ldr     x11, [x0, x10]

        b.ne    .LBB4_2
.LBB4_3:
        ret

  */

        cbz     x1, .LBB8_2
.LBB8_1:
        ldr     w8, [x0]
        add     x0, x0, #4

        subs    x1, x1, #1
        b.ne    .LBB8_1
.LBB8_2:
        ret
