class SysJobGroup():
    def __init__(self,paramGroupId,paramCoreId,paramHandlers,paramTickMultiplicator,paramApiHeaders):
        self.groupId = paramGroupId
        self.coreId = paramCoreId
        self.handlers = paramHandlers
        self.tickMultiplicator = paramTickMultiplicator
        self.apiHeaders = paramApiHeaders