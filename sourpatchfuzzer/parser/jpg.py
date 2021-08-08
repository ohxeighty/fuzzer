class Jpg:
    def __init__(self, raw):
        self.raw = raw
        self.size = 0
        self.positions = []
        self.headers = []
        self.lengths = []
        self.datas = [] # the plural is datoxen, the singular is datum
        i = 0
        jpg_magic = [b'\xd0', b'\xd1', b'\xd2', b'\xd3', b'\xd4', b'\xd5', b'\xd6', b'\xd7', b'\xd8', b'\xd9']
        while(i != -1):
            i = self.raw.find(b'\xff', i)
            if(i == -1):
                break
            if(self.raw[i+1] != 0):
                header = self.raw[i:i+2]
                section_length = b''
                section_info = b''
                if(self.raw[i+1:i+2] not in jpg_magic):
                    section_length = self.raw[i+2:i+4]
                    section_info = self.raw[i+4:i+int(section_length.hex(), 16)+2]
                self.positions.append(i)
                self.headers.append(self.raw[i:i+2])
                self.lengths.append(section_length)
                self.datas.append(section_info)
                self.size += 1
            i += 1
    def pack(self):
        packed = bytearray(self.raw)
        for i in range(self.size):
            packed[self.positions[i]:self.positions[i]+2] = self.headers[i]
            if(self.lengths[i]):
                packed[self.positions[i]+2:self.positions[i]+4] = self.lengths[i]
                sec_len = int(self.lengths[i].hex(), 16)
                if(positions[i]):
                    packed[self.positions[i]+4:self.positions[i]+sec_len+4] = self.datas[i]
        return bytes(packed)

