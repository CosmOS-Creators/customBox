from typing import List
import Generator.GeneratorCorePlugins.LogicRunner as logicRunnerPlugin
from Parser.helpers import overrides
from Parser.ConfigTypes import ConfigElement, Configuration, Subconfig
from functools import reduce

class ScheduleEntry:
    startTime = None
    task = None
    wcet = None

class SchedulerLogic(logicRunnerPlugin.logicRunner):
    @overrides(logicRunnerPlugin.logicRunner)
    def doMagic(self, config:Configuration):
        try:
            config.require(
                [
                    "cores/:coreScheduler",
                    "programs/:core",
                    "tasks/:program",
                    "tasks/:wcet",
                    "tasks/:period",
                    "scheduleTableEntries/:scheduler",
                    "scheduleTableEntries/:entryId",
                    "scheduleTableEntries/:executionTick",
                    "schedulers/:table",
                ]
            )
        except Exception as e:
            raise Exception(
                f"Initializer is missing required attribute, more info : {str(e)}"
            ) from e

        self.maxUniqueId = None

        self.cores = config.getSubconfig("cores")
        self.tasks = config.getSubconfig("tasks")
        self.schedulers = config.getSubconfig("schedulers")
        self.scheduleTableEntries = config.getSubconfig("scheduleTableEntries")

        self.clearScheduleTable()
        self.createScheduleTable()

    def lcm(self, x, y):
        tmp = x
        while (tmp % y) != 0:
            tmp += x
        return tmp

    def lcmm(self, numbers):
        return reduce(self.lcm, numbers)

    def clearScheduleTable(self):
        elementNames = []
        for element in self.scheduleTableEntries.elements.keys():
            elementNames.append(element)
        for elementName in elementNames:
            element = self.scheduleTableEntries.getElement(elementName)
            element.delete()

    def createScheduleTable(self):
        elementCounter = 0
        for core in self.cores:
            scheduleTable = list()
            hyperPeriod = self.lcmm(
                [
                    task.period
                    for task in self.tasks
                    if task.period and task.program.core == core
                ]
            )
            core.schedulers[0].hyperTick = hyperPeriod
            for task in self.tasks:
                if task.program.core == core and task.period:
                    for startTime in range(0, task.period - 1):
                        foundStartTime = False
                        tmpStartTime = startTime
                        while tmpStartTime < hyperPeriod - 1:
                            tmpStartTime = tmpStartTime
                            isElement = [
                                entry
                                for entry in scheduleTable
                                if (
                                    (
                                        entry.startTime
                                        < ((tmpStartTime + task.wcet) % hyperPeriod)
                                    )
                                    and (
                                        ((entry.startTime + entry.wcet) % hyperPeriod)
                                        > tmpStartTime
                                    )
                                )
                            ]
                            if isElement:
                                foundStartTime = False
                                break
                            else:
                                tmpStartTime += task.period
                                foundStartTime = True
                        if foundStartTime:
                            tmpStartTime = startTime
                            while tmpStartTime < hyperPeriod - 1:
                                entryTmp = ScheduleEntry()
                                entryTmp.startTime = tmpStartTime
                                entryTmp.task = task
                                entryTmp.wcet = task.wcet
                                scheduleTable.append(entryTmp)

                                newElement = self.scheduleTableEntries.createElement(f"element_{elementCounter}")
                                newElement.executionTick = tmpStartTime
                                newElement.getAttributeInstance("scheduler").populate(task.program.core.schedulers[0], False)
                                newElement.getAttributeInstance("task").populate(task, False)
                                elementCounter += 1

                                tmpStartTime += task.period
                            break
                    if not foundStartTime:
                        print("THE SCHEDULE TABLE COMBINATION CANNOT BE FOUND")
            scheduleTable = scheduleTable
