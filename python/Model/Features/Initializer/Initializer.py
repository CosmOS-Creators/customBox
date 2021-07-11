from typing import List
import Generator.GeneratorCorePlugins.LogicRunner as logicRunnerPlugin
from Parser.helpers import overrides
from Parser.ConfigTypes import ConfigElement

class InitializerLogic(logicRunnerPlugin.logicRunner):

	@overrides(logicRunnerPlugin.logicRunner)
	def doMagic(self, config):
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
							'cores/:coreSysJobGroups',
							'programs/:programId',
							'programs/:core',
							'tasks/:program',
							'tasks/:taskId',
							'tasks/:uniqueId',
							'threads/:program',
							'threads/:threadId',
							'threads/:uniqueId',
							'sysJobs/:groupId',
							])
		except Exception as e:
			raise Exception(f"Initializer is missing required attribute, more info : {str(e)}")

		self.maxUniqueId = None

		self.cores = config.cores.iterator										#type: List[ConfigElement]
		self.programs = config.programs.iterator								#type: List[ConfigElement]
		self.buffers = config.buffers.iterator									#type: List[ConfigElement]
		self.tasks = config.tasks.iterator										#type: List[ConfigElement]
		self.threads = config.threads.iterator									#type: List[ConfigElement]
		self.buffers = config.buffers.iterator									#type: List[ConfigElement]
		self.sysJobs = config.sysJobs.iterator									#type: List[ConfigElement]
		self.schedulers = config.schedulers.iterator							#type: List[ConfigElement]
		self.scheduleTableEntries = config.scheduleTableEntries.iterator		#type: List[ConfigElement]
		self.cpuBitWidth = config.mcu.MCU.cpuBitWidth
		self.os = config.os.os

		self.assigneUniqueId()
		self.assigneIterativeId()
		self.assigneSysJobHypertick()
		self.assigneSchedulerEntries()

	def assigneUniqueId(self):
		uniqueId = 0
		for task in self.tasks:
			task.uniqueId = uniqueId
			uniqueId += 1
		for thread in self.threads:
			thread.uniqueId = uniqueId
			uniqueId += 1
		self.os.schedulableNum = uniqueId

	def assigneIterativeId(self):
		coreIterativeId = 0
		for core in self.cores:
			core.coreId = coreIterativeId
			programIterativeId = 0
			coreNumberOfThreads = 0
			coreNumberOfTasks = 0
			coreIterativeId += 1
			for program in self.programs:
				if (program.core == core):
					core.corePrograms.append(program)
					program.programId = programIterativeId
					programIterativeId += 1
					threadIterativeId = 0
					taskIterativeId = 0
					for thread in self.threads:
						if (thread.program == program):
							program.programThreads.append(thread)
							thread.threadId = threadIterativeId
							threadIterativeId += 1
							coreNumberOfThreads += 1
					for task in self.tasks:
						if (task.program == program):
							program.programTasks.append(task)
							task.taskId = taskIterativeId
							taskIterativeId += 1
							coreNumberOfTasks += 1
			sysJobGroupIterativeId = 0
			for sysJobGroup in self.sysJobs:
				if (sysJobGroup.core == core):
					core.coreSysJobGroups.append(sysJobGroup)
					sysJobGroup.groupId = sysJobGroupIterativeId
					sysJobGroupIterativeId += 1
			for scheduler in self.schedulers:
				if (scheduler.core == core):
					core.coreScheduler.append(scheduler)
			core.coreNumberOfThreads = coreNumberOfThreads
			core.coreNumberOfTasks = coreNumberOfTasks
		bufferIterativeId = 0
		doubleBufferIterativeId = 0
		for buffer in self.buffers:
			buffer.bufferId = bufferIterativeId
			bufferIterativeId += 1
			if (buffer.isDoubleBuffer):
				bufferIterativeId += 1
				buffer.doubleBufferId = doubleBufferIterativeId
				doubleBufferIterativeId += 1
		self.os.buffersNum = bufferIterativeId
		self.os.doubleBuffersNum = doubleBufferIterativeId

	def assigneSysJobHypertick(self):
		for core in self.cores:
			core.coreSysJobHyperTick = max(SysJobGroup.tickMultiplicator for SysJobGroup in core.coreSysJobGroups)

	def assigneSchedulerEntries(self):
		for scheduler in self.schedulers:
			for entry in self.scheduleTableEntries:
				if (entry.scheduler == scheduler):
					scheduler.table.append(entry)
			scheduler.table.sort(key=lambda entry: entry.executionTick)
			entryIterativeId = 0
			for entry in scheduler.table:
				entry.entryId = entryIterativeId
				entryIterativeId += 1
