import Generator.GeneratorCorePlugins.LogicRunner as logicRunnerPlugin
from Parser.helpers import overrides


class PermissionerLogic(logicRunnerPlugin.logicRunner):

	@overrides(logicRunnerPlugin.logicRunner)
	def doMagic(self,config):
		try:
			config.require([
							'buffers/:readPermissions',
							'buffers/:writePermissions',
							'buffers/:compressedReadPermission',
							'buffers/:compressedWritePermission',
							'buffers/:compressedReadPermissionInverted',
							'buffers/:compressedWritePermissionInverted',
							'mcu/:cpuBitWidth',
							'os/:schedulableNum',
							])
		except Exception as e:
			raise Exception(f"Permissioner is missing required attribute, more info : {str(e)}")

		self.tasks = config.tasks
		self.threads = config.threads
		self.buffers = config.buffers
		self.cpuBitWidth = config.mcu.MCU.cpuBitWidth
		self.maxUniqueId = config.os.os.schedulableNum

		self.permissionCompression()

	def permissionCompression(self):
		for buffer in self.buffers:
			if((len(buffer.readPermissions))):
				buffer.readPermissions.sort(key=lambda x: x.uniqueId, reverse=False)

				readPermissionTemp = [0] * self.getPermissionArraySize(self.maxUniqueId)

				for schedulable in buffer.readPermissions:
					arrayIterator = self.getPermissionArrayIterator(schedulable.uniqueId)
					readPermissionTemp[arrayIterator] = (readPermissionTemp[arrayIterator] | (1 << (schedulable.uniqueId - (self.cpuBitWidth * arrayIterator))))

				buffer.compressedReadPermission = ['{0:0{1}b}'.format(element,self.cpuBitWidth) for element in readPermissionTemp]
				buffer.compressedReadPermissionInverted = [''.join('1' if x == '0' else '0' for x in element) for element in buffer.compressedReadPermission]
			else:
				readPermissionTemp = [0] * self.getPermissionArraySize(self.maxUniqueId)

				buffer.compressedReadPermission = ['{0:0{1}b}'.format(element,self.cpuBitWidth) for element in readPermissionTemp]
				buffer.compressedReadPermissionInverted = [''.join('1' if x == '0' else '0' for x in element) for element in buffer.compressedReadPermission]

			if((len(buffer.writePermissions))):
				buffer.writePermissions.sort(key=lambda x: x.uniqueId, reverse=False)

				writePermissionTemp = [0] * self.getPermissionArraySize(self.maxUniqueId)

				for schedulable in buffer.writePermissions:
					arrayIterator = self.getPermissionArrayIterator(schedulable.uniqueId)
					writePermissionTemp[arrayIterator] = (writePermissionTemp[arrayIterator] | (1 << (schedulable.uniqueId - (self.cpuBitWidth * arrayIterator))))

				buffer.compressedWritePermission = ['{0:0{1}b}'.format(element,self.cpuBitWidth) for element in writePermissionTemp]
				buffer.compressedWritePermissionInverted = [''.join('1' if x == '0' else '0' for x in element) for element in buffer.compressedWritePermission]
			else:
				writePermissionTemp = [0] * self.getPermissionArraySize(self.maxUniqueId)

				buffer.compressedWritePermission = ['{0:0{1}b}'.format(element,self.cpuBitWidth) for element in writePermissionTemp]
				buffer.compressedWritePermissionInverted = [''.join('1' if x == '0' else '0' for x in element) for element in buffer.compressedWritePermission]

	def getPermissionArrayIterator(self, uniqueId):
		iterator = 0
		elementSize = 0
		while elementSize <= uniqueId:
			iterator+=1
			elementSize = self.cpuBitWidth * iterator

		return iterator-1

	def getPermissionArraySize(self, highestUniqueId):
		iterator = 0
		elementSize = 0
		while elementSize <= highestUniqueId:
			iterator+=1
			elementSize = self.cpuBitWidth * iterator

		return iterator
