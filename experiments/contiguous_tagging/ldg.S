
.global benchmark_ldg

benchmark_ldg:
        cbz     x1, .LBB8_2
.LBB8_1:
        subs    x1, x1, #16
    
        ldg     x4, [x0]
        add     x0, x0, #16
        b.ne    .LBB8_1
.LBB8_2:
        ret
