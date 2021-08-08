class Pdf:
    def __init__(self, raw):
        self.raw = raw
        self.ver = float(raw[5:8])