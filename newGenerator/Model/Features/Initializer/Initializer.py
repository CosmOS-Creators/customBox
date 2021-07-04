class Initializer():

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
							'cores/:coreId',
							'programs/:programId',
							'programs/:core',
							'tasks/:program',
							'tasks/:taskId',
							'tasks/:uniqueId',
							'threads/:program',
							'threads/:threadId',
							'threads/:uniqueId',
							])
		except Exception as e:
			raise Exception(f"Initializer is missing required attribute, more info : {str(e)}")

		self.maxUniqueId = None

		self.cores = config.cores.iterator
		self.programs = config.programs.iterator
		self.tasks = config.tasks.iterator
		self.threads = config.threads.iterator
		self.buffers = config.buffers.iterator
		self.cpuBitWidth = config.mcu.MCU.cpuBitWidth

		self.assigneUniqueId()
		self.assigneIterativeId()

	def assigneUniqueId(self):
		uniqueId = 0
		for task in self.tasks:
			task.uniqueId = uniqueId
			uniqueId += 1
		for thread in self.threads:
			thread.uniqueId = uniqueId
			uniqueId += 1
		self.maxUniqueId = uniqueId

	def assigneIterativeId(self):
		coreIterativeId = 0
		for core in self.cores:
			core.coreId = coreIterativeId
			coreIterativeId += 1
			programIterativeId = 0
			for program in self.programs:
				if (program.core == core):
					core.corePrograms.append(program)
					program.programId = programIterativeId
					programIterativeId +=1
					threadIterativeId = 0
					taskIterativeId = 0
					for thread in self.threads:
						if (thread.program == program):
							program.programThreads.append(thread)
							thread.threadId = threadIterativeId
							threadIterativeId += 1
					for task in self.tasks:
						if (task.program == program):
							program.programTasks.append(task)
							task.taskId = taskIterativeId
							taskIterativeId += 1
