def u32(num):
    return int.from_bytes(int(num.hex(), 16).to_bytes(4, byteorder='little'), byteorder='big')

def u64(num):
    return int.from_bytes(int(num.hex(), 16).to_bytes(8, byteorder='little'), byteorder='big')

def p32(num):
    return int.from_bytes(int(num.hex(), 16).to_bytes(4, byteorder='little'), byteorder='big')

def p64(num):
    return int.from_bytes(int(num.hex(), 16).to_bytes(8, byteorder='little'), byteorder='big')

class Elf:
    def __init__(self, raw):
        self.raw = raw
        self.bits = raw[4] * 32
        self.endianness = raw[5]
        if(self.bits == 32):
            self.elfheader = raw[0:52]
            progheaderstart
            self.progheader = [progheaderstart:progheaderstart+32]
        if(self.bits == 64):
            self.elfheader = raw[0:64]
            progheaderstart
            self.progheader = [progheaderstart:progheaderstart+56]
        else:
            return

