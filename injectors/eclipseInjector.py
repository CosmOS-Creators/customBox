import json

import os
import re
import json
import argparse
from jinja2 import Template
from itertools import zip_longest

import sys
sys.path.append('Cosmos/CustomBox/shared')

from compiler import Compiler
from workspace import Workspace


LINE = "----------------------------------------------------------------------\n"
flagLineTemplate = "									<listOptionValue builtIn=\"false\" value=\"{{flag}}\"/>{{\"\n\"}}"
defineLineTemplate = "									<listOptionValue builtIn=\"false\" value=\"{{define}}\"/>{{\"\n\"}}"
sourceLineTemplate = "						<entry flags=\"VALUE_WORKSPACE_PATH|RESOLVED\" kind=\"sourcePath\" name=\"{{sourcePath}}\"/>{{\"\n\"}}"
includeLineTemplate = "									<listOptionValue builtIn=\"false\" value=\"{{pathToUnit}}/inc\"/>{{\"\n\"}}"
includeLineMulticoreTemplate = "									<listOptionValue builtIn=\"false\" value=\"../../{{pathToUnit}}/inc\"/>{{\"\n\"}}"
linkedResourcesMultilineTemplate = "		<link>{{\"\n\"}}			<name>{{sourcePath}}</name>{{\"\n\"}}			<type>2</type>{{\"\n\"}}\
    		<locationURI>$%7BPARENT-1-PROJECT_LOC%7D/{{sourcePath}}</locationURI>{{\"\n\"}}		</link>{{\"\n\"}}"

linkedResourcesMultilineFoundTemplate = "			<name>{{sourcePath}}</name>{{\"\n\"}}			<type>2</type>{{\"\n\"}}\
    		<locationURI>$%7BPARENT-1-PROJECT_LOC%7D/{{sourcePath}}</locationURI>{{\"\n\"}}"

regexStartName = re.compile(r"<name>")
regexStartFlags = re.compile(r"stringList\">")
regexStartDefs = re.compile(r"definedSymbols\">")
regexStartSource = re.compile(r"<sourceEntries>")
regexStartLocationUri = re.compile(r"<locationURI>")
regexStartIncludePaths = re.compile(r"includePath\">")
regexStartLinkedResources = re.compile(r"<linkedResources>")

regexEndOfSection = re.compile(r"</option>")
regexEndOfSource = re.compile(r"</sourceEntries>")
regexEndOfLinkedResources = re.compile(r"</linkedResources>")


def injectConfig(workspace,compilerCfg):

    if ( len(compilerCfg.cores) != len(workspace.cprojectPaths) ):
        raise ValueError('Number of cores in compilerCfg.json is not equal to the cprojectPaths in workspace.json')

    defTemplateInstance = Template(defineLineTemplate)
    flagTemplateInstance = Template(flagLineTemplate)
    sourceTemplateInstance = Template(sourceLineTemplate)
    linkedResourcesTemplateInstance = Template(linkedResourcesMultilineTemplate)
    linkedResourcesFoundTemplateInstance = Template(linkedResourcesMultilineFoundTemplate)

    if (len(compilerCfg.cores) > 1): #multicore project
        incTemplateInstance = Template(includeLineMulticoreTemplate)
    else:
        incTemplateInstance = Template(includeLineTemplate)

    #inject cproject files
    for cprojectPath in workspace.cprojectPaths:

        startDefsSection = False
        startFlagsSection = False
        startSourcesSection = False
        startIncludesSection = False

        cprojectDir = os.path.dirname(cprojectPath)
        currentCompilerCfg = None

        if (len(compilerCfg.cores) > 1): #multicore project
            for coreCompilerCfg in compilerCfg.cores:
                if ( cprojectDir == compilerCfg.cores[coreCompilerCfg]['name'] ):
                    currentCompilerCfg = compilerCfg.cores[coreCompilerCfg]
        else:
            for coreCompilerCfg in compilerCfg.cores:
                currentCompilerCfg = compilerCfg.cores[coreCompilerCfg]

        inputFile = open(cprojectPath, 'r').readlines()
        writeFile = open(cprojectPath,'w')

        print("{}{}{}{}".format(LINE, "-> Injecting ", cprojectPath, " defines"))
        #inject defines
        for line in inputFile:
            
            if (startDefsSection and re.search(regexEndOfSection, line)):
                for define in currentCompilerCfg['defines']:
                    newDefLine = defTemplateInstance.render(define = define)
                    writeFile.write(newDefLine)
                writeFile.write(line)
                startDefsSection = False
            elif (startDefsSection):
                matchDefine = False
                for define in currentCompilerCfg['defines']:
                    if ( (re.search(define, line)) ):
                        matchDefine = True 
                if (not(matchDefine)):
                    writeFile.write(line)
            else:
                writeFile.write(line)

            if (re.search(regexStartDefs, line)):
                startDefsSection = True

        writeFile.close()

        inputFile = open(cprojectPath, 'r').readlines()
        writeFile = open(cprojectPath,'w')

        print("{}{}{}{}".format(LINE, "-> Injecting ", cprojectPath, " flags"))
        #inject flags
        for line in inputFile:
            
            if (startFlagsSection and re.search(regexEndOfSection, line)):
                for flag in currentCompilerCfg['flags']:
                    newDefLine = flagTemplateInstance.render(flag = flag)
                    writeFile.write(newDefLine)
                writeFile.write(line)
                startFlagsSection = False
            elif (startFlagsSection):
                matchDefine = False
                for flag in currentCompilerCfg['flags']:
                    if ( (re.search(flag, line)) ):
                        matchDefine = True 
                if (not(matchDefine)):
                    writeFile.write(line)
            else:
                writeFile.write(line)

            if (re.search(regexStartFlags, line)):
                startFlagsSection = True

        writeFile.close()

        if ( startFlagsSection ):
            raise ValueError('The flags section in the .cproject file was not found, \
                please add dummy flags in STM Cube IDE and run stmInjector again')

        inputFile = open(cprojectPath, 'r').readlines()
        writeFile = open(cprojectPath,'w')

        print("{}{}{}{}".format(LINE, "-> Injecting ", cprojectPath, " includes"))
        #inject includes
        for line in inputFile:
            if (startIncludesSection and re.search(regexEndOfSection, line)):
                for unit in workspace.CosmOSCoreModules:
                    newDefLine = incTemplateInstance.render(pathToUnit = "{}/{}".format(workspace.CosmOSCorePath,unit))
                    writeFile.write(newDefLine)
                for unit in workspace.CosmOSGeneratedCoreModules:
                    newDefLine = incTemplateInstance.render(pathToUnit = "{}/{}".format(workspace.CosmOSGeneratedCorePath,unit))
                    writeFile.write(newDefLine)
                newDefLine = incTemplateInstance.render(pathToUnit = workspace.CosmOSIntegrationLayerPath)
                writeFile.write(newDefLine)
                newDefLine = incTemplateInstance.render(pathToUnit = workspace.CosmOSApplicationLayerPath)
                writeFile.write(newDefLine)
                writeFile.write(line)
                startIncludesSection = False
            elif (startIncludesSection):
                matchDefine = False
                for unit,generatedUnit in zip_longest(workspace.CosmOSCoreModules,workspace.CosmOSGeneratedCoreModules):
                    if ((re.search("{}/{}".format(workspace.CosmOSCorePath,unit), line)) or \
                        (re.search(workspace.CosmOSIntegrationLayerPath, line)) or \
                        (re.search(workspace.CosmOSApplicationLayerPath, line)) or \
                        (re.search("{}/{}".format(workspace.CosmOSGeneratedCorePath,generatedUnit), line))):
                        matchDefine = True 
                if (not(matchDefine)):
                    writeFile.write(line)
            else:
                writeFile.write(line)

            if (re.search(regexStartIncludePaths, line)):
                startIncludesSection = True

        writeFile.close()

        inputFile = open(cprojectPath, 'r').readlines()
        writeFile = open(cprojectPath,'w')

        print("{}{}{}{}".format(LINE, "-> Injecting ", cprojectPath, " sources"))
        #inject sources
        for line in inputFile:
            
            if (startSourcesSection and re.search(regexEndOfSource, line)):
                newDefLine = sourceTemplateInstance.render(sourcePath = workspace.CosmOSIntegrationLayerPath)
                writeFile.write(newDefLine)
                newDefLine = sourceTemplateInstance.render(sourcePath = workspace.CosmOSApplicationLayerPath)
                writeFile.write(newDefLine)
                newDefLine = sourceTemplateInstance.render(sourcePath = workspace.CosmOSCorePath)
                writeFile.write(newDefLine)
                newDefLine = sourceTemplateInstance.render(sourcePath = workspace.CosmOSGeneratedCorePath)
                writeFile.write(newDefLine)
                writeFile.write(line)
                startSourcesSection = False
            elif (startSourcesSection):
                matchDefine = False
                if ((re.search(workspace.CosmOSCorePath, line)) or \
                    (re.search(workspace.CosmOSGeneratedCorePath, line)) or \
                    (re.search(workspace.CosmOSApplicationLayerPath, line)) or \
                    (re.search(workspace.CosmOSIntegrationLayerPath, line))):
                    matchDefine = True 
                if (not(matchDefine)):
                    writeFile.write(line)
            else:
                writeFile.write(line)

            if (re.search(regexStartSource, line)):
                startSourcesSection = True

        writeFile.close()

    if (len(compilerCfg.cores) > 1): #multicore project
        for projectPath in workspace.projectPaths:

            startLinkedResourcesSection = False
            startNameSection = False
            startUriSection = False

            inputFile = open(projectPath, 'r').readlines()
            writeFile = open(projectPath,'w')

            cachedLines = []
            matchNameCorePath = False
            matchNameGeneratedCorePath = False
            matchNameAL = False
            matchNameCIL = False
            matchUriCorePath = False
            matchUriGeneratedCorePath = False
            matchUriAL = False
            matchUriCIL = False

            corePathIsLinked = False
            generatedCorePathIsLinked = False
            CILPathIsLinked = False
            ALPathIsLinked = False

            print("{}{}{}{}".format(LINE, "-> Injecting ", projectPath, " linked resources"))
            #inject linkedResources
            for line in inputFile:

                if (startLinkedResourcesSection and re.search(regexEndOfLinkedResources, line)):
                    startLinkedResourcesSection = False
                    if( not(corePathIsLinked) ):
                        newDefLine = linkedResourcesTemplateInstance.render(sourcePath = workspace.CosmOSCorePath)
                        writeFile.write(newDefLine)
                    if( not(generatedCorePathIsLinked) ):
                        newDefLine = linkedResourcesTemplateInstance.render(sourcePath = workspace.CosmOSGeneratedCorePath)
                        writeFile.write(newDefLine)
                    if( not(ALPathIsLinked) ):
                        newDefLine = linkedResourcesTemplateInstance.render(sourcePath = workspace.CosmOSApplicationLayerPath)
                        writeFile.write(newDefLine)
                    if( not(CILPathIsLinked) ):
                        newDefLine = linkedResourcesTemplateInstance.render(sourcePath = workspace.CosmOSIntegrationLayerPath)
                        writeFile.write(newDefLine)
                    writeFile.write(line)
                elif ( startLinkedResourcesSection ):
                    
                    if ( re.search(regexStartName, line) ):
                        startNameSection = True
                        startUriSection = False
                        if ( re.search(workspace.CosmOSCorePath, line) ):
                            matchNameCorePath = True
                        elif ( re.search(workspace.CosmOSGeneratedCorePath, line) ):
                            matchNameGeneratedCorePath = True
                        elif( re.search(workspace.CosmOSApplicationLayerPath, line) ):
                            matchNameAL = True 
                        elif( re.search(workspace.CosmOSIntegrationLayerPath, line) ):
                            matchNameCIL = True 

                    if ( re.search(regexStartLocationUri, line) ):
                        startUriSection = True
                        if ( re.search(workspace.CosmOSCorePath, line) ):
                            matchUriCorePath = True
                        elif ( re.search(workspace.CosmOSGeneratedCorePath, line) ):
                            matchUriGeneratedCorePath = True
                        elif( re.search(workspace.CosmOSApplicationLayerPath, line) ):
                            matchUriAL = True 
                        elif( re.search(workspace.CosmOSIntegrationLayerPath, line) ):
                            matchUriCIL = True 

                    if ( matchNameCorePath == matchUriCorePath and matchNameCorePath):
                        corePathIsLinked = True

                    if ( matchNameGeneratedCorePath == matchUriGeneratedCorePath and matchNameGeneratedCorePath):
                        generatedCorePathIsLinked = True

                    if ( matchNameCIL == matchUriCIL and matchNameCIL):
                        CILPathIsLinked = True

                    if ( matchNameAL == matchUriAL and matchNameAL):
                        ALPathIsLinked = True

                    if(startNameSection):
                        cachedLines.append(line)
                    else :
                        writeFile.write(line)

                    if( startUriSection and matchNameCorePath != matchUriCorePath and not(corePathIsLinked)):
                        newDefLine = linkedResourcesFoundTemplateInstance.render(sourcePath = workspace.CosmOSCorePath)
                        writeFile.write(newDefLine)
                        startNameSection = False
                        corePathIsLinked = True
                        cachedLines = []
                    if( startUriSection and matchNameGeneratedCorePath != matchUriGeneratedCorePath and not(generatedCorePathIsLinked)):
                        newDefLine = linkedResourcesFoundTemplateInstance.render(sourcePath = workspace.CosmOSGeneratedCorePath)
                        writeFile.write(newDefLine)
                        startNameSection = False
                        generatedCorePathIsLinked = True
                        cachedLines = []
                    elif( startUriSection and matchNameAL != matchUriAL and not(ALPathIsLinked)):
                        newDefLine = linkedResourcesFoundTemplateInstance.render(sourcePath = workspace.CosmOSApplicationLayerPath)
                        writeFile.write(newDefLine)
                        startNameSection = False
                        ALPathIsLinked = True
                        cachedLines = []
                    elif( startUriSection and matchNameCIL != matchUriCIL and not(CILPathIsLinked)):
                        newDefLine = linkedResourcesFoundTemplateInstance.render(sourcePath = workspace.CosmOSIntegrationLayerPath)
                        writeFile.write(newDefLine)
                        startNameSection = False
                        CILPathIsLinked = True
                        cachedLines = []
                    elif( startUriSection ):
                        for oldLine in cachedLines:
                            writeFile.write(oldLine)
                        startNameSection = False
                        cachedLines = []
                else:
                    writeFile.write(line)

                if (re.search(regexStartLinkedResources, line)):
                    startLinkedResourcesSection = True

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
    workspace = Workspace(args.workspace)

    #load compiler configuration
    compilerCfg = Compiler(workspace.compilerCfgPath)

    #inject config files
    injectConfig(workspace,compilerCfg)

    print("{}{}{}".format(LINE,"-> STM CUBE IDE cproject and project files were successfully injected!\n",LINE))


if __name__ == "__main__":
    main()