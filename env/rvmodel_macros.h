#ifndef _RVMODEL_MACROS_H
#define _RVMODEL_MACROS_H

#define RVMODEL_DATA_SECTION \
    .pushsection .tohost,"aw",@progbits ;\
    .align 8 ;\
    .global tohost ;\
tohost: ;\
    .dword 0 ;\
    .align 8 ;\
    .global fromhost ;\
fromhost: ;\
    .dword 0 ;\
    .popsection

#define RVMODEL_BOOT_TO_MMODE

#define RVMODEL_HALT_PASS \
    .option push ;\
    .option norvc ;\
    la t0, tohost ;\
    li t1, 1 ;\
    sw t1, 0(t0) ;\
1:  j 1b ;\
    .option pop

#define RVMODEL_HALT_FAIL \
    .option push ;\
    .option norvc ;\
    la t0, tohost ;\
    li t1, 3 ;\
    sw t1, 0(t0) ;\
1:  j 1b ;\
    .option pop

#define RVMODEL_IO_WRITE_STR(_R1, _R2, _R3, _STR_PTR)

#define RVMODEL_INTERRUPT_LATENCY 10
#define RVMODEL_TIMER_INT_SOON_DELAY 100

#define RVMODEL_SET_MEXT_INT(_R1, _R2)
#define RVMODEL_CLR_MEXT_INT(_R1, _R2)
#define RVMODEL_SET_MSW_INT(_R1, _R2)
#define RVMODEL_CLR_MSW_INT(_R1, _R2)
#define RVMODEL_SET_SEXT_INT(_R1, _R2)
#define RVMODEL_CLR_SEXT_INT(_R1, _R2)
#define RVMODEL_SET_SSW_INT(_R1, _R2)
#define RVMODEL_CLR_SSW_INT(_R1, _R2)

#endif
