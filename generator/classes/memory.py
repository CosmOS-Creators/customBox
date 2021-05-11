class Memory():
    def __init__(self,paramName,paramSize,paramLowAddress,paramCores,paramFreeChunks):
        self.name = paramName
        self.size = paramSize
        self.lowAddress = paramLowAddress
        self.freeChunks = paramFreeChunks
        self.cores = paramCores