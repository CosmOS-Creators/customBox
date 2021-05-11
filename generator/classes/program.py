class Program():
    def __init__(self,paramName,paramProgramId,paramCoreId,paramTasks,paramNumOfTasks,paramSize,paramMemory,paramThreads,paramNumOfThreads):
        self.name = paramName
        self.tasks = paramTasks
        self.threads = paramThreads
        self.size = paramSize
        self.numOfTasks = paramNumOfTasks
        self.numOfThreads = paramNumOfThreads
        self.coreId = paramCoreId
        self.programId = paramProgramId
        self.memory = paramMemory
        self.memoryLowAddress = 0
        self.memoryHighAddress = 0