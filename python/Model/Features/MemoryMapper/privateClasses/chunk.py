class Chunk():
    def __init__(self,paramLowAddress,paramHighAddress,paramSize):
        self.highAddress = paramHighAddress
        self.lowAddress = paramLowAddress
        self.size = paramHighAddress - paramLowAddress