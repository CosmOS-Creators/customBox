from stack import Stack
from schedulable import Schedulable

class Thread(Stack):
    def __init__(self,paramName,paramCoreId,paramProgramId,paramThreadId,paramStackId,paramStackSize,paramFloatingPoint,paramSchedulableId,paramIsIdle,paramIsSysJob):
        Stack.__init__(self,paramStackId,paramStackSize)
        Schedulable.__init__(self,paramName,paramSchedulableId,paramFloatingPoint,paramCoreId,paramProgramId,paramIsIdle,paramIsSysJob)
        self.name = paramName
        self.threadId = paramThreadId