from stack import Stack
from schedulable import Schedulable

class Task(Stack):
    def __init__(self,paramName,paramWcet,paramPeriod,paramCoreId,paramProgramId,paramTaskId,paramStackId,paramStackSize,paramFloatingPoint,paramSchedulableId):
        Stack.__init__(self,paramStackId,paramStackSize)
        Schedulable.__init__(self,paramName,paramSchedulableId,paramFloatingPoint,paramCoreId,paramProgramId)
        self.wcet = paramWcet
        self.taskId = paramTaskId
        self.period = paramPeriod



