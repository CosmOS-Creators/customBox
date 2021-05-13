class Route:
    def __init__(self,paramName,paramSysCall,paramUserVisible,paramIsMappedToEntity,paramArgs):
        self.name = paramName
        self.sysCall = paramSysCall
        self.userVisible = paramUserVisible
        self.isMappedToEntity = paramIsMappedToEntity
        self.args = paramArgs