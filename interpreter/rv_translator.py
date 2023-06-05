WORD_WIDTH = 4
INST_WIDTH = 3 * WORD_WIDTH

CSR_MASK = int(0xffff8000)
GPR_MASK = int(0xffffc000)
PRC_MASK = int(0xffffe000)

T0  = int(0xffffc080)
T1  = int(0xffffc084)
T2  = int(0xffffc088)
T3  = int(0xffffc08c)
T4  = int(0xffffc090)
T5  = int(0xffffc094)
T6  = int(0xffffc098)
T7  = int(0xffffc09c)

CONST_POW = [int(0xffffc100) + x * WORD_WIDTH for x in range(0,32)]
CONST_ONE = [int(0xffffc180) + x * WORD_WIDTH for x in range(0,32)]

RZ  = int(0xffffc200)

ADD_START   = int(0x00000000)
ADD_END     = int(0x00000054)
SUB_START   = int(0x00000060)
SUB_END     = int(0x000000b4)
AND_START   = int(0x000000c0)
AND_END     = int(0x00000234)
OR_START    = int(0x00000240)
OR_END      = int(0x000003b4)
XOR_START   = int(0x000003c0)
XOR_END     = int(0x00000534)
SLT_START   = int(0x00000540)
SLT_END     = int(0x00000594)
SLTU_START  = int(0x000005a0)
SLTU_END    = int(0x000006b4)
SLL_START   = int(0x000006c0)
SLL_END     = int(0x00000774)
SRL_START   = int(0x00000780)
SRL_END     = int(0x000009b4)
SRA_START   = int(0x000009c0)
SRA_END     = int(0x00000bf4)
BEQ_START   = int(0x00000c00)
BEQ_END     = int(0x00000c54)
BLT_START   = int(0x00000c60)
BLT_END     = int(0x00000cb4)
BLTU_START  = int(0x00000cc0)
BLTU_END    = int(0x00000dd4)
LW_START    = int(0x00000de0)
LW_END      = int(0x00000e94)
SW_START    = int(0x00000ea0)
SW_END      = int(0x00000f54)
    
def subleq(a, b, c):
    return [a, b, c]

def _add():
    """ add rd,rs1,rs2
        
    Initial state:
        T1: (rs1)
        T2: (rs2)
    Pseudocode:
        T0 = 0
        T0 = T0 - (0 - T1)
        T0 = T0 - (0 - T2)
    Final state:
        T0: (rs1) + (rs2)
    
    Returns:
        list: target instruction sequence
    """
    _start = ADD_START | PRC_MASK
    return [
        subleq(T0, T0, _start + 1 * INST_WIDTH),
        subleq(RZ, RZ, _start + 2 * INST_WIDTH),
        subleq(RZ, T1, _start + 3 * INST_WIDTH),
        subleq(T0, RZ, _start + 4 * INST_WIDTH),
        subleq(RZ, RZ, _start + 5 * INST_WIDTH),
        subleq(RZ, T2, _start + 6 * INST_WIDTH),
        subleq(T0, RZ, _start + 7 * INST_WIDTH),
        subleq(RZ, RZ, _start)
    ]

def _sub():
    """ sub rd,rs1,rs2

    Initial state:
        T1: (rs1)
        T2: (rs2)
    Pseudocode:
        T0 = 0
        T0 = T0 - (0 - T1)
        T0 = T0 - T2
    Final state:
        T0: (rs1) - (rs2)

    Returns:
        list: target instruction sequence
    """
    _start = SUB_START | PRC_MASK
    return [
        subleq(T0, T0, _start + 1 * INST_WIDTH),
        subleq(RZ, RZ, _start + 2 * INST_WIDTH),
        subleq(RZ, T1, _start + 3 * INST_WIDTH),
        subleq(T0, RZ, _start + 4 * INST_WIDTH),
        subleq(T0, T2, _start + 5 * INST_WIDTH),
        subleq(RZ, RZ, _start + 6 * INST_WIDTH),
        subleq(RZ, RZ, _start + 7 * INST_WIDTH),
        subleq(RZ, RZ, _start)
    ]

def _and(rd, rs1, rs2, line):
    """ and rd,rs1,rs2

    Initial state:
        T1: (rs1)
        T2: (rs2)
    Pseudocode:
        T0 = 0
        mask = 1 << 31
        while mask > 0:
            if T1 < mask, goto L0.
            T1 = T1 - mask
            if T2 < mask, goto L1.
            T2 = T2 - mask
            T0 = T0 - (0 - mask)
        L0:
            if T2 < mask, goto L1.
            T2 = T2 - mask
        L1:
            mask = mask >> 1
    Final state:
        T0: (rs1) & (rs2)

    Returns:
        list: target instruction sequence
    """
    _start = AND_START | PRC_MASK
    return [
        # T0 = 0
        subleq(T0, T0, _start + 1 * INST_WIDTH),
        # T5 = 2^31
        subleq(RZ, RZ, _start + 2 * INST_WIDTH),
        subleq(T5, T5, _start + 3 * INST_WIDTH),
        subleq(RZ, CONST_POW[31], _start + 4 * INST_WIDTH),
        subleq(T5, RZ, _start + 5 * INST_WIDTH),
        # T6 = 2^31-1
        subleq(RZ, RZ, _start + 6 * INST_WIDTH),
        subleq(T6, T6, _start + 7 * INST_WIDTH),
        subleq(RZ, CONST_ONE[31], _start + 8 * INST_WIDTH),
        subleq(T6, RZ, _start + 9 * INST_WIDTH),
        # while T5 > 0: (assuming mask = T5)
        subleq(RZ, RZ, _start + 10 * INST_WIDTH),
        subleq(T5, RZ, _start + 31 * INST_WIDTH),
        # T3 = T1
        subleq(T3, T3, _start + 12 * INST_WIDTH),
        subleq(RZ, T1, _start + 13 * INST_WIDTH),
        subleq(T3, RZ, _start + 14 * INST_WIDTH),
        # T4 = T2
        subleq(RZ, RZ, _start + 15 * INST_WIDTH),
        subleq(T4, T4, _start + 16 * INST_WIDTH),
        subleq(RZ, T2, _start + 17 * INST_WIDTH),
        subleq(T4, RZ, _start + 18 * INST_WIDTH),
        # if T3 < mask, goto L0.
        subleq(T3, T6, _start + 25 * INST_WIDTH),
        # T1 = T1 - mask
        subleq(T1, T5, _start + 20 * INST_WIDTH),
        # if T4 < mask, goto L1.
        subleq(T4, T6, _start + 26 * INST_WIDTH),
        # T2 = T2 - T5
        subleq(T2, T5, _start + 22 * INST_WIDTH),
        # T0 = T0 + mask
        subleq(RZ, RZ, _start + 23 * INST_WIDTH),
        subleq(RZ, T5, _start + 24 * INST_WIDTH),
        subleq(T0, RZ, _start + 25 * INST_WIDTH),
        # goto L1.
        subleq(RZ, RZ, _start + 28 * INST_WIDTH),
    # L0:
        # if T4 < mask, goto L1.
        subleq(T4, T6, _start + 28 * INST_WIDTH),
        # T2 = T2 - T5
        subleq(T2, T5, _start + 28 * INST_WIDTH),
    # L1:
        # mask = mask >> 1
        subleq(_start + 3 * INST_WIDTH + WORD_WIDTH, CONST_POW[2],  _start + 28 * INST_WIDTH),
        subleq(_start + 7 * INST_WIDTH + WORD_WIDTH, CONST_POW[2],  _start + 29 * INST_WIDTH),
        subleq(RZ, RZ, _start + 9 * INST_WIDTH),
        subleq(RZ, RZ, _start + 31 * INST_WIDTH),
    # EXIT:
        subleq(RZ, RZ, _start)
    ]

def _or(rd, rs1, rs2, line):
    """ or rd,rs1,rs2

    Initial state:
        T1: (rs1)
        T2: (rs2)
    Pseudocode:
        T0 <= 0
        mask <= 1 << 31
        while mask >= 0:
            if T1 < mask, goto L0.
            T1 = T1 - mask
            if T2 < mask, goto L1.
            T2 = T2 - mask
            goto L1.
        L0:
            if T2 < mask, goto L2.
            T2 = T2 - mask
        L1:
            T0 <= T0 - (0 - mask)
        L2:
            mask <= mask >> 1
    Final state:
        T0: (rs1) | (rs2)

    Returns:
        list: target instruction sequence
    """
    _start = OR_START | PRC_MASK
    return [
        # T0 = 0
        subleq(T0, T0, _start + 1 * INST_WIDTH),
        # T5 = 2^31
        subleq(RZ, RZ, _start + 2 * INST_WIDTH),
        subleq(T5, T5, _start + 3 * INST_WIDTH),
        subleq(RZ, CONST_POW[31], _start + 4 * INST_WIDTH),
        subleq(T5, RZ, _start + 5 * INST_WIDTH),
        # T6 = 2^31-1
        subleq(RZ, RZ, _start + 6 * INST_WIDTH),
        subleq(T6, T6, _start + 7 * INST_WIDTH),
        subleq(RZ, CONST_ONE[31], _start + 8 * INST_WIDTH),
        subleq(T6, RZ, _start + 9 * INST_WIDTH),
        # while T5 > 0: (assuming mask = T5)
        subleq(RZ, RZ, _start + 10 * INST_WIDTH),
        subleq(T5, RZ, _start + 31 * INST_WIDTH),
        # T3 = T1
        subleq(T3, T3, _start + 12 * INST_WIDTH),
        subleq(RZ, T1, _start + 13 * INST_WIDTH),
        subleq(T3, RZ, _start + 14 * INST_WIDTH),
        # T4 = T2
        subleq(RZ, RZ, _start + 15 * INST_WIDTH),
        subleq(T4, T4, _start + 16 * INST_WIDTH),
        subleq(RZ, T2, _start + 17 * INST_WIDTH),
        subleq(T4, RZ, _start + 18 * INST_WIDTH),
        
        # if T3 < mask, goto L0.
        subleq(T3, T6, _start + 23 * INST_WIDTH),
        # T1 = T1 - mask
        subleq(T1, T5, _start + 20 * INST_WIDTH),
        # if T4 < mask, L1.
        subleq(T4, T6, _start + 25 * INST_WIDTH),
        # T2 = T2 - mask
        subleq(T2, T5, _start + 22 * INST_WIDTH),
        # goto L1.
        subleq(RZ, RZ, _start + 25 * INST_WIDTH),
    # L0:
        # if T4 < mask, goto L2.
        subleq(T4, T6, _start + 28 * INST_WIDTH),
        # T2 = T2 - mask
        subleq(T2, T5, _start + 25 * INST_WIDTH),
    # L1:
        # T0 = T0 + mask
        subleq(RZ, RZ, _start + 26 * INST_WIDTH),
        subleq(RZ, T5, _start + 27 * INST_WIDTH),
        subleq(T0, RZ, _start + 28 * INST_WIDTH),
    # L2:
        # mask = mask >> 1
        subleq(_start + 3 * INST_WIDTH + WORD_WIDTH, CONST_POW[2],  _start + 29 * INST_WIDTH),
        subleq(_start + 7 * INST_WIDTH + WORD_WIDTH, CONST_POW[2],  _start + 30 * INST_WIDTH),
        subleq(RZ, RZ, _start + 9 * INST_WIDTH),
    # EXIT:
        subleq(RZ, RZ, _start)
    ]

def _xor(rd, rs1, rs2, line):
    """ xor rd,rs1,rs2

    Initial state:
        T1: (rs1)
        T2: (rs2)
    Pseudocode:
        T0 <= 0
        mask <= 1 << 31
        while mask >= 0:
            if T1 < mask, goto L0.
            T1 = T1 - mask
            if T2 < mask, goto L1.
            T2 = T2 - mask
            goto L2.
        L0:
            if T2 < mask, goto L2.
            T2 = T2 - mask
        L1:
            T0 <= T0 - (0 - mask)
        L2:
            mask <= mask >> 1
    Final state:
        T0: (rs1) ^ (rs2)

    Returns:
        list: target instruction sequence
    """
    _start = XOR_START | PRC_MASK
    return [
        # T0 = 0
        subleq(T0, T0, _start + 1 * INST_WIDTH),
        # T5 = 2^31
        subleq(RZ, RZ, _start + 2 * INST_WIDTH),
        subleq(T5, T5, _start + 3 * INST_WIDTH),
        subleq(RZ, CONST_POW[31], _start + 4 * INST_WIDTH),
        subleq(T5, RZ, _start + 5 * INST_WIDTH),
        # T6 = 2^31-1
        subleq(RZ, RZ, _start + 6 * INST_WIDTH),
        subleq(T6, T6, _start + 7 * INST_WIDTH),
        subleq(RZ, CONST_ONE[31], _start + 8 * INST_WIDTH),
        subleq(T6, RZ, _start + 9 * INST_WIDTH),
        # while T5 > 0: (assuming mask = T5)
        subleq(RZ, RZ, _start + 10 * INST_WIDTH),
        subleq(T5, RZ, _start + 31 * INST_WIDTH),
        # T3 = T1
        subleq(T3, T3, _start + 12 * INST_WIDTH),
        subleq(RZ, T1, _start + 13 * INST_WIDTH),
        subleq(T3, RZ, _start + 14 * INST_WIDTH),
        # T4 = T2
        subleq(RZ, RZ, _start + 15 * INST_WIDTH),
        subleq(T4, T4, _start + 16 * INST_WIDTH),
        subleq(RZ, T2, _start + 17 * INST_WIDTH),
        subleq(T4, RZ, _start + 18 * INST_WIDTH),
        
        # if T3 < mask, goto L0.
        subleq(T3, T6, _start + 23 * INST_WIDTH),
        # T1 = T1 - mask
        subleq(T1, T5, _start + 20 * INST_WIDTH),
        # if T4 < mask, goto L1.
        subleq(T4, T6, _start + 25 * INST_WIDTH),
        # T2 = T2 - mask
        subleq(T2, T5, _start + 22 * INST_WIDTH),
        # goto L2.
        subleq(RZ, RZ, _start + 29 * INST_WIDTH),
    # L0:
        # if T4 < mask, goto L2.
        subleq(T4, T6, _start + 28 * INST_WIDTH),
        # T2 = T2 - mask
        subleq(T2, T5, _start + 25 * INST_WIDTH),
    # L1:
        # T0 = T0 + mask
        subleq(RZ, RZ, _start + 26 * INST_WIDTH),
        subleq(RZ, T5, _start + 27 * INST_WIDTH),
        subleq(T0, RZ, _start + 28 * INST_WIDTH),
    # L2:
        # mask = mask >> 1
        subleq(_start + 3 * INST_WIDTH + WORD_WIDTH, CONST_POW[2],  _start + 29 * INST_WIDTH),
        subleq(_start + 7 * INST_WIDTH + WORD_WIDTH, CONST_POW[2],  _start + 30 * INST_WIDTH),
        subleq(RZ, RZ, _start + 9 * INST_WIDTH),
    # EXIT:
        subleq(RZ, RZ, _start)
    ]


def _slt(rd, rs1, rs2, line):
    """ slt rd,rs1,rs2

    Initial state:
        T1: (rs1)
        T2: (rs2)
    Pseudocode:
        T0 <= 0
        if T2 - T1 <= 0, goto L0.
        T0 <= 1
        L0:
    Final state:
        T0: signed(rs1) < signed(rs2) ? 1 : 0

    Returns:
        list: target instruction sequence
    """
    _start = SLT_START | PRC_MASK
    return [
        subleq(T0, T0, _start + 1 * INST_WIDTH),
        subleq(T2, T1, _start + 7 * INST_WIDTH),
        subleq(RZ, RZ, _start + 3 * INST_WIDTH),
        subleq(RZ, CONST_POW[0], _start + 4 * INST_WIDTH),
        subleq(T0, RZ, _start + 5 * INST_WIDTH),
        subleq(RZ, RZ, _start + 6 * INST_WIDTH),
        subleq(RZ, RZ, _start + 7 * INST_WIDTH),
        subleq(RZ, RZ, _start)
    ]
        
def _sltu(rd, rs1, rs2, line):
    """ sltu rd,rs1,rs2

    Initial state:
        T1: (rs1)
        T2: (rs2)
    Pseudocode:
        T0 <= 0
        T3 <= T1 - T2
        if T3 < 0 and !(T1 < 0 and T2 > 0), goto L0.
        if T3 > 0 and  (T1 > 0 and T2 < 0), goto L0.
        T0 <= 1
        L0:
    Final state:
        T0: unsigned(rs1) < unsigned(rs2) ? 1 : 0

    Returns:
        list: target instruction sequence
    """
    _start = SLTU_START | PRC_MASK
    return [
        # T0 = 0
        subleq(T0, T0, _start + 1 * INST_WIDTH),
        # T3 = T1
        subleq(RZ, RZ, _start + 2 * INST_WIDTH),
        subleq(T3, T3, _start + 3 * INST_WIDTH),
        subleq(RZ, T1, _start + 4 * INST_WIDTH),
        subleq(T3, RZ, _start + 5 * INST_WIDTH),
        # if T1 <= T2, goto L0.
        subleq(T3, T2, _start + 10 * INST_WIDTH),
        # if T2 >= 0, goto EXIT.
        subleq(RZ, RZ, _start + 7 * INST_WIDTH),
        subleq(RZ, T2, _start + 23 * INST_WIDTH),
        # if T1 <= 0, goto EXIT
        subleq(RZ, RZ, _start + 9 * INST_WIDTH),
        subleq(T3, RZ, _start + 23 * INST_WIDTH),
        # goto L2.
        subleq(RZ, RZ, _start + 18 * INST_WIDTH),
    # L0:
        # if T1 == T2, goto EXIT
        subleq(RZ, RZ, _start + 12 * INST_WIDTH),
        subleq(T3, RZ, _start + 23 * INST_WIDTH),
    # L1:
        # if T1 >= 0, goto L2.
        subleq(RZ, RZ, _start + 14 * INST_WIDTH),
        subleq(RZ, T1, _start + 18 * INST_WIDTH),
        # if T2 <= 0, goto L2.
        subleq(RZ, RZ, _start + 16 * INST_WIDTH),
        subleq(T2, RZ, _start + 18 * INST_WIDTH),
        # goto EXIT.
        subleq(RZ, RZ, _start + 23 * INST_WIDTH),
    # L2:
        # T0 = 1
        subleq(RZ, RZ, _start + 19 * INST_WIDTH),
        subleq(RZ, CONST_POW[0], _start + 20 * INST_WIDTH),
        subleq(T0, RZ, _start + 21 * INST_WIDTH),
    # EXIT:
        subleq(RZ, RZ, _start + 23 * INST_WIDTH),
        subleq(RZ, RZ, _start + 23 * INST_WIDTH),
        subleq(RZ, RZ, _start)
    ]

def _sll(rd, rs1, rs2, line):
    """ sll rd,rs1,rs2

    Initial state:
        T1: (rs1)
        T2: (rs2)
    Pseudocode:
        T0 <= 0
        T0 <= T0 - (0 - T1)
        L0:
            if T2 <= 0, goto L1.
            T2 <= T2 - 1
            T0 <= T0 - (0 - T0)
            goto L0
        L1:
    Final state:
        T0: (rs1) << (rs2)

    Returns:
        list: target instruction sequence
    """
    _start = SLL_START | PRC_MASK
    return [
        # T0 = T1
        subleq(T0, T0, _start + 1 * INST_WIDTH),
        subleq(RZ, RZ, _start + 2 * INST_WIDTH),
        subleq(RZ, T1, _start + 3 * INST_WIDTH),
        subleq(T0, RZ, _start + 4 * INST_WIDTH),
        subleq(RZ, RZ, _start + 5 * INST_WIDTH),
    # LOOP:
        # if T2 == 0, goto EXIT.
        subleq(T2, RZ, _start + 15 * INST_WIDTH),
        # T2 = T2 - 1
        subleq(T2, CONST_POW[0], _start +  7 * INST_WIDTH),
        # T0 = T0 + T0
        subleq(RZ, T0, _start + 8 * INST_WIDTH),
        subleq(T0, RZ, _start + 9 * INST_WIDTH),
        # goto LOOP.
        subleq(RZ, RZ, _start + 6 * INST_WIDTH),
    # EXIT:
        subleq(RZ, RZ, _start + 15 * INST_WIDTH),
        subleq(RZ, RZ, _start + 15 * INST_WIDTH),
        subleq(RZ, RZ, _start + 15 * INST_WIDTH),
        subleq(RZ, RZ, _start + 15 * INST_WIDTH),
        subleq(RZ, RZ, _start + 15 * INST_WIDTH),
        subleq(RZ, RZ, _start)
    ]
    
def _srl():
    """ srl rd,rs1,rs2

    Initial state:
        T1: (rs1)
        T2: (rs2)
    Pseudocode:
        T0 = 0
        while T2 > 0:
            mask = 1 << 31
            half = 1 << 30
            T3 = T1
            T2 = T2 - 1
            while mask > 1:
                if T3 < mask, goto L0.
                T3 = T3 - mask
                T0 = T0 + half
            L0:
                mask = mask >> 1
                half = half >> 1
    Final state:
        T0: (rs1) >> (rs2)

    Returns:
        list: target instruction sequence
    """
    _start = SRL_START | PRC_MASK
    return [
        # T0 = T1
        subleq(T0, T0, _start + 1 * INST_WIDTH),
        subleq(RZ, RZ, _start + 2 * INST_WIDTH),
        subleq(RZ, T1, _start + 3 * INST_WIDTH),
        subleq(T0, RZ, _start + 4 * INST_WIDTH),
        # if T2 == 0, goto EXIT.
        subleq(RZ, RZ, _start + 5 * INST_WIDTH),
        subleq(T2, RZ, _start + 47 * INST_WIDTH),
        subleq(T0, T0, _start + 7 * INST_WIDTH),
        # while T2 > 0:
        subleq(RZ, RZ, _start + 8 * INST_WIDTH),
        subleq(T2, RZ, _start + 47 * INST_WIDTH),
        # T4 = T1
        subleq(T4, T4, _start + 10 * INST_WIDTH),
        subleq(RZ, T1, _start + 11 * INST_WIDTH),
        subleq(T4, RZ, _start + 12 * INST_WIDTH),
        # T5 = 2^31
        subleq(RZ, RZ, _start + 13 * INST_WIDTH),
        subleq(T5, T5, _start + 14 * INST_WIDTH),
        subleq(RZ, CONST_POW[31], _start + 15 * INST_WIDTH),
        subleq(T5, RZ, _start + 16 * INST_WIDTH),
        # T6 = 2^31-1
        subleq(RZ, RZ, _start + 17 * INST_WIDTH),
        subleq(T6, T6, _start + 18 * INST_WIDTH),
        subleq(RZ, CONST_ONE[31], _start + 19 * INST_WIDTH),
        subleq(T6, RZ, _start + 20 * INST_WIDTH),
        # T7 = 2^30
        subleq(RZ, RZ, _start + 21 * INST_WIDTH),
        subleq(T7, T7, _start + 22 * INST_WIDTH),
        subleq(RZ, CONST_POW[30], _start + 23 * INST_WIDTH),
        subleq(T7, RZ, _start + 24 * INST_WIDTH),
        # while T7 > 0: (assuming mask = T5)
        subleq(RZ, RZ, _start + 25 * INST_WIDTH),
        subleq(T7, RZ, _start + 38 * INST_WIDTH),
        # T3 = T4
        subleq(T3, T3, _start + 27 * INST_WIDTH),
        subleq(RZ, T4, _start + 28 * INST_WIDTH),
        subleq(T3, RZ, _start + 29 * INST_WIDTH),
        # if T3 < mask, goto L0.
        subleq(T3, T6, _start + 34 * INST_WIDTH),
        # T4 = T4 - mask
        subleq(T4, T5, _start + 31 * INST_WIDTH),
        # T0 = T0 + T7
        subleq(RZ, RZ, _start + 32 * INST_WIDTH),
        subleq(RZ, T7, _start + 33 * INST_WIDTH),
        subleq(T0, RZ, _start + 34 * INST_WIDTH),
    # L0:
        # mask = mask >> 1
        subleq(_start + 14 * INST_WIDTH + WORD_WIDTH, CONST_POW[2],  _start + 35 * INST_WIDTH),
        subleq(_start + 18 * INST_WIDTH + WORD_WIDTH, CONST_POW[2],  _start + 36 * INST_WIDTH),
        subleq(_start + 22 * INST_WIDTH + WORD_WIDTH, CONST_POW[2],  _start + 37 * INST_WIDTH),
        subleq(RZ, RZ, _start + 24 * INST_WIDTH),
        # T2 = T2 - 1
        subleq(T2, CONST_POW[0], _start + 39 * INST_WIDTH),
        subleq(RZ, RZ, _start + 7 * INST_WIDTH),
    # EXIT:
        subleq(RZ, RZ, _start + 47 * INST_WIDTH),
        subleq(RZ, RZ, _start + 47 * INST_WIDTH),
        subleq(RZ, RZ, _start + 47 * INST_WIDTH),
        subleq(RZ, RZ, _start + 47 * INST_WIDTH),
        subleq(RZ, RZ, _start + 47 * INST_WIDTH),
        subleq(RZ, RZ, _start + 47 * INST_WIDTH),
        subleq(RZ, RZ, _start + 47 * INST_WIDTH),
        subleq(RZ, RZ, _start)
    ]
    
def _sra():
    """ sra rd,rs1,rs2

    Initial state:
        T1: (rs1)
        T2: (rs2)
    Pseudocode:
        T0 = 0
        while T2 > 0:
            mask = 1 << 31
            half = 1 << 30
            T3 = T1
            T2 = T2 - 1
            while mask > 1:
                if T3 < mask, goto L0.
                T3 = T3 - mask
                T0 = T0 + half
                if T0 < 2^30, goto L0.
                T0 = T0 + 2^31
            L0:
                mask = mask >> 1
                half = half >> 1
    Final state:
        T0: (rs1) >>> (rs2)

    Returns:
        list: target instruction sequence
    """
    _start = SRA_START | PRC_MASK
    return [
        # T0 = T1
        subleq(T0, T0, _start + 1 * INST_WIDTH),
        subleq(RZ, RZ, _start + 2 * INST_WIDTH),
        subleq(RZ, T1, _start + 3 * INST_WIDTH),
        subleq(T0, RZ, _start + 4 * INST_WIDTH),
        # if T2 == 0, goto EXIT.
        subleq(RZ, RZ, _start + 5 * INST_WIDTH),
        subleq(T2, RZ, _start + 47 * INST_WIDTH),
        subleq(T0, T0, _start + 7 * INST_WIDTH),
        # while T2 > 0:
        subleq(RZ, RZ, _start + 8 * INST_WIDTH),
        subleq(T2, RZ, _start + 47 * INST_WIDTH),
        # T4 = T1
        subleq(T4, T4, _start + 10 * INST_WIDTH),
        subleq(RZ, T1, _start + 11 * INST_WIDTH),
        subleq(T4, RZ, _start + 12 * INST_WIDTH),
        # T5 = 2^31
        subleq(RZ, RZ, _start + 13 * INST_WIDTH),
        subleq(T5, T5, _start + 14 * INST_WIDTH),
        subleq(RZ, CONST_POW[31], _start + 15 * INST_WIDTH),
        subleq(T5, RZ, _start + 16 * INST_WIDTH),
        # T6 = 2^31-1
        subleq(RZ, RZ, _start + 17 * INST_WIDTH),
        subleq(T6, T6, _start + 18 * INST_WIDTH),
        subleq(RZ, CONST_ONE[31], _start + 19 * INST_WIDTH),
        subleq(T6, RZ, _start + 20 * INST_WIDTH),
        # T7 = 2^30
        subleq(RZ, RZ, _start + 21 * INST_WIDTH),
        subleq(T7, T7, _start + 22 * INST_WIDTH),
        subleq(RZ, CONST_POW[30], _start + 23 * INST_WIDTH),
        subleq(T7, RZ, _start + 24 * INST_WIDTH),
        # while T7 > 0: (assuming mask = T5)
        subleq(RZ, RZ, _start + 25 * INST_WIDTH),
        subleq(T7, RZ, _start + 38 * INST_WIDTH),
        # T3 = T4
        subleq(T3, T3, _start + 27 * INST_WIDTH),
        subleq(RZ, T4, _start + 28 * INST_WIDTH),
        subleq(T3, RZ, _start + 29 * INST_WIDTH),
        # if T3 < mask, goto L0.
        subleq(T3, T6, _start + 34 * INST_WIDTH),
        # T4 = T4 - mask
        subleq(T4, T5, _start + 31 * INST_WIDTH),
        # T0 = T0 + T7
        subleq(RZ, RZ, _start + 32 * INST_WIDTH),
        subleq(RZ, T7, _start + 33 * INST_WIDTH),
        subleq(T0, RZ, _start + 34 * INST_WIDTH),
    # L0:
        # mask = mask >> 1
        subleq(_start + 14 * INST_WIDTH + WORD_WIDTH, CONST_POW[2], _start + 35 * INST_WIDTH),
        subleq(_start + 18 * INST_WIDTH + WORD_WIDTH, CONST_POW[2], _start + 36 * INST_WIDTH),
        subleq(_start + 22 * INST_WIDTH + WORD_WIDTH, CONST_POW[2], _start + 37 * INST_WIDTH),
        subleq(RZ, RZ, _start + 25 * INST_WIDTH),
        # T2 = T2 - 1
        subleq(T2, CONST_POW[0], _start + 39 * INST_WIDTH),
        # T0 = T0 + 2^31 if T0 - 2^30 > 0
        subleq(T3, T3, _start + 40 * INST_WIDTH),
        subleq(RZ, T0, _start + 41 * INST_WIDTH),
        subleq(T3, RZ, _start + 42 * INST_WIDTH),
        subleq(T3, CONST_ONE[30], _start + 7 * INST_WIDTH),
        subleq(RZ, RZ, _start + 44 * INST_WIDTH),
        subleq(RZ, CONST_POW[31], _start + 45 * INST_WIDTH),
        subleq(T0, RZ, _start + 46 * INST_WIDTH),
        subleq(RZ, RZ, _start + 7 * INST_WIDTH),
    # EXIT:
        subleq(RZ, RZ, _start)
    ]

def _beq():
    """ beq rs1,rs2,offset

    Initial state:
        T1: (rs1)
        T2: (rs2)
    Final state:
        if rs1 == rs2, pc += offset.

    Returns:
        list: target instruction sequence
    """
    _start = BEQ_START | PRC_MASK
    return [
        subleq(T0, T0, _start + 1 * INST_WIDTH),
        subleq(RZ, RZ, _start + 2 * INST_WIDTH),
        subleq(RZ, T1, _start + 3 * INST_WIDTH),
        subleq(T0, RZ, _start + 4 * INST_WIDTH),
        subleq(T0, T2, _start + 5 * INST_WIDTH),
        subleq(RZ, RZ, _start + 6 * INST_WIDTH),
        subleq(T0, RZ, _start),
        subleq(RZ, RZ, _start)
    ]

def _blt():
    """ blt rs1,rs2,offset

    Initial state:
        T1: (rs1)
        T2: (rs2)
    Final state:
        if signed(rs1) < signed(rs2), pc += offset.

    Returns:
        list: target instruction sequence
    """
    _start = BLT_START | PRC_MASK
    return [
        subleq(T0, T0, _start + 1 * INST_WIDTH),
        subleq(RZ, RZ, _start + 2 * INST_WIDTH),
        subleq(RZ, RZ, _start + 3 * INST_WIDTH),
        subleq(RZ, T2, _start + 4 * INST_WIDTH),
        subleq(T0, RZ, _start + 5 * INST_WIDTH),
        subleq(T0, T1, _start + 7 * INST_WIDTH),
        subleq(RZ, RZ, _start),
        subleq(RZ, RZ, _start)
    ]
    
def _bltu():
    """ bltu rs1,rs2,offset

    Initial state:
        T1: (rs1)
        T2: (rs2)
    Final state:
        if unsigned(rs1) < unsigned(rs2), pc += offset.

    Returns:
        list: target instruction sequence
    """
    _start = BLTU_START | PRC_MASK
    return [
        # T0 = 0
        subleq(T0, T0, _start + 1 * INST_WIDTH),
        # T3 = T1
        subleq(RZ, RZ, _start + 2 * INST_WIDTH),
        subleq(T3, T3, _start + 3 * INST_WIDTH),
        subleq(RZ, T1, _start + 4 * INST_WIDTH),
        subleq(T3, RZ, _start + 5 * INST_WIDTH),
        # if T1 <= T2, goto L0.
        subleq(T3, T2, _start + 10 * INST_WIDTH),
        # if T2 >= 0, goto EXIT.
        subleq(RZ, RZ, _start + 7 * INST_WIDTH),
        subleq(RZ, T2, _start + 23 * INST_WIDTH),
        # if T1 <= 0, goto EXIT
        subleq(RZ, RZ, _start + 9 * INST_WIDTH),
        subleq(T3, RZ, _start + 23 * INST_WIDTH),
        # goto BRANCH.
        subleq(RZ, RZ, _start + 22 * INST_WIDTH),
    # L0:
        # if T1 == T2, goto EXIT
        subleq(RZ, RZ, _start + 12 * INST_WIDTH),
        subleq(T3, RZ, _start + 23 * INST_WIDTH),
    # L1:
        # if T1 >= 0, goto BRANCH.
        subleq(RZ, RZ, _start + 14 * INST_WIDTH),
        subleq(RZ, T1, _start + 22 * INST_WIDTH),
        # if T2 <= 0, goto BRANCH.
        subleq(RZ, RZ, _start + 16 * INST_WIDTH),
        subleq(T2, RZ, _start + 22 * INST_WIDTH),
        # goto EXIT.
        subleq(RZ, RZ, _start + 23 * INST_WIDTH),
        subleq(RZ, RZ, _start + 23 * INST_WIDTH),
        subleq(RZ, RZ, _start + 23 * INST_WIDTH),
        subleq(RZ, RZ, _start + 23 * INST_WIDTH),
        subleq(RZ, RZ, _start + 23 * INST_WIDTH),
    # BRANCH:
        subleq(RZ, RZ, _start),
    # EXIT:
        subleq(RZ, RZ, _start)
    ]

def _lw():
    """ lw rd,offset(rs1)

    Initial state:
        T1: (rs1)
        T2: (offset)
    Final state:
        T0: MEM[(rs1)+offset]

    Returns:
        list: target instruction sequence
    """
    
    _start = LW_START | PRC_MASK
    return [
        subleq(T0, T0, _start + 1 * INST_WIDTH),
        subleq(RZ, RZ, _start + 2 * INST_WIDTH),
        subleq(RZ, T1, _start + 3 * INST_WIDTH),
        subleq(_start + 9 * INST_WIDTH + WORD_WIDTH, RZ, _start + 4 * INST_WIDTH),
        subleq(RZ, RZ, _start + 5 * INST_WIDTH),
        subleq(RZ, T2, _start + 6 * INST_WIDTH),
        subleq(_start + 9 * INST_WIDTH + WORD_WIDTH, RZ, _start + 7 * INST_WIDTH),
        subleq(RZ, RZ, _start + 8 * INST_WIDTH),
        subleq(RZ, 0,  _start + 9 * INST_WIDTH),
        subleq(T0, RZ, _start + 15 * INST_WIDTH),
        subleq(RZ, RZ, _start + 15 * INST_WIDTH),
        subleq(RZ, RZ, _start + 15 * INST_WIDTH),
        subleq(RZ, RZ, _start + 15 * INST_WIDTH),
        subleq(RZ, RZ, _start + 15 * INST_WIDTH),
        subleq(RZ, RZ, _start + 15 * INST_WIDTH),
        subleq(RZ, RZ, _start)
    ]

def _sw():
    """ sw rs2,offset(rs1)

    Initial state:
        T1: (rs1)
        T2: (rs2)
        T3: offset
    Final state:
        MEM[(rs1)+offset] = (rs2)

    Returns:
        list: target instruction sequence
    """
    
    _start = SW_START | PRC_MASK
    return [
        subleq(T0, T0, _start + 1 * INST_WIDTH),
        subleq(RZ, RZ, _start + 2 * INST_WIDTH),
        subleq(RZ, T1, _start + 3 * INST_WIDTH),
        subleq(_start + 9 * INST_WIDTH, RZ, _start + 4 * INST_WIDTH),
        subleq(RZ, RZ, _start + 5 * INST_WIDTH),
        subleq(RZ, T3, _start + 6 * INST_WIDTH),
        subleq(_start + 9 * INST_WIDTH, RZ, _start + 7 * INST_WIDTH),
        subleq(RZ, RZ, _start + 8 * INST_WIDTH),
        subleq(RZ, T2, _start + 9 * INST_WIDTH),
        subleq(0,  RZ, _start + 15 * INST_WIDTH),
        subleq(RZ, RZ, _start + 15 * INST_WIDTH),
        subleq(RZ, RZ, _start + 15 * INST_WIDTH),
        subleq(RZ, RZ, _start + 15 * INST_WIDTH),
        subleq(RZ, RZ, _start + 15 * INST_WIDTH),
        subleq(RZ, RZ, _start + 15 * INST_WIDTH),
        subleq(RZ, RZ, _start)
    ]

class rv_translator:
    def __init__(self):
        pass