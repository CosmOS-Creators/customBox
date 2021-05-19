class Cosmos():
    def __init__(self,paramCores,paramPrograms,paramTasks,paramBuffers,paramSwitches,paramMaxSchedulablesOnOneCore,\
        paramNumOfInitializedCores,paramNumOfInitializedBuffers,routesParam,paramBuffersDouble,paramThreads,\
        paramRoutesApiHeaders,paramSysJobsApiHeaders):
        self.cores = paramCores
        self.programs = paramPrograms
        self.tasks = paramTasks
        self.buffers = paramBuffers
        self.switches = paramSwitches
        self.maxSchedulablesOnOneCore = paramMaxSchedulablesOnOneCore
        self.numOfInitializedCores = paramNumOfInitializedCores
        self.numOfInitializedBuffers = paramNumOfInitializedBuffers
        self.routes = routesParam
        self.buffersDouble = paramBuffersDouble
        self.threads = paramThreads
        self.routesApiHeaders = paramRoutesApiHeaders
        self.sysJobsApiHeaders = paramSysJobsApiHeaders