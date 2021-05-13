class Cosmos():
    def __init__(self,paramCores,paramPrograms,paramTasks,paramBuffers,paramSwitches,paramMaxTaskOnOneCore,\
        paramNumOfInitializedCores,paramNumOfInitializedBuffers,routesParam,paramBuffersDouble,paramThreads):
        self.cores = paramCores
        self.programs = paramPrograms
        self.tasks = paramTasks
        self.buffers = paramBuffers
        self.switches = paramSwitches
        self.maxTaskOnOneCore = paramMaxTaskOnOneCore
        self.numOfInitializedCores = paramNumOfInitializedCores
        self.numOfInitializedBuffers = paramNumOfInitializedBuffers
        self.routes = routesParam
        self.buffersDouble = paramBuffersDouble
        self.threads = paramThreads