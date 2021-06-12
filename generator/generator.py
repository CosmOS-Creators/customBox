import os
import re
import json
import argparse

import sys

from datetime import date
from classes.section import Section
from jinja2 import Template
from shared.workspace import Workspace
from shared.systemModel import SystemModel


LINE = "----------------------------------------------------------------------\n"

regexALStartSection = re.compile(r"start_name =")
regexALStopSection = re.compile(r"stop_name =")

def compareFiles(codePath, newFile):

    fileIsSame = True
    dateFound = False

    if(os.path.isfile(codePath)):
        with open(codePath, 'r') as oldFile:
            oldLines = oldFile.readlines()
            newLines = newFile.splitlines()

            for newLine,oldLine in zip(newLines,oldLines):
                newLine = newLine.rstrip()
                oldLine = oldLine.rstrip()
                newLineFindDate = re.search(r'@date',newLine)
                oldLineFindDate = re.search(r'@date',oldLine)

                if newLineFindDate and oldLineFindDate:
                    dateFound = True
                else:
                    if(newLine != oldLine):
                        fileIsSame = False
                        break
    else:
        fileIsSame = False

    return fileIsSame


def generateCosmOSCore(systemModel,workspace):
    fileIsSame = False

    for templateName in os.listdir(workspace.CosmOSCoreTemplatesPath):
        fileName = os.path.splitext(templateName)[0]
        templatePath = os.path.join(workspace.CosmOSCoreTemplatesPath,templateName)
        unitName = re.search(r'[^A-Z]+',fileName).group()

        if unitName == 'sys' or unitName == 'cosmos':
            unitNameAdd = re.findall(r'[A-Z][^A-Z]*', os.path.splitext(fileName)[0])[0]
            unitName = "{}{}".format(unitName,unitNameAdd)

        if re.split(r'\.',fileName)[1] == 'h':
            codePath = os.path.join(workspace.CosmOSGeneratedCorePath,unitName,"inc",fileName)
            codeDir = os.path.join(workspace.CosmOSGeneratedCorePath,unitName,"inc")

        else:
            codePath = os.path.join(workspace.CosmOSGeneratedCorePath,unitName,"src",fileName)
            codeDir = os.path.join(workspace.CosmOSGeneratedCorePath,unitName,"src")

        with open(templatePath, 'r') as templateFile:
            template=templateFile.read()

        templateInstance = Template(template)

        generatedOutput = templateInstance.render(os = systemModel.os, mcu = systemModel.mcu, tasks=systemModel.os.tasks, threads=systemModel.os.threads, \
        programs = systemModel.os.programs,cores = systemModel.os.cores,buffers = systemModel.os.buffers,switches  = systemModel.os.switches,\
            buffersDouble = systemModel.os.buffersDouble,version = systemModel.CosmOSVersion,date=date.today())

        fileIsSame = compareFiles(codePath,generatedOutput)

        if(not fileIsSame):
            if not os.path.exists(codeDir):
                os.makedirs(codeDir)
            with open(codePath, 'w+') as source:
                source.write(generatedOutput)
                print("{}{}{}{}".format(LINE, "-> ",codePath," was generated successfully"))


def generateCosmOSIntegrationLayer(systemModel,workspace):
    fileIsSame = False

def generateCosmOSApplicationLayer(systemModel,workspace):

    #generate all header files
    headerTemplatePath = os.path.join(workspace.CosmOSApplicationLayerTemplatesPath,workspace.CosmOSApplicationLayerHeaderTemplateName)
    with open(headerTemplatePath, 'r') as templateFile:
            template=templateFile.read()

    headerTemplateInstance = Template(template)

    pathToHeaderFiles = os.path.join(workspace.CosmOSApplicationLayerPath,"inc")

    headerSections = []

    if not os.path.exists(pathToHeaderFiles):
        os.makedirs(pathToHeaderFiles)
        for program in systemModel.programs:
            generatedOutput = headerTemplateInstance.render(program = program, sections = headerSections ,version = systemModel.CosmOSVersion,\
                switches  = systemModel.os.switches, date=date.today())
            headerName = "{}{}".format(program.name,".h")
            headerPath = os.path.join(pathToHeaderFiles,headerName)

            with open(headerPath, 'w+') as header:
                header.write(generatedOutput)
                print("{}{}{}{}".format(LINE, "-> ",headerPath," was generated successfully"))
    else :
        for f in os.listdir(pathToHeaderFiles):
            if f.endswith('.h'):
                inputFile = open(os.path.join(pathToHeaderFiles,f), 'r').readlines()

                name = None
                tempLines = []
                sectionStarted = False

                for line in inputFile:
                    if(re.search(regexALStopSection, line)):
                        if(name != re.split("=", line, 1)[1]):
                            raise ValueError("{}{}{}{}{}{}".format('Section ',name,' in file ',inputFile,'coherency is broken, please remove dir ',pathToHeaderFiles))
                        sectionStarted = False
                        tempLines.pop(0)
                        tempLines.pop()

                    if(sectionStarted):
                        tempLines.append(line[:-1])

                    if( re.search(regexALStartSection, line) ):
                        name = re.split("=", line, 1)[1]
                        sectionStarted = True

                os.remove(os.path.join(pathToHeaderFiles,f))
                headerSections.append(Section(name[:-1],tempLines[:]))

        for program in systemModel.programs:
            generatedOutput = headerTemplateInstance.render(program = program, sections = headerSections ,version = systemModel.CosmOSVersion, \
                switches  = systemModel.os.switches, date=date.today())
            headerName = "{}{}".format(program.name,".h")
            headerPath = os.path.join(pathToHeaderFiles,headerName)

            with open(headerPath, 'w+') as header:
                header.write(generatedOutput)
                print("{}{}{}{}".format(LINE, "-> ",headerPath," was generated successfully"))

    #generate all source files
    sourceTemplatePath = os.path.join(workspace.CosmOSApplicationLayerTemplatesPath,workspace.CosmOSApplicationLayerSourceTemplateName)
    with open(sourceTemplatePath, 'r') as templateFile:
            template=templateFile.read()

    sourceTemplateInstance = Template(template)

    pathToSourceFiles = os.path.join(workspace.CosmOSApplicationLayerPath,"src")

    sourceSections = []

    if not os.path.exists(pathToSourceFiles):
        os.makedirs(pathToSourceFiles)
        for program in systemModel.programs:
            generatedOutput = sourceTemplateInstance.render(program = program, sections = sourceSections ,version = systemModel.CosmOSVersion, \
                switches  = systemModel.os.switches, date=date.today())
            sourceName = "{}{}".format(program.name,".c")
            sourcePath = os.path.join(pathToSourceFiles,sourceName)

            with open(sourcePath, 'w+') as source:
                source.write(generatedOutput)
                print("{}{}{}{}".format(LINE, "-> ",sourcePath," was generated successfully"))
    else :
        for f in os.listdir(pathToSourceFiles):
            if f.endswith('.c'):
                inputFile = open(os.path.join(pathToSourceFiles,f), 'r').readlines()

                name = None
                tempLines = []
                sectionStarted = False

                for line in inputFile:
                    if(re.search(regexALStopSection, line)):
                        if(name != re.split("=", line, 1)[1]):
                            raise ValueError("{}{}{}{}{}{}".format('Section ',name,' in file ',inputFile,'coherency is broken, please remove dir ',pathToSourceFiles))
                        sectionStarted = False
                        tempLines.pop(0)
                        tempLines.pop()
                        sourceSections.append(Section(name[:-1],tempLines[:]))
                        tempLines = []

                    if(sectionStarted):
                        tempLines.append(line[:-1])

                    if( re.search(regexALStartSection, line) ):
                        name = re.split("=", line, 1)[1]
                        sectionStarted = True

                os.remove(os.path.join(pathToSourceFiles,f))

        for program in systemModel.programs:
            generatedOutput = sourceTemplateInstance.render(program = program, sections = sourceSections ,version = systemModel.CosmOSVersion, \
                switches  = systemModel.os.switches, date=date.today())
            sourceName = "{}{}".format(program.name,".c")
            sourcePath = os.path.join(pathToSourceFiles,sourceName)

            with open(sourcePath, 'w+') as source:
                source.write(generatedOutput)
                print("{}{}{}{}".format(LINE, "-> ",sourcePath," was generated successfully"))

def generateLinkerScript(systemModel,workspace):
    fileIsSame = False

    for core,linkerScriptPath in zip(systemModel.cores,workspace.linkerScriptPaths):
        templatePath = os.path.join(workspace.LinkerScriptTemplatePath,workspace.LinkerTemplateName)

        with open(templatePath, 'r') as templateFile:
            template=templateFile.read()

        templateInstance = Template(template)

        outputDirectory = os.path.dirname(linkerScriptPath)

        if not os.path.exists(outputDirectory):
            os.mkdir(outputDirectory)

        generatedOutput = templateInstance.render(os = systemModel.os, mcu = systemModel.mcu, tasks=systemModel.os.tasks, \
        programs = systemModel.os.programs,core = core,version = systemModel.CosmOSVersion,date=date.today())

        fileIsSame = compareFiles(linkerScriptPath,generatedOutput)

        if(not fileIsSame):
            with open(linkerScriptPath, 'w+') as source:
                source.write(generatedOutput)
                print("{}{}{}{}".format(LINE, "-> ",linkerScriptPath," was generated successfully"))

def generateCode(systemModel,workspace):

    print("{}{}".format(LINE, "-> Generating the CosmOS Core code"))
    generateCosmOSCore(systemModel,workspace)
    #print("{}{}".format(LINE, "-> Generating the CosmOS Integration Layer code"))
    #generateCosmOSIntegrationLayer(systemModel,workspace)
    print("{}{}".format(LINE, "-> Generating the CosmOS Application Layer code"))
    generateCosmOSApplicationLayer(systemModel,workspace)
    print("{}{}".format(LINE, "-> Generating the Linker Scripts"))
    generateLinkerScript(systemModel,workspace)



def main():
    my_parser = argparse.ArgumentParser()
    my_parser.add_argument('-w',
                        '--workspace',
                        type = str,
                        action = 'store',
                        dest='workspace',
                        help='Path to the workspace.json',
                        required = True)

    args = my_parser.parse_args()

    #load workspace
    print("{}{}{}".format(LINE, "-> Parsing workspace with path ", args.workspace))
    workspace = Workspace(args.workspace)

    #load systemModel
    print("{}{}".format(LINE, "-> Parsing System model and MCU configuration"))
    systemModel = SystemModel(workspace.systemModelCfgPath,workspace.mcuCfgPath)

    #generate code
    generateCode(systemModel,workspace)
    print("{}{}{}".format(LINE,"-> The CosmOS code was successfully generated!\n",LINE))


if __name__ == "__main__":
    main()