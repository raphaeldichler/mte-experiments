
.global benchmark_st2g

benchmark_st2g:
        cbz     x1, .LBB8_2
.LBB8_1:
        subs    x1, x1, #32
    
        st2g     x0, [x0]
        add     x0, x0, #32
        b.ne    .LBB8_1
.LBB8_2:
        ret
