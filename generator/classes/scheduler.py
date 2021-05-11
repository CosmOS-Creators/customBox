class Scheduler:
    def __init__(self,paramHyperTick,paramTable,paramCoreId,paramNumOfElementsInTable,paramSyncTicks,paramFirstSyncTaskStartTick,paramPreemptTick):
        self.hyperTick = paramHyperTick
        self.table = paramTable
        self.coreId = paramCoreId
        self.numOfElementsInTable = paramNumOfElementsInTable
        self.syncTicks = paramSyncTicks
        self.firstSyncTaskStartTick = paramFirstSyncTaskStartTick
        self.preemptTick = paramPreemptTick
        self.lastToFistTaskTicks = None