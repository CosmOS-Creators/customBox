class Schedulable:
    def __init__(self,paramName,paramSchedulableId,paramFloatingPoint,paramCoreId,paramProgramId):
        self.schedulableId = paramSchedulableId
        self.name = paramName
        self.coreId = paramCoreId
        self.programId = paramProgramId
        self.floatingPoint = paramFloatingPoint