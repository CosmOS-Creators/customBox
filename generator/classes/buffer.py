class Buffer():
    def __init__(self,paramBufferId,paramName,paramReadPermission,paramWritePermission,paramBufferSize,paramIsDouble):
        self.readPermission = paramReadPermission
        self.writePermission = paramWritePermission
        self.name = paramName
        self.bufferId = paramBufferId
        self.bufferSize = paramBufferSize
        self.isDouble = paramIsDouble
        self.compressedReadPermission = None
        self.compressedWritePermission = None
        self.compressedReadPermissionInverted = None
        self.compressedWritePermissionInverted = None
        self.doubleName = None