import argparse

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
    _start = int(0x00000000) | PRC_MASK
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
    _start = int(0x00000060) | PRC_MASK
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
    _start = int(0x00000c0) | PRC_MASK
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
    _start = int(0x00000240) | PRC_MASK
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
    _start = int(0x000003c0) | PRC_MASK
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
    _start = int(0x00000540) | PRC_MASK
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
    _start = int(0x000005a0) | PRC_MASK
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
            subleq(RZ, T2, _start + 31 * INST_WIDTH),
            # if T1 <= 0, goto EXIT
            subleq(RZ, RZ, _start + 9 * INST_WIDTH),
            subleq(T3, RZ, _start + 31 * INST_WIDTH),
            # goto L2.
            subleq(RZ, RZ, _start + 18 * INST_WIDTH),
        # L0:
            # if T1 == T2, goto EXIT
            subleq(RZ, RZ, _start + 12 * INST_WIDTH),
            subleq(T3, RZ, _start + 31 * INST_WIDTH),
        # L1:
            # if T1 >= 0, goto L2.
            subleq(RZ, RZ, _start + 14 * INST_WIDTH),
            subleq(RZ, T1, _start + 18 * INST_WIDTH),
            # if T2 <= 0, goto L2.
            subleq(RZ, RZ, _start + 16 * INST_WIDTH),
            subleq(T2, RZ, _start + 18 * INST_WIDTH),
            # goto EXIT.
            subleq(RZ, RZ, _start + 31 * INST_WIDTH),
        # L2:
            # T0 = 1
            subleq(RZ, RZ, _start + 19 * INST_WIDTH),
            subleq(RZ, CONST_POW[0], _start + 20 * INST_WIDTH),
            subleq(T0, RZ, _start + 21 * INST_WIDTH),
        # EXIT
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
    _start = int(0x000006c0) | PRC_MASK
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
    _start = int(0x00000780) | PRC_MASK
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
                subleq(_start + 11 * INST_WIDTH + WORD_WIDTH, CONST_POW[2],  _start + 35 * INST_WIDTH),
                subleq(_start + 15 * INST_WIDTH + WORD_WIDTH, CONST_POW[2],  _start + 36 * INST_WIDTH),
                subleq(_start + 19 * INST_WIDTH + WORD_WIDTH, CONST_POW[2],  _start + 37 * INST_WIDTH),
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
    _start = int(0x000009c0) | PRC_MASK
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
                subleq(_start + 11 * INST_WIDTH + WORD_WIDTH, CONST_POW[2], _start + 35 * INST_WIDTH),
                subleq(_start + 15 * INST_WIDTH + WORD_WIDTH, CONST_POW[2], _start + 36 * INST_WIDTH),
                subleq(_start + 19 * INST_WIDTH + WORD_WIDTH, CONST_POW[2], _start + 37 * INST_WIDTH),
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, help="select source binary file")
    parser.add_argument("-o", "--output", type=str, default="a.out", help="place target binary file")
    args = parser.parse_args()

    with open(args.file, "r") as f:
        inst = int.from_bytes(f.read(4), byteorder="little", signed=False)
    