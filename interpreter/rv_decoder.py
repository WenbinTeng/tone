class rv_decoder:
    def __init__(self, inst:int):
        self.opcode =  inst        & 0x7f
        self.funct3 = (inst >> 12) & 0x07
        self.funct7 = (inst >> 25) & 0x7f 
        self.rd     = (inst >>  7) & 0x1f
        self.rs1    = (inst >> 15) & 0x1f
        self.rs2    = (inst >> 20) & 0x1f
        self.b_imm  = (0xffffe000 if self.funct7 & 0x40 else 0x00) + (self.funct7 & 0x3f << 5) + (self.rd & 0x1e) + (self.rd & 0x1 << 11)
        self.s_imm  = (0xffffe000 if self.funct7 & 0x40 else 0x00) + (self.funct7 & 0x3f << 5) + (self.rd)
        self.i_imm  = (0xffffe000 if self.funct7 & 0x40 else 0x00) + (self.funct7 & 0x3f << 5) + (self.rs2)
        self.id     = self.opcode + self.funct3 << 7 + (self.funct7 << 10 if self.opcode == 0x33 or self.opcode == 0x13 and self.funct3 == 0x05 else 0x00)