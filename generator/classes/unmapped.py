class Unmapped():
    def __init__(self,paramSize,paramMemory,paramCoreId):
        self.size = paramSize
        self.memory = paramMemory
        self.coreId = paramCoreId
        self.lowAddress = None
        self.highAddress = None