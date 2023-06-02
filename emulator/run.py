import argparse

class emu:
    def __init__(self, size=1024):
        self.pc = 0
        self.memo = bytearray([0]*size)
        self.csr_space = [0]*4096
        self.gpr_space = [0]*32
        self.temporary_variable = [0]*32
        self.constant_value = [0x00000001 << x for x in range(0, 32)] + [0xffffffff >> x for x in range(1, 33)][::-1]
    
    def mmio_rd(self, addr:int):
        if      addr >= 0xffff8000 and addr < 0xffffc000:
            return self.csr_space[(addr&0x3fff)>>2]
        elif    addr >= 0xffffc000 and addr < 0xffffc080:
            return self.gpr_space[(addr&0x007f)>>2]
        elif    addr >= 0xffffc080 and addr < 0xffffc100:
            return self.temporary_variable[((addr-0x80)&0x007f)>>2]
        elif    addr >= 0xffffc100 and addr < 0xffffc200:
            return self.constant_value[(addr&0x00ff)>>2]
        elif    addr < 0x00000400:
            return int.from_bytes(self.memo[addr:addr+4], byteorder="little")
        
    def mmio_wr(self, addr:int, data:int):
        if      addr >= 0xffff8000 and addr < 0xffffc000:
            self.csr_space[(addr&0x3fff)>>2] = data
        elif    addr >= 0xffffc000 and addr < 0xffffc080:
            self.gpr_space[(addr&0x007f)>>2] = data
        elif    addr >= 0xffffc080 and addr < 0xffffc100:
            self.temporary_variable[((addr-0x80)&0x007f)>>2] = data
        elif    addr >= 0xffffc100 and addr < 0xffffc200:
            self.constant_value[(addr&0x00ff)>>2] = data
        elif    addr < 0x00000400:
            self.memo[addr:addr+4] = int.to_bytes(data, 4, byteorder="little")
    
    def poke(self, addr, byte):
        self.memo[addr] = byte
    
    def peek(self, addr):
        return self.memo[addr]
    
    def step(self):
        a = self.mmio_rd(self.pc)
        b = self.mmio_rd(self.pc + 4)
        c = self.mmio_rd(self.pc + 8)
        a = self.mmio_rd(a)
        b = self.mmio_rd(b)
        r = a - b
        self.mmio_wr(self.pc, r)
        if r <= 0:
            self.pc = c
        else:
            self.pc = self.pc + 12

if __name__ == "__main__":
    e = emu()
    