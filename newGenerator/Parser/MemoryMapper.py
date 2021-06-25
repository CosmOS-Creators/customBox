from privateClasses.chunk import Chunk

class MemoryMapper():

	def doMagic(self,config):

		config.require(['osPartitions/:name',
						'osPartitions/:size',
						'osPartitions/:memory',
						'osPartitions/:lowAddress',
						'osPartitions/:highAddress',
						'memories/:lowAddress',
						'memories/:size',
						'programs/:size',
						'programs/:memory',
						'programs/:name',
						'programs/:lowAddress',
						'programs/:highAddress',
						'mcu/MCU:architecture'])

		self.memories = config.memories.iterator
		self.osPartitions = config.osPartitions.iterator
		self.programs = config.programs.iterator
		self.cpus = config.cpu.iterator
		self.threads = config.threads.iterator
		self.architecture = config.mcu.MCU.architecture

		#initialize chunks
		self.assignFreeChunks()

		#allocate memory
		#self.mapTasksStacks()
		self.mapOS()
		self.mapThreadStacks()
		self.mapProgramMemory()
		#self.mapUnmappedMemory()

	def assignFreeChunks(self):
		for memory in self.memories:
			highAddress = memory.size + memory.lowAddress
			memory.freeChunks.append(Chunk(memory.lowAddress,highAddress,memory.size))

	def mapOS(self):
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
		for task in self.tasks:
			for cpu in self.cpus:
				if task.program.core == cpu.core:
					startingAddress = int(self.cores[coreId].kernelLowAddress,0)
					if startingAddress % task.stackSize :
						startingAddress = closestLowerNumber(startingAddress,task.stackSize)
					if (startingAddress - task.stackSize) < (self.cores[coreId].eStackAddress - self.cores[coreId].stackRamSize):
						raise ValueError("{}{}{}".format('Task ',task.name,' is too large and cannot be placed into the RAM'))
					self.cores[coreId].numOfTasks += 1
					task.highAddress = startingAddress
					task.lowAddress = task.highAddress - task.stackSize
					if self.cores[coreId].lowestTaskStackAddress > task.lowAddress :
						self.cores[coreId].lowestTaskStackAddress = task.lowAddress
					task.highAddress = hex(task.highAddress)
					task.lowAddress = hex(task.lowAddress)
		for memory in self.memories:
			if memory.name == self.cores[coreId].stackMemoryName:
				if self.cores[coreId].lowestTaskStackAddress == memory.freeChunks[0].lowAddress:
					memory.freeChunks.remove(memory.freeChunks[0])
				else:
					chunkNewSize = self.cores[coreId].lowestTaskStackAddress - memory.freeChunks[0].lowAddress
					memory.freeChunks.append(Chunk(memory.freeChunks[0].lowAddress,self.cores[coreId].lowestTaskStackAddress,chunkNewSize))
					memory.freeChunks.remove(memory.freeChunks[0])

	def mapThreadStacks(self):
		for thread in self.threads:
			for cpu in self.cpus:
				stackMemory = None
				if thread.program.core == cpu.core:
					stackMemory = cpu.stackMemory
				if not stackMemory:
					raise ValueError("BULLSHIT")
			lowAddress,highAddress = self.updateFreeMemory(stackMemory,thread.stackSize)
			if not lowAddress or not highAddress:
					raise ValueError(f"Thread {thread.name} stack with size :{thread.size} bytes cannot be allocated in the {stackMemory}\
									cause it has only {self.returnFreeBytes(stackMemory)} free bytes")
			else:
				thread.lowAddress = lowAddress
				thread.highAddress = highAddress

	def mapProgramMemory(self):
		for program in self.programs:
			if program.size:
				lowAddress,highAddress = self.allocateMemory(program.memory,program.size)
				if not lowAddress or not highAddress:
					raise ValueError(f"Program {program.name} with size :{program.size} bytes cannot be allocated in the {program.memory}\
									cause it has only {self.returnFreeBytes(program.memory)} free bytes")
				else:
					program.lowAddress = lowAddress
					program.highAddress = highAddress

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
