class Route:
    def __init__(self,paramName,paramApiHeader,paramSysCall,paramUserVisible,paramIsMappedToEntity,paramArgs):
        self.name = paramName
        self.apiHeader = paramApiHeader
        self.sysCall = paramSysCall
        self.userVisible = paramUserVisible
        self.isMappedToEntity = paramIsMappedToEntity
        self.args = paramArgs