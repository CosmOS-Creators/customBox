from Model.Features.MemoryMapper.privateClasses.chunk import Chunk
import Generator.GeneratorCorePlugins.LogicRunner as logicRunnerPlugin
from Parser.helpers import overrides

class MemoryMapperLogic(logicRunnerPlugin.logicRunner):

	@overrides(logicRunnerPlugin.logicRunner)
	def doMagic(self,config):
		try:
			config.require([
							'memories/:lowAddress',
							'memories/:size',
							'kernels/:lowAddress',
							'kernels/:highAddress',
							'kernels/:core',
							'kernels/:stackSize',
							'osPartitions/:name',
							'osPartitions/:size',
							'osPartitions/:memory',
							'osPartitions/:lowAddress',
							'osPartitions/:highAddress',
							'programs/:size',
							'programs/:memory',
							'programs/:name',
							'programs/:lowAddress',
							'programs/:highAddress',
							'programs/:core',
							'cpu/:stackMemory',
							'cores/:unmappedDataSize',
							'cores/:unmappedDataMemory',
							'cores/:unmappedDataLowAddress',
							'cores/:unmappedDataHighAddress',
							'cores/:userCodeSize',
							'cores/:userCodeMemory',
							'cores/:userCodeLowAddress',
							'cores/:userCodeHighAddress',
							'cores/:cpu',
							'tasks/:stackSize',
							'tasks/:name',
							'tasks/:lowAddress',
							'tasks/:highAddress',
							'tasks/:program',
							'threads/:stackSize',
							'threads/:name',
							'threads/:lowAddress',
							'threads/:highAddress',
							'threads/:program',
							'mcu/MCU:architecture'
							])
		except Exception as e:
			raise Exception(f"MemoryMapper is missing required attribute, more info : {str(e)}") from e

		self.memories = config.memories
		self.kernels = config.kernels
		self.osPartitions = config.osPartitions
		self.programs = config.programs
		self.cores = config.cores
		self.tasks = config.tasks
		self.threads = config.threads
		self.architecture = config.mcu.MCU.architecture

		self.assignFreeChunks()

		#must be executed first to place startup code first to the flash - requirement by stm
		self.mapStaticData()

		self.mapKernelStacks()
		self.mapOsData()
		self.mapTasksStacks()
		self.mapThreadStacks()
		self.mapProgramData()
		self.mapUnmappedData()
		self.mapUserCode()

	def assignFreeChunks(self):
		for memory in self.memories:
			highAddress = memory.size + memory.lowAddress
			memory.freeChunks.append(Chunk(memory.lowAddress,highAddress,memory.size))

	def mapKernelStacks(self):
		for kernel in self.kernels:
			stackMemory = kernel.core.cpu.stackMemory
			lowAddress,highAddress = self.allocateMemory(stackMemory,kernel.stackSize)
			if not lowAddress or not highAddress:
					raise ValueError(f"Kernel for core {kernel.core.name} with stack size :{kernel.stackSize} bytes cannot be allocated in the {stackMemory}\
									cause it has only {self.returnFreeBytes(stackMemory)} free bytes")
			else:
				kernel.lowAddress = lowAddress
				kernel.highAddress = highAddress

	def mapOsData(self):
		for osPartition in self.osPartitions:
			if osPartition.size:
				lowAddress,highAddress = self.allocateMemory(osPartition.memory,osPartition.size)
				if not lowAddress or not highAddress:
					raise ValueError(f"OsPartition {osPartition.name} with size :{osPartition.size} bytes cannot be allocated in the {osPartition.memory}\
									cause it has only {self.returnFreeBytes(osPartition.memory)} free bytes")
				else:
					osPartition.lowAddress = lowAddress
					osPartition.highAddress = highAddress

	def mapTasksStacks(self):
		for core in self.cores:
			taskWithMaxStackSize = None
			maxStackSize = 0
			for task in self.tasks:
				if (task.program.core == core):
					if (task.stackSize > maxStackSize):
						taskWithMaxStackSize = task
						maxStackSize = task.stackSize
			stackMemory = core.cpu.stackMemory
			lowAddress,highAddress = self.allocateMemory(stackMemory,taskWithMaxStackSize.stackSize)
			if not lowAddress or not highAddress:
					raise ValueError(f"Task {taskWithMaxStackSize.name} stack with size :{taskWithMaxStackSize.stackSize} bytes cannot be allocated in the {stackMemory}\
									cause it has only {self.returnFreeBytes(stackMemory)} free bytes")
			else:
				taskWithMaxStackSize.lowAddress = lowAddress
				taskWithMaxStackSize.highAddress = highAddress
			for task in self.tasks:
				if (task.program.core == taskWithMaxStackSize.program.core):
					task.lowAddress = taskWithMaxStackSize.highAddress - task.stackSize
					task.highAddress = taskWithMaxStackSize.highAddress

	def mapThreadStacks(self):
		for thread in self.threads:
			stackMemory = thread.program.core.cpu.stackMemory
			lowAddress,highAddress = self.allocateMemory(stackMemory,thread.stackSize)
			if not lowAddress or not highAddress:
					raise ValueError(f"Thread {thread.name} stack with size :{thread.stackSize} bytes cannot be allocated in the {stackMemory}\
									cause it has only {self.returnFreeBytes(stackMemory)} free bytes")
			else:
				thread.lowAddress = lowAddress
				thread.highAddress = highAddress

	def mapProgramData(self):
		for program in self.programs:
			if program.size:
				lowAddress,highAddress = self.allocateMemory(program.memory,program.size)
				if not lowAddress or not highAddress:
					raise ValueError(f"Program {program.name} with size :{program.size} bytes cannot be allocated in the {program.memory}\
									cause it has only {self.returnFreeBytes(program.memory)} free bytes")
				else:
					program.lowAddress = lowAddress
					program.highAddress = highAddress

	def mapUnmappedData(self):
		for core in self.cores:
			if core.unmappedDataSize:
				lowAddress,highAddress = self.allocateMemory(core.unmappedDataMemory,core.unmappedDataSize)
				if not lowAddress or not highAddress:
					raise ValueError(f"Unmapped data for core {core.name} with size :{core.unmappedDataSize} bytes cannot be allocated in the {core.unmappedDataMemory}\
									cause it has only {self.returnFreeBytes(core.unmappedDataMemory)} free bytes")
				else:
					core.unmappedDataLowAddress = lowAddress
					core.unmappedDataHighAddress = highAddress

	def mapUserCode(self):
		for core in self.cores:
			if core.userCodeSize:
				lowAddress,highAddress = self.allocateMemory(core.userCodeMemory,core.userCodeSize)
				if not lowAddress or not highAddress:
					raise ValueError(f"User code for core {core.name} with size :{core.userCodeSize} bytes cannot be allocated in the {core.userCodeMemory}\
									cause it has only {self.returnFreeBytes(core.userCodeMemory)} free bytes")
				else:
					core.userCodeLowAddress = lowAddress
					core.userCodeHighAddress = highAddress

	def mapStaticData(self):
		for core in self.cores:
			if core.staticDataSize:
				lowAddress,highAddress = self.allocateMemory(core.staticDataMemory,core.staticDataSize)
				if not lowAddress or not highAddress:
					raise ValueError(f"Unmapped code for core {core.name} with size :{core.staticDataSize} bytes cannot be allocated in the {core.staticDataMemory}\
									cause it has only {self.returnFreeBytes(core.staticDataMemory)} free bytes")
				else:
					core.staticDataLowAddress = lowAddress
					core.staticDataHighAddress = highAddress

	def allocateMemory(self, memory, size):
		lowAddress = None
		highAddress = None

		if ( self.architecture == "ARMv7" ):
			lowAddress,highAddress =  self.allocateMemoryARMv7(memory, size)

		return lowAddress,highAddress

	def allocateMemoryARMv7(self, memory, size):
		lowAddress = None
		highAddress = None

		memory.freeChunks.sort(key=lambda x: x.size)

		for chunk in memory.freeChunks:
			if size == chunk.size and not(chunk.lowAddress % size):
				lowAddress = chunk.lowAddress
				highAddress = chunk.highAddress
				memory.freeChunks.remove(chunk)
				break
			elif size < chunk.size:
				if not(chunk.lowAddress % size):
					lowAddress = chunk.lowAddress
					highAddress = lowAddress + size
					chunkNewSize = chunk.highAddress - highAddress
					memory.freeChunks.append(Chunk(highAddress,chunk.highAddress,chunkNewSize))
					memory.freeChunks.remove(chunk)
					break
				else:
					newLowAddress = self.closestHigherNumber(chunk.lowAddress,size)
					if size == (chunk.highAddress - newLowAddress):
						lowAddress = newLowAddress
						highAddress = chunk.highAddress
						chunkNewSize = newLowAddress - chunk.lowAddress
						memory.freeChunks.append(Chunk(chunk.lowAddress,newLowAddress,chunkNewSize))
						memory.freeChunks.remove(chunk)
						break
					elif size < (chunk.highAddress - newLowAddress):
						lowAddress = newLowAddress
						highAddress = newLowAddress + size
						chunkNewSize = newLowAddress - chunk.lowAddress
						memory.freeChunks.append(Chunk(chunk.lowAddress,newLowAddress,chunkNewSize))
						chunkNewSize = chunk.highAddress - highAddress
						memory.freeChunks.append(Chunk(highAddress,chunk.highAddress,chunkNewSize))
						memory.freeChunks.remove(chunk)
						break

		return lowAddress,highAddress

	def returnFreeBytes(self, memory):
		freeBytes = 0
		for chunk in memory.freeChunks:
			freeBytes += chunk.size
		return freeBytes

	def closestLowerNumber(self,n, m) :
		q = int(n / m)
		n2 = m * q
		return n2

	def closestHigherNumber(self,n, m) :
		q = int(n / m)
		n2 = m * (q+1)
		return n2
