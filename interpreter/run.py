import argparse
from ctypes import c_int32
from rv_decoder import *
from rv_translator import *

def transform(l:list) -> list:
    pc = 0
    inst_list = list()
    addr_list = list() + [0]
    wait_dict = dict()
    code_dict = {
        0x0033: "add", 0x8033: "sub", 0x0133: "slt", 0x01b3: "sltu", 0x00b3: "sll", 0x02b3: "srl", 0x82b3: "sra", 0x0233: "xor", 0x0333: "or", 0x03b3: "and",
        0x0013: "addi", 0x0113: "slti", 0x0193: "sltiu", 0x0213: "xori", 0x0313: "ori", 0x0393: "andi", 0x0093: "slli", 0x0293: "srli", 0x8293: "srai",
        0x0063: "beq", 0x00e3: "bne", 0x0263: "blt", 0x02e3: "bge", 0x0363: "bltu", 0x03e3: "bgeu",
        0x0123: "sw", 0x0103: "lw",
        0x0037: "lui", 0x0017: "auipc",
        0x006f: "jal"
    }
    start_dict = {
        0x0033: ADD_START, 0x8033: SUB_START, 0x0133: SLT_START, 0x01b3: SLTU_START, 0x00b3: SLL_START, 0x02b3: SRL_START, 0x82b3: SRA_START, 0x0233: XOR_START, 0x0333: OR_START, 0x03b3: AND_START,
        0x0013: ADD_START, 0x0113: SLT_START, 0x0193: SLTU_START, 0x0213: XOR_START, 0x0313: OR_START, 0x0393: AND_START, 0x0093: SLL_START, 0x0293: SRL_START, 0x8293: SRA_START,
        0x0063: BEQ_START, 0x00e3: BEQ_START, 0x0263: BLT_START, 0x02e3: BLT_START, 0x0363: BLTU_START, 0x03e3: BLTU_START,
        0x0123: SW_START, 0x0103: LW_START
    }
    end_dict = {
        0x0033: ADD_END, 0x8033: SUB_END, 0x0133: SLT_END, 0x01b3: SLTU_END, 0x00b3: SLL_END, 0x02b3: SRL_END, 0x82b3: SRA_END, 0x0233: XOR_END, 0x0333: OR_END, 0x03b3: AND_END,
        0x0013: ADD_END, 0x0113: SLT_END, 0x0193: SLTU_END, 0x0213: XOR_END, 0x0313: OR_END, 0x0393: AND_END, 0x0093: SLL_END, 0x0293: SRL_END, 0x8293: SRA_END,
        0x0063: BEQ_END, 0x00e3: BEQ_END, 0x0263: BLT_END, 0x02e3: BLT_END, 0x0363: BLTU_END, 0x03e3: BLTU_END,
        0x0123: SW_END, 0x0103: LW_END
    }
    
    for key in start_dict:
        start_dict[key] = start_dict[key] | PRC_MASK
    for key in end_dict:
        end_dict[key] = end_dict[key] | PRC_MASK
    
    for i in l:
        
        # Initialize instruction decoder
        decoder = rv_decoder(i)
        
        # Update branch address
        if len(addr_list) in wait_dict:
            p = int(wait_dict[len(addr_list)]/INST_WIDTH)
            inst_list[p][1] = pc
            del wait_dict[len(addr_list)]
            
        print("pc=%d, inst=%s"%(pc,code_dict[decoder.id]))
        
        # Store parameters
        if code_dict[decoder.id] in {"add", "sub", "slt", "sltu", "sll", "srl", "sra", "xor", "or", "and", "beq", "bne", "blt", "bge", "bltu", "bgeu"}:
            inst_list = inst_list + [
                subleq(RZ, RZ, pc + 1 * INST_WIDTH),
                subleq(RZ, GPR_MASK + (decoder.rs1<<2), pc + 2 * INST_WIDTH),
                subleq(T1, T1, pc + 3 * INST_WIDTH),
                subleq(T1, RZ, pc + 4 * INST_WIDTH),
                subleq(RZ, RZ, pc + 5 * INST_WIDTH),
                subleq(RZ, GPR_MASK + (decoder.rs2<<2), pc + 6 * INST_WIDTH),
                subleq(T2, T2, pc + 7 * INST_WIDTH),
                subleq(T2, RZ, pc + 8 * INST_WIDTH)
            ]
            pc = pc + 8 * INST_WIDTH
        elif code_dict[decoder.id] in {"addi", "slti", "sltiu", "xori", "ori", "andi", "slli", "srli", "srai", "lw"}:
            inst_list = inst_list + [
                subleq(RZ, RZ, pc + 2 * INST_WIDTH),
                [decoder.i_imm, 0, 0],
                subleq(RZ, GPR_MASK + (decoder.rs1<<2), pc + 3 * INST_WIDTH),
                subleq(T1, T1, pc + 4 * INST_WIDTH),
                subleq(T1, RZ, pc + 5 * INST_WIDTH),
                subleq(RZ, RZ, pc + 6 * INST_WIDTH),
                subleq(RZ, pc + 1 * INST_WIDTH, pc + 7 * INST_WIDTH),
                subleq(T2, T2, pc + 8 * INST_WIDTH),
                subleq(T2, RZ, pc + 9 * INST_WIDTH)
            ]
            pc = pc + 9 * INST_WIDTH
        elif code_dict[decoder.id] == "sw":
            inst_list = inst_list + [
                subleq(RZ, RZ, pc + 2 * INST_WIDTH),
                [decoder.s_imm, 0, 0],
                subleq(RZ, GPR_MASK + (decoder.rs1<<2), pc + 3 * INST_WIDTH),
                subleq(T1, T1, pc + 4 * INST_WIDTH),
                subleq(T1, RZ, pc + 5 * INST_WIDTH),
                subleq(RZ, RZ, pc + 6 * INST_WIDTH),
                subleq(RZ, GPR_MASK + (decoder.rs2<<2), pc + 7 * INST_WIDTH),
                subleq(T2, T2, pc + 8 * INST_WIDTH),
                subleq(T2, RZ, pc + 9 * INST_WIDTH),
                subleq(RZ, RZ, pc + 10 * INST_WIDTH),
                subleq(RZ, pc + 1 * INST_WIDTH, pc + 11 * INST_WIDTH),
                subleq(T3, T3, pc + 12 * INST_WIDTH),
                subleq(T3, RZ, pc + 13 * INST_WIDTH)
            ]
            pc = pc + 13 * INST_WIDTH
        
        # Overwrite exit address then jump to entrance
        if code_dict[decoder.id] in {"add", "sub", "slt", "sltu", "sll", "srl", "sra", "xor", "or", "and", "addi", "slti", "sltiu", "xori", "ori", "andi", "slli", "srli", "srai", "lw", "sw"}:
            inst_list = inst_list + [
                subleq(RZ, RZ, pc + 2 * INST_WIDTH),
                [pc + 6 * INST_WIDTH, 0, 0],                                                                    # mark the address after calling micro-procedure manually.
                subleq(RZ, pc + 1 * INST_WIDTH, pc + 3 * INST_WIDTH),                                           # store the address negative value temporary.
                subleq(end_dict[decoder.id], end_dict[decoder.id], pc + 4 * INST_WIDTH),                        # clear the destination
                subleq(end_dict[decoder.id], RZ, pc + 5 * INST_WIDTH),                                          # overwrite the return address to the exit of the micro-procedure.
                subleq(RZ, RZ, start_dict[decoder.id])                                                          # calling micro-procedure.
            ]
            pc = pc + 6 * INST_WIDTH
        elif code_dict[decoder.id] in {"beq", "blt", "bltu"}:                                                   # take judgement natively.
            inst_list = inst_list + [
                subleq(RZ, RZ, pc + 2 * INST_WIDTH),
                [pc + 10 * INST_WIDTH, 0, 0],                                                                   # 1st word stores return address, 2nd word stores branch address.
                subleq(RZ, pc + 1 * INST_WIDTH, pc + 3 * INST_WIDTH),                                           # store the address negative value temporary.
                subleq(end_dict[decoder.id], end_dict[decoder.id], pc + 4 * INST_WIDTH),                        # clear the destination
                subleq(end_dict[decoder.id], RZ, pc + 5 * INST_WIDTH),                                          # overwrite the return address (if branch NOT taken) to the exit of the micro-procedure.
                subleq(RZ, RZ, pc + 6 * INST_WIDTH),
                subleq(RZ, pc + 1 * INST_WIDTH + WORD_WIDTH, pc + 7 * INST_WIDTH),                              # store the address negative value temporary.
                subleq(end_dict[decoder.id]-INST_WIDTH, end_dict[decoder.id]-INST_WIDTH, pc + 8 * INST_WIDTH),  # clear the destination
                subleq(end_dict[decoder.id]-INST_WIDTH, RZ, pc + 9 * INST_WIDTH),                               # overwrite the return address (if branch taken) to the exit of the micro-procedure.
                subleq(RZ, RZ, start_dict[decoder.id])                                                          # calling micro-procedure.
            ]
            if decoder.b_imm < 0x80000000:
                wait_dict[len(addr_list)+(decoder.b_imm>>2)] = pc + INST_WIDTH                                  # if jump after, join the wait list, and overwrite target address later.
            else:
                inst_list[int(pc/INST_WIDTH)+1][1] = addr_list[(c_int32(decoder.b_imm).value>>2)-1]             # if jump before, store the target address.
            pc = pc + 10 * INST_WIDTH
        elif code_dict[decoder.id] in {"bne", "bge", "bgeu"}:                                                   # take judgement opposite to beq/blt/bltu.
            inst_list = inst_list + [
                subleq(RZ, RZ, pc + 2 * INST_WIDTH),
                [pc + 10 * INST_WIDTH, 0, 0],                                                                   # 1st word stores return address, 2nd word stores branch address.
                subleq(RZ, pc + 1 * INST_WIDTH, pc + 3 * INST_WIDTH),                                           # store the address negative value temporary.
                subleq(end_dict[decoder.id]-INST_WIDTH, end_dict[decoder.id]-INST_WIDTH, pc + 4 * INST_WIDTH),  # clear the destination
                subleq(end_dict[decoder.id]-INST_WIDTH, RZ, pc + 5 * INST_WIDTH),                               # overwrite the return address (if branch NOT taken) to the exit of the micro-procedure.
                subleq(RZ, RZ, pc + 6 * INST_WIDTH),
                subleq(RZ, pc + 1 * INST_WIDTH + WORD_WIDTH, pc + 7 * INST_WIDTH),                              # store the address negative value temporary.
                subleq(end_dict[decoder.id], end_dict[decoder.id], pc + 8 * INST_WIDTH),                        # clear the destination
                subleq(end_dict[decoder.id], RZ, pc + 9 * INST_WIDTH),                                          # overwrite the return address (if branch taken) to the exit of the micro-procedure.
                subleq(RZ, RZ, start_dict[decoder.id])                                                          # calling micro-procedure.
            ]
            if decoder.b_imm < 0x80000000:
                wait_dict[len(addr_list)+(decoder.b_imm>>2)] = pc + INST_WIDTH                                  # if jump after, join the wait list, and overwrite target address later.
            else:
                inst_list[int(pc/INST_WIDTH)+1][1] = addr_list[(c_int32(decoder.b_imm).value>>2)-1]             # if jump before, store the target address.
            pc = pc + 10 * INST_WIDTH
        
        # Load Result
        if code_dict[decoder.id] in {"add", "sub", "slt", "sltu", "sll", "srl", "sra", "xor", "or", "and", "addi", "slti", "sltiu", "xori", "ori", "andi", "slli", "srli", "srai", "lw"}:
            inst_list = inst_list + [
                subleq(RZ, RZ, pc + 1 * INST_WIDTH),
                subleq(RZ, T0, pc + 2 * INST_WIDTH),
                subleq(GPR_MASK + (decoder.rd<<2), GPR_MASK + (decoder.rd<<2), pc + 3 * INST_WIDTH),
                subleq(GPR_MASK + (decoder.rd<<2), RZ, pc + 4 * INST_WIDTH)
            ]
            pc = pc + 4 * INST_WIDTH
        
        # This instruction need not to call micro-procedure
        if code_dict[decoder.id] == "lui":
            inst_list = inst_list + [
                subleq(RZ, RZ, pc + 2 * INST_WIDTH),
                [decoder.u_imm, 0, 0],
                subleq(RZ, pc + 1 * INST_WIDTH, pc + 3 * INST_WIDTH),
                subleq(GPR_MASK + (decoder.rd<<2), GPR_MASK + (decoder.rd<<2), pc + 4 * INST_WIDTH),
                subleq(GPR_MASK + (decoder.rd<<2), RZ, pc + 5 * INST_WIDTH)
            ]
            pc = pc + 5 * INST_WIDTH
        elif code_dict[decoder.id] == "auipc":
            inst_list = inst_list + [
                subleq(RZ, RZ, pc + 2 * INST_WIDTH),
                [0, 0, 0],
                subleq(RZ, pc + 1 * INST_WIDTH + WORD_WIDTH, pc + 3 * INST_WIDTH),
                subleq(pc + 4 * INST_WIDTH + 2 * WORD_WIDTH, RZ, pc + 4 * INST_WIDTH),
                subleq(RZ, RZ, 0)
            ]
            if decoder.u_imm < 0x80000000:
                wait_dict[len(addr_list)+(decoder.u_imm>>2)] = pc + INST_WIDTH
            else:
                inst_list[int(pc/INST_WIDTH)+1][1] = addr_list[(c_int32(decoder.u_imm).value>>2)-1]
            pc = pc + 5 * INST_WIDTH
        elif code_dict[decoder.id] == "jal":
            inst_list = inst_list + [
                subleq(RZ, RZ, pc + 2 * INST_WIDTH),
                [0, 0, 0],
                subleq(RZ, pc + 1 * INST_WIDTH + WORD_WIDTH, pc + 3 * INST_WIDTH),
                subleq(pc + 5 * INST_WIDTH + 2 * WORD_WIDTH, pc + 5 * INST_WIDTH + 2 * WORD_WIDTH, pc + 4 * INST_WIDTH),
                subleq(pc + 5 * INST_WIDTH + 2 * WORD_WIDTH, RZ, pc + 5 * INST_WIDTH),
                subleq(RZ, RZ, 0)
            ]
            if decoder.j_imm < 0x80000000:
                wait_dict[len(addr_list)+(decoder.j_imm>>2)] = pc + INST_WIDTH
            else:
                inst_list[int(pc/INST_WIDTH)+1][1] = addr_list[(c_int32(decoder.j_imm).value>>2)-1]
            pc = pc + 6 * INST_WIDTH
        
        # Record instruction address
        addr_list.append(pc)
        
    return inst_list

if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("file", type=str, help="select source binary file")
    # parser.add_argument("-o", "--output", type=str, default="a.out", help="place target binary file")
    # args = parser.parse_args()
    
    in_file = "./demo/final.bin"
    out_file = "./demo/fpga.txt"
    
    origin_inst = []
    target_inst = []

    with open(in_file, "rb") as f:
        while True:
            inst = f.read(4)
            if inst:
                origin_inst.append(int.from_bytes(bytes(inst), byteorder="little", signed=False))
            else:
                break
    
    target_inst = transform(origin_inst)
    
    with open(out_file, "w") as f:
        for inst in target_inst:
            for word in inst:
                f.write(word.to_bytes(4, byteorder="little").hex() + '\n')

    from rv_translator import _add, _sub, _and, _or, _xor, _slt, _sltu, _sll, _srl, _sra, _beq, _blt, _bltu, _lw, _sw
    micro_proc = [] + _add() + _sub() + _and() + _or() + _xor() + _slt() + _sltu() + _sll() + _srl() + _sra() + _beq() + _blt() + _bltu() + _lw() + _sw()
    
    with open("./demo/micro-procedure.txt", "w") as f:
        for inst in micro_proc:
            for word in inst:
                f.write(word.to_bytes(4, byteorder="little").hex() + '\n')
