from typing import List
import Generator.GeneratorCorePlugins.LogicRunner as logicRunnerPlugin
from Parser.helpers import overrides
from Parser.ConfigTypes import ConfigElement


class InitializerLogic(logicRunnerPlugin.logicRunner):
    @overrides(logicRunnerPlugin.logicRunner)
    def doMagic(self, config):
        try:
            config.require(
                [
                    "buffers/:bufferId",
                    "buffers/:doubleBufferId",
                    "buffers/:isDoubleBuffer",
                    "buffers/:readPermissions",
                    "buffers/:writePermissions",
                    "buffers/:compressedReadPermission",
                    "buffers/:compressedWritePermission",
                    "buffers/:compressedReadPermissionInverted",
                    "buffers/:compressedWritePermissionInverted",
                    "channels/:channelId",
                    "channels/:semaphoreId",
                    "channels/:replyPermissions",
                    "channels/:sendPermissions",
                    "channels/:compressedReplyPermission",
                    "channels/:compressedSendPermission",
                    "channels/:compressedReplyPermissionInverted",
                    "channels/:compressedSendPermissionInverted",
                    "mcu/:cpuBitWidth",
                    "cores/:coreId",
                    "cores/:coreSysJobGroups",
                    "cores/:coreScheduler",
                    "cores/:coreSysJobHyperTick",
                    "cores/:corePrograms",
                    "cores/:cpu",
                    "cores/:prioSortedThreads",
                    "programs/:programId",
                    "programs/:core",
                    "programs/:programThreads",
                    "programs/:programTasks",
                    "tasks/:program",
                    "tasks/:taskId",
                    "tasks/:uniqueId",
                    "threads/:program",
                    "threads/:threadId",
                    "threads/:uniqueId",
                    "threads/:alarmId",
                    "sysJobs/:groupId",
                    "sysJobs/:core",
                    "sysJobs/:tickMultiplicator",
                    "os/:schedulableNum",
                    "os/:buffersNum",
                    "os/:doubleBuffersNum",
                    "os/:eventSpinlockId",
                    "scheduleTableEntries/:scheduler",
                    "scheduleTableEntries/:entryId",
                    "scheduleTableEntries/:executionTick",
                    "schedulers/:table",
                    "schedulers/:core",
                    "schedulers/:maxTimerTick",
                    "spinlocks/:spinlockId",
                    "semaphores/:semaphoreId",
                    "buffers/:spinlockId",
                    "buffers/:isInterCore",
                    "cpu/:systemTimerWidth",
                    "cpu/:systemTimerTickCount",
                ]
            )
        except Exception as e:
            raise Exception(
                f"Initializer is missing required attribute, more info : {str(e)}"
            ) from e

        self.maxUniqueId = None

        self.cores = config.cores  # type: List[ConfigElement]
        self.cpus = config.cpu  # type: List[ConfigElement]
        self.programs = config.programs  # type: List[ConfigElement]
        self.tasks = config.tasks  # type: List[ConfigElement]
        self.threads = config.threads  # type: List[ConfigElement]
        self.buffers = config.buffers  # type: List[ConfigElement]
        self.channels = config.channels  # type: List[ConfigElement]
        self.sysJobs = config.sysJobs  # type: List[ConfigElement]
        self.schedulers = config.schedulers  # type: List[ConfigElement]
        self.scheduleTableEntries = (
            config.scheduleTableEntries
        )  # type: List[ConfigElement]
        self.spinlocks = config.spinlocks  # type: List[ConfigElement]
        self.semaphores = config.semaphores  # type: List[ConfigElement]
        self.cpuBitWidth = config.mcu.MCU.cpuBitWidth
        self.os = config.os.os

        self.highestSpinlockId = 0
        self.highestSemaphoreId = 0

        # sequence of the functions must be kept
        self.assigneUniqueId()
        self.assigneIterativeId()
        self.assigneSysJobHypertick()
        self.assigneSchedulerEntries()
        self.assigneBufferSpinlocks()
        self.assigneChannelSemaphores()
        self.assigneEventSpinlock()
        self.assigneMaxTimerTick()

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
            alarmIterativeId = 0
            coreIterativeId += 1
            for program in self.programs:
                if program.core == core:
                    core.corePrograms.append(program)
                    program.programId = programIterativeId
                    programIterativeId += 1
                    threadIterativeId = 0
                    taskIterativeId = 0
                    for thread in self.threads:
                        if thread.program == program:
                            program.programThreads.append(thread)
                            core.prioSortedThreads.append(thread)
                            thread.threadId = threadIterativeId
                            thread.alarmId = alarmIterativeId
                            threadIterativeId += 1
                            alarmIterativeId += 1
                            coreNumberOfThreads += 1
                    for task in self.tasks:
                        if task.program == program:
                            program.programTasks.append(task)
                            task.taskId = taskIterativeId
                            taskIterativeId += 1
                            coreNumberOfTasks += 1
            sysJobGroupIterativeId = 0
            for sysJobGroup in self.sysJobs:
                if sysJobGroup.core == core:
                    core.coreSysJobGroups.append(sysJobGroup)
                    sysJobGroup.groupId = sysJobGroupIterativeId
                    sysJobGroupIterativeId += 1
            for scheduler in self.schedulers:
                if scheduler.core == core:
                    core.coreScheduler.append(scheduler)
            core.coreNumberOfThreads = coreNumberOfThreads
            core.coreNumberOfTasks = coreNumberOfTasks
            core.prioSortedThreads = sorted(
                core.prioSortedThreads, key=lambda x: x.priority, reverse=True
            )
        bufferIterativeId = 0
        doubleBufferIterativeId = 0
        for buffer in self.buffers:
            buffer.bufferId = bufferIterativeId
            bufferIterativeId += 1
            if buffer.isDoubleBuffer:
                bufferIterativeId += 1
                buffer.doubleBufferId = doubleBufferIterativeId
                doubleBufferIterativeId += 1
        spinlockIterativeId = 0
        for spinlock in self.spinlocks:
            spinlock.spinlockId = spinlockIterativeId
            spinlockIterativeId += 1

        semaphoreIterativeId = 0
        for semaphore in self.semaphores:
            semaphore.semaphoreId = semaphoreIterativeId
            semaphoreIterativeId += 1

        self.os.buffersNum = bufferIterativeId
        self.os.doubleBuffersNum = doubleBufferIterativeId

        channelIterativeId = 0
        for channel in self.channels:
            channel.channelId = channelIterativeId
            channelIterativeId += 1

        self.os.channelsNum = channelIterativeId
        self.highestSpinlockId = sorted(
            self.spinlocks, key=lambda x: x.spinlockId, reverse=True
        )[0].spinlockId

        self.highestSemaphoreId = sorted(
            self.semaphores, key=lambda x: x.semaphoreId, reverse=True
        )[0].semaphoreId

    def assigneSysJobHypertick(self):
        for core in self.cores:
            if len(core.coreSysJobGroups):
                core.coreSysJobHyperTick = max(
                    SysJobGroup.tickMultiplicator for SysJobGroup in core.coreSysJobGroups
                )

    def assigneSchedulerEntries(self):
        for scheduler in self.schedulers:
            for entry in self.scheduleTableEntries:
                if entry.scheduler == scheduler:
                    scheduler.table.append(entry)
            scheduler.table.sort(key=lambda entry: entry.executionTick)
            entryIterativeId = 0
            for entry in scheduler.table:
                entry.entryId = entryIterativeId
                entryIterativeId += 1

    def assigneBufferSpinlocks(self):
        for buffer in self.buffers:
            coreId = 0
            isInterCore = False
            for readPermission in buffer.readPermissions:
                if coreId is not readPermission.program.core.coreId:
                    isInterCore = True
                    break
            for writePermission in buffer.writePermissions:
                if coreId is not writePermission.program.core.coreId:
                    isInterCore = True
                    break
            self.highestSpinlockId += 1
            buffer.spinlockId = self.highestSpinlockId
            if buffer.isDoubleBuffer:
                self.highestSpinlockId += 1

            buffer.isInterCore = isInterCore

    def assigneChannelSemaphores(self):
        for channel in self.channels:
            self.highestSemaphoreId += 1
            channel.semaphoreId = self.highestSemaphoreId

    def assigneEventSpinlock(self):
        self.highestSpinlockId += 1
        self.os.eventSpinlockId = self.highestSpinlockId

    def assigneMaxTimerTick(self):
        for scheduler in self.schedulers:
            cpu = [
                cpu
                for cpu in [core.cpu for core in self.cores if scheduler.core == core]
            ][0]
            scheduler.maxTimerTick = (
                2 ** cpu.systemTimerWidth - 1
            ) / cpu.systemTimerTickCount
