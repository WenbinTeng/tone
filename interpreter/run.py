import argparse

WORD_WIDTH = 4

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

RZ  = int(0xffffc100)
C1  = int(0xffffc104)
C2  = int(0xffffc108)
C4  = int(0xffffc10c) 
C8  = int(0xffffc110)
C16 = int(0xffffc114)
C32 = int(0xffffc118)
C64 = int(0xffffc11c)

def subleq(a, b, c):
    return [a, b, c]

def _add():
    """ add rd,rs1,rs2
        
    Initial state:
        T1: (rs1)
        T2: (rs2)
    Pseudocode:
        T0 <= 0
        T0 <= T0 - (0 - T1)
        T0 <= T0 - (0 - T2)
    Final state:
        T0: (rs1) + (rs2)
    
    Returns:
        list: target instruction sequence
    """
    _start = int(0x00000000) | PRC_MASK
    return [] + \
        subleq(T0, T0, _start + 1 * WORD_WIDTH) + \
        subleq(RZ, RZ, _start + 2 * WORD_WIDTH) + \
        subleq(RZ, T1, _start + 3 * WORD_WIDTH) + \
        subleq(T0, RZ, _start + 4 * WORD_WIDTH) + \
        subleq(RZ, RZ, _start + 5 * WORD_WIDTH) + \
        subleq(RZ, T2, _start + 6 * WORD_WIDTH) + \
        subleq(T0, RZ, _start + 7 * WORD_WIDTH) + \
        subleq(RZ, RZ, _start)

def _sub():
    """ sub rd,rs1,rs2

    Initial state:
        T1: (rs1)
        T2: (rs2)
    Pseudocode:
        T0 <= 0
        T0 <= T0 - (0 - T1)
        T0 <= T0 - T2
    Final state:
        T0: (rs1) - (rs2)

    Returns:
        list: target instruction sequence
    """
    _start = int(0x00000020) | PRC_MASK
    return [] + \
        subleq(T0, T0, _start + 1 * WORD_WIDTH) + \
        subleq(RZ, RZ, _start + 2 * WORD_WIDTH) + \
        subleq(RZ, T1, _start + 3 * WORD_WIDTH) + \
        subleq(T0, RZ, _start + 4 * WORD_WIDTH) + \
        subleq(T0, T2, _start + 5 * WORD_WIDTH) + \
        subleq(RZ, RZ, _start)                  + \
        subleq(RZ, RZ, _start)                  + \
        subleq(RZ, RZ, _start)
    
def _sll(rd, rs1, rs2, line):
    pass  
    
def _srl(rd, rs1, rs2, line):
    pass
    
def _sra(rd, rs1, rs2, line):
    pass

def _xor(rd, rs1, rs2, line):
    pass

def _or(rd, rs1, rs2, line):
    pass

def _and(rd, rs1, rs2, line):
    pass

def _slt(rd, rs1, rs2, line):
    pass
        
def _sltu(rd, rs1, rs2, line):
    pass
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, help="select source binary file")
    parser.add_argument("-o", "--output", type=str, default="a.out", help="place target binary file")
    args = parser.parse_args()

    with open(args.file, "r") as f:
        inst = int.from_bytes(f.read(4), byteorder="little", signed=False)
    