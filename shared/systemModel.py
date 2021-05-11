import json
import importlib.util
import sys

from numpy import invert

module_name = 'chunk'
file_path = 'Cosmos/CustomBox/generator/classes/chunk.py'

spec = importlib.util.spec_from_file_location(module_name, file_path)
module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = module
spec.loader.exec_module(module)

from chunk import Chunk
from mcu import Mcu
from core import Core
from task import Task
from switch import Switch
from buffer import Buffer
from cosmos import Cosmos
from memory import Memory
from thread import Thread
from program import Program
from unmapped import Unmapped
from scheduler import Scheduler
from permission import Permission
from sysJobGroup import SysJobGroup
from bufferDouble import BufferDouble
from scheduleTableElement import ScheduleTableElement


def closestLowerNumber(n, m) :
    q = int(n / m)
    n2 = m * q
    return n2

def closestHigherNumber(n, m) :
    q = int(n / m)
    n2 = m * (q+1)
    return n2

class SystemModel():
    def __init__(self,paramSystemModelCfgPath,paramMcuCfgPath):

        self.cores = []
        self.programs = []
        self.tasks = []
        self.threads = []
        self.buffers = []
        self.buffersDouble = []
        self.memories = []
        
        self.switches = None
        self.sysCalls = None
        self.mcu = None
        self.os = None
        self.CosmOSVersion = None

        self.systemModelCfg = paramSystemModelCfgPath
        self.mcuCfg = paramMcuCfgPath

        #the order cannot be changed
        self.parseSystemModelCfg()
        self.parseMcuCfg()
        self.placeTasksStacks()
        self.placeThreadStacks()
        self.allocateUnmappedMemory()
        self.allocateProgramMemory()
        self.schedulerLastToFirstTaskTick()
        self.permissionCompression()
        self.doubleBuffersInit()
        self.getMaxSysJobsTickMultiplicator()
        self.initOs()

    def parseSystemModelCfg(self):

        with open(self.systemModelCfg , 'r') as myfile:
            data=myfile.read()

        systemModelCfg = json.loads(data)

        cores = []
        programs = []
        tasks = []
        buffers = []
        threads = []

        programsTemp = []
        tasksTemp = []
        threadsTemp = []
        tableTemp = []
        writePermissionCoreGroupsTemp = []
        readPermissionCoreGroupsTemp = []
        sysJobGroupsTemp = []

        coreIterator = 0
        programIterator = 0
        taskIterator = 0
        taskStackIterator = 0
        threadIterator = 0
        threadStackIterator = 0
        elementIterator = 0
        bufferIterator = 0
        sysJobGroupIterator = 0
        schedulableIterator = 0

        self.CosmOSVersion = systemModelCfg['CosmOSVersion']

        for core in systemModelCfg['cores']:
            coreName = systemModelCfg['cores'][core]['name']
            bootOs = systemModelCfg['cores'][core]['bootOs']
            for element in systemModelCfg['cores'][core]['scheduler']['table']:
                coreId = systemModelCfg['cores'][core]['scheduler']['table'][element]['core']
                programId = systemModelCfg['cores'][core]['scheduler']['table'][element]['program']
                taskId = systemModelCfg['cores'][core]['scheduler']['table'][element]['task']
                executionTick = systemModelCfg['cores'][core]['scheduler']['table'][element]['executionTick']
                tableTemp.append(ScheduleTableElement(coreId,int(programId),int(taskId),int(executionTick),elementIterator))
                elementIterator+=1
            elementIterator = 0
            for program in systemModelCfg['cores'][core]['programs']:
                programName = systemModelCfg['cores'][core]['programs'][program]['name']
                programSize = systemModelCfg['cores'][core]['programs'][program]['size']
                programMemory = systemModelCfg['cores'][core]['programs'][program]['memory']
                for task in systemModelCfg['cores'][core]['programs'][program]['tasks']:
                    taskName = systemModelCfg['cores'][core]['programs'][program]['tasks'][task]['name']
                    wcet = systemModelCfg['cores'][core]['programs'][program]['tasks'][task]['wcet']
                    period = systemModelCfg['cores'][core]['programs'][program]['tasks'][task]['period']
                    taskStackSize = systemModelCfg['cores'][core]['programs'][program]['tasks'][task]['stack']['size']
                    floatingPoint = systemModelCfg['cores'][core]['programs'][program]['tasks'][task]['floatingPoint']
                    tasksTemp.append(Task(taskName,int(wcet),period,coreIterator,programIterator,taskIterator,taskStackIterator,int(taskStackSize),floatingPoint,schedulableIterator))
                    taskStackIterator+=1
                    taskIterator+=1
                    schedulableIterator+=1
                for thread in systemModelCfg['cores'][core]['programs'][program]['threads']:
                    threadName = systemModelCfg['cores'][core]['programs'][program]['threads'][thread]['name']
                    threadStackSize = systemModelCfg['cores'][core]['programs'][program]['threads'][thread]['stack']['size']
                    floatingPoint = systemModelCfg['cores'][core]['programs'][program]['threads'][thread]['floatingPoint']
                    threadsTemp.append(Thread(threadName,coreIterator,programIterator,threadIterator,threadStackIterator,int(threadStackSize),floatingPoint,schedulableIterator))
                    threadStackIterator+=1
                    threadIterator+=1
                    schedulableIterator+=1
                programsTemp.append(Program(programName,programIterator,coreIterator,tasksTemp,len(tasksTemp),int(programSize),programMemory,threadsTemp,len(threadsTemp)))
                tasks += tasksTemp
                threads += threadsTemp
                tasksTemp = []
                threadsTemp = []
                programIterator+=1
                taskIterator = 0
                threadIterator = 0
            for sysJobGroup in systemModelCfg['cores'][core]['sysJobs']:
                handlers = systemModelCfg['cores'][core]['sysJobs'][sysJobGroup]['handlers']
                tickMultiplicator = int(systemModelCfg['cores'][core]['sysJobs'][sysJobGroup]['tickMultiplicator'])
                sysJobGroupsTemp.append(SysJobGroup(sysJobGroupIterator,coreIterator,handlers,tickMultiplicator))
                sysJobGroupIterator+=1
            sysJobGroupIterator = 0
            schedulerHyperTick = systemModelCfg['cores'][core]['scheduler']['hyperTick']
            syncTicks = systemModelCfg['cores'][core]['scheduler']['syncTicks']
            firstSyncTaskStartTick = systemModelCfg['cores'][core]['scheduler']['firstSyncTaskStartTick']
            preemptTick = systemModelCfg['cores'][core]['scheduler']['preemptTick']
            unmappedSize = int(systemModelCfg['cores'][core]['unmapped']['size'])
            unmappedMemory = systemModelCfg['cores'][core]['unmapped']['memory']
            cores.append(Core(coreName,programsTemp,coreIterator,\
                Scheduler(int(schedulerHyperTick),tableTemp,coreIterator,len(tableTemp),syncTicks,firstSyncTaskStartTick,preemptTick),\
                Unmapped(unmappedSize,unmappedMemory,coreIterator),\
                    bootOs,\
                        sysJobGroupsTemp))
            sysJobGroupsTemp = []
            tableTemp = []
            programs += programsTemp
            programsTemp = []
            coreIterator+=1
            programIterator = 0

        for iterator in range(coreIterator):
            readPermissionCoreGroupsTemp.append([])
            writePermissionCoreGroupsTemp.append([])


        for buffer in systemModelCfg['buffers']:
            bufferSize = systemModelCfg['buffers'][buffer]['size']
            bufferName = systemModelCfg['buffers'][buffer]['name']
            bufferIsDouble = systemModelCfg['buffers'][buffer]['isDoubleBuffer']
            for element in systemModelCfg['buffers'][buffer]['readPermissions']:
                coreId = systemModelCfg['buffers'][buffer]['readPermissions'][element]['core']
                taskId = systemModelCfg['buffers'][buffer]['readPermissions'][element]['task']
                readPermissionCoreGroupsTemp[int(coreId)].append(Permission(int(coreId),int(taskId)))
            for element in systemModelCfg['buffers'][buffer]['writePermissions']:
                coreId = systemModelCfg['buffers'][buffer]['writePermissions'][element]['core']
                taskId = systemModelCfg['buffers'][buffer]['writePermissions'][element]['task']
                writePermissionCoreGroupsTemp[int(coreId)].append(Permission(int(coreId),int(taskId)))
            currentBuffer = Buffer(bufferIterator,bufferName,readPermissionCoreGroupsTemp[:],writePermissionCoreGroupsTemp[:],bufferSize,bufferIsDouble)
            if bufferIsDouble :
                currentBuffer.doubleName = bufferIsDouble = systemModelCfg['buffers'][buffer]['double']['name']
            buffers.append(currentBuffer)
            bufferIterator+=1
            for iterator in range(coreIterator):
                readPermissionCoreGroupsTemp[iterator] = []
                writePermissionCoreGroupsTemp[iterator] = []

        self.cores = cores
        self.programs = programs
        self.tasks = tasks
        self.threads = threads
        self.buffers = buffers
        self.switches = Switch( systemModelCfg['switches']['memoryProtection'],\
                                systemModelCfg['switches']['coreSync'],\
                                systemModelCfg['switches']['performanceScheduling'])

        self.sysCalls = systemModelCfg['sysCalls']

    def parseMcuCfg(self):

        with open(self.mcuCfg, 'r') as myfile:
            data = myfile.read()

        mcuCfg = json.loads(data)

        name = mcuCfg['mcu']['name']
        bitWidth = int(mcuCfg['mcu']['bitWidth'])

        self.mcu = Mcu(name,bitWidth)

        for core in mcuCfg['cores']:
            coreName = mcuCfg['cores'][core]['name']
            estackAddress = mcuCfg['cores'][core]['e_stack_address']
            stackRamSize = mcuCfg['cores'][core]['stack_ram_size']
            stackMemory = mcuCfg['cores'][core]['stack_memory']
            for coreItem in self.cores:
                if coreItem.name == coreName:
                    coreItem.stackMemoryName = stackMemory
                    coreItem.eStackAddress = int(estackAddress)
                    coreItem.kernelHighAddress = int(estackAddress)
                    coreItem.kernelLowAddress = int(estackAddress) - coreItem.kernelStackSize
                    coreItem.stackRamSize = int(stackRamSize)
                    coreItem.lowestTaskStackAddress = int(estackAddress)
                    coreItem.kernelHighAddress = hex(coreItem.kernelHighAddress)
                    coreItem.kernelLowAddress = hex(coreItem.kernelLowAddress)

        tempChunks = []

        for memory in mcuCfg['memory']:
            memoryName = mcuCfg['memory'][memory]['name']
            memorySize = int(mcuCfg['memory'][memory]['size'])
            memoryLowAddress = int(mcuCfg['memory'][memory]['low_address'])
            memoryCores = mcuCfg['memory'][memory]['cores']
            highAddress = (memoryLowAddress + memorySize)
            tempChunks.append(Chunk(memoryLowAddress,highAddress,memorySize))
            self.memories.append(Memory(memoryName,memorySize,memoryLowAddress,memoryCores,tempChunks[:]))
            tempChunks = []

    def updateFreeMemory(self, memoryName , size):
        lowAddress = None
        highAddress = None
        for memory in self.memories:
            if memory.name == memoryName:
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
                            newLowAddress = closestHigherNumber(chunk.lowAddress,size)
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

    def placeTasksStacks(self):
        for coreId in range(len(self.cores)):
            for task in self.tasks:
                if task.coreId == coreId:
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

    def placeThreadStacks(self):
        for coreId in range(len(self.cores)):
            for thread in self.threads:
                if thread.coreId == coreId:
                    self.cores[coreId].numOfThreads += 1
                    lowAddress,highAddress = self.updateFreeMemory(self.cores[coreId].stackMemoryName,thread.stackSize)
                    if not lowAddress or not highAddress:
                        raise ValueError("{}{}{}{}".format('Thread ',thread.name,' is too large and cannot be placed into the ',self.cores[coreId].stackMemoryName))
                    else:
                        thread.lowAddress = hex(lowAddress)
                        thread.highAddress = hex(highAddress)

    def allocateProgramMemory(self):
        for program in self.programs:
            if program.size:
                lowAddress,highAddress = self.updateFreeMemory(program.memory,program.size)
                if not lowAddress or not highAddress:
                    raise ValueError("{}{}{}{}".format('Program ',program.name,' is too large and cannot be placed into the ',program.memory))
                else:
                    program.memoryLowAddress = lowAddress
                    program.memoryHighAddress = highAddress

    def doubleBuffersInit(self):
        doubleBuffersIterator = 0
        for buffer in self.buffers:
            if buffer.isDouble:
                isInBuffersDouble = [element for element in self.buffersDouble if element.name == buffer.doubleName]
                if not len(isInBuffersDouble):
                    sameNameElements = [element for element in self.buffers if element.doubleName == buffer.doubleName]
                    if(len(sameNameElements)>2):
                        raise ValueError("{}{}{}{}".format('DoubleBuffer ',buffer.doubleName,' is referenced too many times => ',len(sameNameElements)))
                    if(len(sameNameElements)<2):
                        raise ValueError("{}{}{}".format('DoubleBuffer ',buffer.doubleName,' is referenced just once '))
                    self.buffersDouble.append(BufferDouble(doubleBuffersIterator,buffer.doubleName,sameNameElements))
                    doubleBuffersIterator+=1

    def allocateUnmappedMemory(self):
        for core in self.cores:
            if core.unmapped.size:
                lowAddress,highAddress = self.updateFreeMemory(core.unmapped.memory,core.unmapped.size)
                if not lowAddress or not highAddress:
                    raise ValueError("{}{}{}{}".format('Unmapped section for core ',core.unmapped.coreId,' is too large and cannot be placed into the ',core.unmapped.memory))
                else:
                    core.unmapped.lowAddress = lowAddress
                    core.unmapped.highAddress = highAddress

    def schedulerLastToFirstTaskTick(self):
        for core in self.cores:
            core.scheduler.lastToFistTaskTicks = core.scheduler.table[0].executionTick + (core.scheduler.hyperTick - \
                (core.scheduler.table[len(core.scheduler.table) - 1].executionTick + \
                core.programs[core.scheduler.table[len(core.scheduler.table) - 1].programId].tasks[core.scheduler.table[len(core.scheduler.table) - 1].taskId].wcet))

    def permissionCompression(self):
        tempMultidimensionalListConstructor = []
        for coreId in range(len(self.cores)):
            tempMultidimensionalListConstructor.append([])
        for buffer in self.buffers:
            buffer.compressedReadPermission = tempMultidimensionalListConstructor[:]
            buffer.compressedWritePermission = tempMultidimensionalListConstructor[:]
            buffer.compressedReadPermissionInverted = tempMultidimensionalListConstructor[:]
            buffer.compressedWritePermissionInverted = tempMultidimensionalListConstructor[:]
        for buffer in self.buffers:
            for coreId in range(len(self.cores)):
                if((len(buffer.readPermission[coreId]))):
                    buffer.readPermission[coreId].sort(key=lambda x: x.taskId, reverse=False)
                    
                    readPermissionTemp = [0] * self.getPermissionArraySize(self.cores[coreId].numOfTasks)

                    for permission in buffer.readPermission[int(coreId)]:
                        arrayIterator = self.getPermissionArrayIterator(permission.taskId)
                        readPermissionTemp[arrayIterator] = (readPermissionTemp[arrayIterator] | (1 << (permission.taskId - (self.mcu.bitWidth * arrayIterator))))

                    buffer.compressedReadPermission[coreId] = readPermissionTemp[:]

                    buffer.compressedReadPermission[coreId] = ['{0:0{1}b}'.format(element,self.mcu.bitWidth) for element in buffer.compressedReadPermission[coreId]]
                    buffer.compressedReadPermissionInverted[coreId] = [''.join('1' if x == '0' else '0' for x in element) for element in buffer.compressedReadPermission[coreId]]
                else:
                    readPermissionTemp = [0] * self.getPermissionArraySize(self.cores[coreId].numOfTasks)
                    
                    buffer.compressedReadPermission[coreId] = readPermissionTemp[:]

                    buffer.compressedReadPermission[coreId] = ['{0:0{1}b}'.format(element,self.mcu.bitWidth) for element in buffer.compressedReadPermission[coreId]]
                    buffer.compressedReadPermissionInverted[coreId] = [''.join('1' if x == '0' else '0' for x in element) for element in buffer.compressedReadPermission[coreId]]

                if((len(buffer.writePermission[coreId]))):
                    buffer.writePermission[coreId].sort(key=lambda x: x.taskId, reverse=False)

                    writePermissionTemp = [0] * self.getPermissionArraySize(self.cores[coreId].numOfTasks)

                    for permission in buffer.writePermission[int(coreId)]:
                        arrayIterator = self.getPermissionArrayIterator(permission.taskId)
                        writePermissionTemp[arrayIterator] = (writePermissionTemp[arrayIterator] | (1 << (permission.taskId - (self.mcu.bitWidth * arrayIterator))))

                    buffer.compressedWritePermission[coreId] = writePermissionTemp[:]

                    buffer.compressedWritePermission[coreId] = ['{0:0{1}b}'.format(element,self.mcu.bitWidth) for element in buffer.compressedWritePermission[coreId]]
                    buffer.compressedWritePermissionInverted[coreId] = [''.join('1' if x == '0' else '0' for x in element) for element in buffer.compressedWritePermission[coreId]]
                else:
                    writePermissionTemp = [0] * self.getPermissionArraySize(self.cores[coreId].numOfTasks)

                    buffer.compressedWritePermission[coreId] = writePermissionTemp[:]

                    buffer.compressedWritePermission[coreId] = ['{0:0{1}b}'.format(element,self.mcu.bitWidth) for element in buffer.compressedWritePermission[coreId]]
                    buffer.compressedWritePermissionInverted[coreId] = [''.join('1' if x == '0' else '0' for x in element) for element in buffer.compressedWritePermission[coreId]]

    def getPermissionArrayIterator(self, taskId):
        iterator = 0
        elementSize = 0
        while elementSize <= taskId:
            iterator+=1
            elementSize = self.mcu.bitWidth * iterator
        
        return iterator-1

    def getPermissionArraySize(self, highestTaskId):
        iterator = 0
        elementSize = 0
        while elementSize <= highestTaskId:
            iterator+=1
            elementSize = self.mcu.bitWidth * iterator
        
        return iterator

    def getMaxSysJobsTickMultiplicator(self):
        for core in self.cores:
            for sysJobGroup in core.sysJobGroups:
                currentGroupTickMultiplicator = sysJobGroup.tickMultiplicator
                if core.MaxSysJobsTickMultiplicator < currentGroupTickMultiplicator:
                    core.MaxSysJobsTickMultiplicator = currentGroupTickMultiplicator

    def initOs(self):
        maxTaskOnOneCore = 0
        for core in self.cores:
            if core.numOfTasks > maxTaskOnOneCore:
                maxTaskOnOneCore = core.numOfTasks

        self.os = Cosmos(self.cores,self.programs,self.tasks,self.buffers,self.switches,maxTaskOnOneCore,\
            len(self.cores),len(self.buffers),self.sysCalls,self.buffersDouble,self.threads)
