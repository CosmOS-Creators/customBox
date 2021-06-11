import json
import importlib.util
import sys

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
from route import Route
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
        self.routes = []

        self.routesApiHeaders = []
        self.sysJobsApiHeaders = []

        self.switches = None
        self.mcu = None
        self.os = None
        self.CosmOSVersion = None

        self.systemModelCfg = paramSystemModelCfgPath
        self.mcuCfg = paramMcuCfgPath

        self.constsLowAddress = None
        self.constsSize = None
        self.varsLowAddress = None
        self.varsSize = None

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
        self.removeDuplicateRoutesApiHeaders()
        self.removeDuplicateSysJobsApiHeaders()
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
        routes = []

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
                    isIdle = systemModelCfg['cores'][core]['programs'][program]['tasks'][task]['isIdle']
                    isSysJob = systemModelCfg['cores'][core]['programs'][program]['tasks'][task]['isSysJob']
                    tasksTemp.append(Task(taskName,int(wcet),period,coreIterator,programIterator,taskIterator,taskStackIterator,\
                        int(taskStackSize),floatingPoint,schedulableIterator,isIdle,isSysJob))
                    taskStackIterator+=1
                    taskIterator+=1
                    schedulableIterator+=1
                for thread in systemModelCfg['cores'][core]['programs'][program]['threads']:
                    threadName = systemModelCfg['cores'][core]['programs'][program]['threads'][thread]['name']
                    threadStackSize = systemModelCfg['cores'][core]['programs'][program]['threads'][thread]['stack']['size']
                    floatingPoint = systemModelCfg['cores'][core]['programs'][program]['threads'][thread]['floatingPoint']
                    isIdle = systemModelCfg['cores'][core]['programs'][program]['threads'][thread]['isIdle']
                    isSysJob = False
                    threadsTemp.append(Thread(threadName,coreIterator,programIterator,threadIterator,threadStackIterator,\
                        int(threadStackSize),floatingPoint,schedulableIterator,isIdle,isSysJob))
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
            for sysJobGroup in systemModelCfg['cores'][core]['sysJobs']['groups']:
                handlers = systemModelCfg['cores'][core]['sysJobs']['groups'][sysJobGroup]['handlers']
                tickMultiplicator = int(systemModelCfg['cores'][core]['sysJobs']['groups'][sysJobGroup]['tickMultiplicator'])
                apiHeaders = systemModelCfg['cores'][core]['sysJobs']['groups'][sysJobGroup]['api_headers']
                sysJobGroupsTemp.append(SysJobGroup(sysJobGroupIterator,coreIterator,handlers,tickMultiplicator,apiHeaders))
                sysJobGroupIterator+=1
            sysJobGroupIterator = 0

            schedulerHyperTick = systemModelCfg['cores'][core]['scheduler']['hyperTick']
            sysJobsHyperTick = systemModelCfg['cores'][core]['sysJobs']['hyperTick']
            syncTicks = systemModelCfg['cores'][core]['scheduler']['syncTicks']
            firstSyncTaskStartTick = systemModelCfg['cores'][core]['scheduler']['firstSyncTaskStartTick']
            preemptTick = systemModelCfg['cores'][core]['scheduler']['preemptTick']
            unmappedSize = int(systemModelCfg['cores'][core]['unmapped']['size'])
            unmappedMemory = systemModelCfg['cores'][core]['unmapped']['memory']

            cores.append(Core(coreName,programsTemp,coreIterator,\
                Scheduler(int(schedulerHyperTick),tableTemp,coreIterator,len(tableTemp),syncTicks,firstSyncTaskStartTick,preemptTick),\
                Unmapped(unmappedSize,unmappedMemory,coreIterator),\
                bootOs,\
                sysJobGroupsTemp, sysJobsHyperTick))
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
            for element in systemModelCfg['buffers'][buffer]['tasksReadPermissions']:
                coreId = int(systemModelCfg['buffers'][buffer]['tasksReadPermissions'][element]['core'])
                programId = int(systemModelCfg['buffers'][buffer]['tasksReadPermissions'][element]['program'])
                taskId = int(systemModelCfg['buffers'][buffer]['tasksReadPermissions'][element]['task'])
                schedulableId = self.getTaskSchedulableId(tasks,taskId,programId,coreId)
                readPermissionCoreGroupsTemp[coreId].append(Permission(coreId,programId,schedulableId))
            for element in systemModelCfg['buffers'][buffer]['tasksWritePermissions']:
                coreId = int(systemModelCfg['buffers'][buffer]['tasksWritePermissions'][element]['core'])
                programId = int(systemModelCfg['buffers'][buffer]['tasksWritePermissions'][element]['program'])
                taskId = int(systemModelCfg['buffers'][buffer]['tasksWritePermissions'][element]['task'])
                schedulableId = self.getTaskSchedulableId(tasks,taskId,programId,coreId)
                writePermissionCoreGroupsTemp[coreId].append(Permission(coreId,programId,schedulableId))
            for element in systemModelCfg['buffers'][buffer]['threadsReadPermissions']:
                coreId = int(systemModelCfg['buffers'][buffer]['threadsReadPermissions'][element]['core'])
                programId = int(systemModelCfg['buffers'][buffer]['threadsReadPermissions'][element]['program'])
                threadId = int(systemModelCfg['buffers'][buffer]['threadsReadPermissions'][element]['thread'])
                schedulableId = self.getThreadSchedulableId(threads,threadId,programId,coreId)
                readPermissionCoreGroupsTemp[coreId].append(Permission(coreId,programId,schedulableId))
            for element in systemModelCfg['buffers'][buffer]['threadsWritePermissions']:
                coreId = int(systemModelCfg['buffers'][buffer]['threadsWritePermissions'][element]['core'])
                programId = int(systemModelCfg['buffers'][buffer]['threadsWritePermissions'][element]['program'])
                threadId = int(systemModelCfg['buffers'][buffer]['threadsWritePermissions'][element]['thread'])
                schedulableId = self.getThreadSchedulableId(threads,threadId,programId,coreId)
                writePermissionCoreGroupsTemp[coreId].append(Permission(coreId,programId,schedulableId))
            currentBuffer = Buffer(bufferIterator,bufferName,readPermissionCoreGroupsTemp[:],writePermissionCoreGroupsTemp[:],bufferSize,bufferIsDouble)
            if bufferIsDouble :
                currentBuffer.doubleName = bufferIsDouble = systemModelCfg['buffers'][buffer]['double']['name']
            buffers.append(currentBuffer)
            bufferIterator+=1
            for iterator in range(coreIterator):
                readPermissionCoreGroupsTemp[iterator] = []
                writePermissionCoreGroupsTemp[iterator] = []

        for route in systemModelCfg['sysCalls']['routed_funcs']:
            name = systemModelCfg['sysCalls']['routed_funcs'][route]['name']
            apiHeader = systemModelCfg['sysCalls']['routed_funcs'][route]['api_header']
            sysCall = systemModelCfg['sysCalls']['routed_funcs'][route]['sysCall']
            userVisible = systemModelCfg['sysCalls']['routed_funcs'][route]['user_visible']
            isMappedToEntity = systemModelCfg['sysCalls']['routed_funcs'][route]['is_mapped_to_entity']
            args = systemModelCfg['sysCalls']['routed_funcs'][route]['args']
            returnType = systemModelCfg['sysCalls']['routed_funcs'][route]['return_type']
            currentRoute = Route(name,apiHeader,sysCall,userVisible,isMappedToEntity,args,returnType)
            routes.append(currentRoute)

        self.cores = cores
        self.programs = programs
        self.tasks = tasks
        self.threads = threads
        self.buffers = buffers
        self.routes = routes
        self.switches = Switch( systemModelCfg['switches']['memoryProtection'],\
                                systemModelCfg['switches']['coreSync'],\
                                systemModelCfg['switches']['performanceScheduling'])

    def parseMcuCfg(self):

        with open(self.mcuCfg, 'r') as myfile:
            data = myfile.read()

        mcuCfg = json.loads(data)

        name = mcuCfg['mcu']['name']
        bitWidth = int(mcuCfg['mcu']['bitWidth'])

        self.mcu = Mcu(name,bitWidth)

        for core in mcuCfg['cores']:
            coreName = mcuCfg['cores'][core]['name']
            estackAddress = mcuCfg['cores'][core]['stack_memory_partition']['e_stack_address']
            stackRamSize = mcuCfg['cores'][core]['stack_memory_partition']['stack_ram_size']
            stackMemory = mcuCfg['cores'][core]['stack_memory_partition']['name']
            flashLowAddress = mcuCfg['cores'][core]['flash_partition']['low_address']
            flashSize = mcuCfg['cores'][core]['flash_partition']['size']
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
                    coreItem.flashLowAddress = hex(int(flashLowAddress))
                    coreItem.flashSize = hex(int(flashSize))

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

        self.constsLowAddress = hex(int(mcuCfg['os_memory_sections']['consts_partition']['low_address']))
        self.constsSize = hex(int(mcuCfg['os_memory_sections']['consts_partition']['size']))
        self.varsLowAddress = hex(int(mcuCfg['os_memory_sections']['vars_partition']['low_address']))
        self.varsSize = hex(int(mcuCfg['os_memory_sections']['vars_partition']['size']))

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
                    buffer.readPermission[coreId].sort(key=lambda x: x.schedulableId, reverse=False)

                    readPermissionTemp = [0] * self.getPermissionArraySize(self.cores[coreId].numOfTasks)

                    for permission in buffer.readPermission[int(coreId)]:
                        arrayIterator = self.getPermissionArrayIterator(permission.schedulableId)
                        readPermissionTemp[arrayIterator] = (readPermissionTemp[arrayIterator] | (1 << (permission.schedulableId - (self.mcu.bitWidth * arrayIterator))))

                    buffer.compressedReadPermission[coreId] = readPermissionTemp[:]

                    buffer.compressedReadPermission[coreId] = ['{0:0{1}b}'.format(element,self.mcu.bitWidth) for element in buffer.compressedReadPermission[coreId]]
                    buffer.compressedReadPermissionInverted[coreId] = [''.join('1' if x == '0' else '0' for x in element) for element in buffer.compressedReadPermission[coreId]]
                else:
                    readPermissionTemp = [0] * self.getPermissionArraySize(self.cores[coreId].numOfTasks)

                    buffer.compressedReadPermission[coreId] = readPermissionTemp[:]

                    buffer.compressedReadPermission[coreId] = ['{0:0{1}b}'.format(element,self.mcu.bitWidth) for element in buffer.compressedReadPermission[coreId]]
                    buffer.compressedReadPermissionInverted[coreId] = [''.join('1' if x == '0' else '0' for x in element) for element in buffer.compressedReadPermission[coreId]]

                if((len(buffer.writePermission[coreId]))):
                    buffer.writePermission[coreId].sort(key=lambda x: x.schedulableId, reverse=False)

                    writePermissionTemp = [0] * self.getPermissionArraySize(self.cores[coreId].numOfTasks)

                    for permission in buffer.writePermission[int(coreId)]:
                        arrayIterator = self.getPermissionArrayIterator(permission.schedulableId)
                        writePermissionTemp[arrayIterator] = (writePermissionTemp[arrayIterator] | (1 << (permission.schedulableId - (self.mcu.bitWidth * arrayIterator))))

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

    def removeDuplicateRoutesApiHeaders(self):
        for route in self.routes:
            routesApiHeadersSet = set(self.routesApiHeaders)
            if not route.apiHeader in routesApiHeadersSet:
                self.routesApiHeaders.append(route.apiHeader)

    def removeDuplicateSysJobsApiHeaders(self):
        for core in self.cores:
            for sysJobsGroup in core.sysJobGroups:
                for apiHeader in sysJobsGroup.apiHeaders:
                    sysJobsApiHeadersSet = set(self.sysJobsApiHeaders)
                    if not apiHeader in sysJobsApiHeadersSet:
                        self.sysJobsApiHeaders.append(apiHeader)

    def getTaskSchedulableId(self,tasks,taskId,programId,coreId):
        for task in tasks:
            if (task.taskId == taskId) and (task.programId == programId) and (task.coreId == coreId):
                return task.schedulableId

    def getThreadSchedulableId(self,threads,threadId,programId,coreId):
        for thread in threads:
            if (thread.threadId == threadId) and (thread.programId == programId) and (thread.coreId == coreId):
                return thread.schedulableId

    def initOs(self):
        maxSchedulablesOnOneCore = 0
        for core in self.cores:
            if (core.numOfTasks +  core.numOfThreads) > maxSchedulablesOnOneCore:
                maxSchedulablesOnOneCore = (core.numOfTasks +  core.numOfThreads)

        self.os = Cosmos(self.cores,self.programs,self.tasks,self.buffers,self.switches,maxSchedulablesOnOneCore,\
            len(self.cores),len(self.buffers),self.routes,self.buffersDouble,self.threads,\
            self.routesApiHeaders,self.sysJobsApiHeaders,self.constsLowAddress,self.constsSize,self.varsLowAddress,self.constsSize)
