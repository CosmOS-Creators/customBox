class Stack:
    def __init__(self,paramStackId,paramStackSize):
        self.stackId = paramStackId
        self.stackSize = paramStackSize
        self.highAddress = None
        self.lowAddress = None