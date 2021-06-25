from privateClasses.chunk import Chunk

class MemoryMapper():

	def doMagic(self,config):
		self.memories = config.memories.iterator
		self.programs = config.programs.iterator
		self.architecture = config.mcu.architecture

		#initialize chunks
		self.assignFreeChunks()

		#allocate memory
		#self.mapOs()
		#self.mapTasksStacks()
		#self.mapThreadStacks()
		self.mapProgramMemory()
		#self.mapUnmappedMemory()
		return

	def mapProgramMemory(self):
        for program in self.programs:
            if program.size:
                lowAddress,highAddress = self.allocateMemory(program.memory,program.size)
                if not lowAddress or not highAddress:
                    raise ValueError("{}{}{}{}".format('Program ',program.name,' with size :',program.size, \
						' bytes cannot be allocated in the ',program.memory,\
						' cause it has only ',self.returnFreeBytes(memory), ' free bytes'))
                else:
                    program.memoryLowAddress = lowAddress
                    program.memoryHighAddress = highAddress

	def assignFreeChunks(self):
		for memory in self.memories:
			highAddress = memory.size + memory.lowAddress
			memory.freeChunks.append(Chunk(memory.lowAddress,highAddress,memory.size))

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
