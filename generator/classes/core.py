class Core():
    def __init__(self,paramName,paramPrograms,paramCoreId,paramScheduler,paramUnmapped,paramBootOs,paramSysJobGroups):
        self.kernelStackSize = 1024
        self.name = paramName
        self.scheduler = paramScheduler
        self.programs = paramPrograms
        self.coreId = paramCoreId
        self.unmapped = paramUnmapped
        self.bootOs = paramBootOs
        self.sysJobGroups = paramSysJobGroups
        self.numOfTasks = 0
        self.numOfThreads = 0
        self.eStackAddress = None
        self.stackRamSize = None
        self.kernelHighAddress = None
        self.kernelLowAddress = None
        self.lowestTaskStackAddress = None
        self.stackMemoryName = None
        self.MaxSysJobsTickMultiplicator = 0