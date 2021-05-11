class ScheduleTableElement:
    def __init__(self,paramCoreId,paramProgramId,paramTaskId,paramExecutionTick,paramElementId):
        self.elementId = paramElementId
        self.coreId = paramCoreId
        self.programId = paramProgramId
        self.taskId = paramTaskId
        self.executionTick = paramExecutionTick