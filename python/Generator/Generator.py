import json
import os
import jinja2
from pathlib import Path
from typing import Dict, List, Union
import Parser
import Parser.helpers as helpers
import Parser.ConfigTypes as configTypes
import Generator.GeneratorPluginSkeleton as GeneratorPlugins

templateExtension = ".j2"

TEMPLATES_KEY = "templates"
OUTPUT_DIR_KEY = "outputDir"
LOOP_KEY = "loop"
FILE_NAME_KEY = "fileName"
TARGET_KEY = "target"
PATTERN_KEY = "pattern"

TARGET_PLACEHOLDER = "{target}"
TEMPLATE_PLACEHOLDER = "{template}"

mandatoryKeys = [TEMPLATES_KEY, OUTPUT_DIR_KEY]

__version__ = "2.0.0"


class generationElement:
    __outputPath = ""
    __templates = []
    __loopElements = None
    __specialOutName = None
    __targetConfig = None
    __targetName = None
    __pattern = None
    __preFileGenHook = None
    __postFileGenHook = None

    def __init__(self, outPath: Path, templateFiles: List[Union[str, Path]]):
        self.__outputPath = outPath
        self.__templates = templateFiles

    def addLoop(self, loopConfigTarget: str, config: configTypes.Configuration):
        config.require(loopConfigTarget)
        Link = Parser.Link(loopConfigTarget)
        self.__loopElements = Link.resolve(config)
        self.__targetConfig = Link.config
        return len(self.__loopElements)

    def setOutName(self, name: str):
        self.__specialOutName = name

    def setTargetName(self, name: str):
        self.__targetName = name

    def setPattern(self, pattern: dict):
        self.__pattern = pattern

    def registerPreFileGenHook(self, hook):
        self.__preFileGenHook = hook

    def registerPostFileGenHook(self, hook):
        self.__postFileGenHook = hook

    def registerHooks(self, preFileGenHook, postFileGenHook):
        self.registerPreFileGenHook(preFileGenHook)
        self.registerPostFileGenHook(postFileGenHook)

    def injectTemplates(
        self,
        config: Dict[str, configTypes.Configuration],
        fileNamePattern: str,
        outputPath: Path,
    ):
        generatedFiles = []
        for template in self.__templates:
            templateName = Path(template).stem
            temp = Path(templateName)
            outFileSuffix = temp.suffix
            if fileNamePattern is None:
                outFileName = temp.stem
            else:
                outFileName = Path(
                    fileNamePattern.replace(TEMPLATE_PLACEHOLDER, templateName)
                ).stem

            outputFilePath = Path.joinpath(outputPath, outFileName + outFileSuffix)
            config["filename"] = outFileName + outFileSuffix
            if not self.__pattern is None:
                for pattern in self.__pattern:
                    if pattern in outFileSuffix:
                        outputDir = Path.joinpath(outputPath, self.__pattern[pattern])
                        outputFilePath = outputDir.joinpath(outFileName + outFileSuffix)
                        if not outputDir.exists():
                            outputDir.mkdir(parents=True)
                        break

            with open(template, "r") as template:
                templateContent = template.read()
            jinjaTemplate = jinja2.Template(
                templateContent, undefined=jinja2.StrictUndefined
            )
            if self.__preFileGenHook:
                self.__preFileGenHook(config, config["model"], outputFilePath)
            try:
                renderedFile = jinjaTemplate.render(config)
            except Exception as e:
                raise Exception(
                    f'Error while rendering template "{str(template.name)}" to file "{outputFilePath}": {str(e)}'
                ) from e
            generateFile = True
            if self.__postFileGenHook:
                generateFile = self.__postFileGenHook(outputFilePath, renderedFile)
            if generateFile == True:
                with open(outputFilePath, "w") as file:
                    file.write(renderedFile)
            generatedFiles.append(outputFilePath)
        return generatedFiles

    def generate(self, config: configTypes.Configuration):
        configDict = {"model": config, "version": __version__}
        generatedFiles = []
        if self.__loopElements is None:
            if not self.__specialOutName is None:
                if TARGET_PLACEHOLDER in self.__specialOutName:
                    raise AttributeError(
                        f'The value for the key "{FILE_NAME_KEY}" included a placeholder for the target name but no loop property was defined. This is an invalid combination'
                    )
            if TARGET_PLACEHOLDER in str(self.__outputPath):
                raise AttributeError(
                    f'The value for the key "{OUTPUT_DIR_KEY}"" included a placeholder for the target name but no loop property was defined. This is an invalid combination'
                )
            generatedFiles += self.injectTemplates(
                configDict, self.__specialOutName, self.__outputPath
            )
        else:
            if not self.__targetConfig is None:
                link = Parser.Link.construct(config=self.__targetConfig)
                config.require(link)
                configDict[self.__targetConfig] = link.resolve(config)
            for attribDef, element in self.__loopElements:
                filename = self.__specialOutName
                if not self.__targetName is None:
                    configDict[self.__targetName] = element
                targetValue = attribDef.value
                if not filename is None:
                    filename = filename.replace(TARGET_PLACEHOLDER, targetValue)
                outPath = self.__outputPath
                outPath_str = str(self.__outputPath)
                if TARGET_PLACEHOLDER in outPath_str:
                    outPath = Path(outPath_str.replace(TARGET_PLACEHOLDER, targetValue))
                if not outPath.exists():
                    outPath.mkdir(parents=True)
                generatedFiles += self.injectTemplates(configDict, filename, outPath)
        return generatedFiles


class Generator:
    __pluginList: List[GeneratorPlugins.GeneratorPlugin] = []

    def __init__(self, workspace: Parser.Workspace):
        try:
            workspace.requireFolder(["config", "TemplateDir"])
            workspace.requireFile(["GeneratorConfig"])
        except AttributeError as e:
            raise AttributeError(
                f"Workspace file is missing some required keys: {str(e)}"
            ) from e
        self.__workspace = workspace

    def __parseGeneratorConfig(
        self, workspace: Parser.Workspace, SysConfig: configTypes.Configuration
    ):
        self.total_num_generated_files = 0
        filepath = workspace.GeneratorConfig
        with open(filepath, "r") as file:
            jsonData = json.load(file)
        GeneratorConfig: List[generationElement] = []
        for i, config in enumerate(jsonData):
            for key in mandatoryKeys:
                if not key in config:
                    raise KeyError(
                        f'The key "{key}" is mandatory but element {i} is missing it.'
                    )
            try:
                templates = helpers.forceStrList(config[TEMPLATES_KEY])
            except TypeError as e:
                raise TypeError(
                    f'Error in the generator config for values of the "templates" property: {str(e)}'
                ) from e
            parsedTemplates = []
            for template in templates:
                foundMatch = False
                try:
                    workspaceTemplateDirs = helpers.forceStrList(workspace.TemplateDir)
                except TypeError as e:
                    raise TypeError(
                        f'Error in the workspace config for values of the "TemplateDir" property: {str(e)}'
                    ) from e
                for templateDir in workspaceTemplateDirs:
                    templateFileDir = Path(template).parent
                    testpath = Path.joinpath(Path(templateDir), templateFileDir)
                    if testpath.is_dir():
                        foundMatch = True
                        break
                if foundMatch:
                    pattern = Path(template).stem + "*" + templateExtension
                    for file in testpath.rglob(pattern):
                        parsedTemplates.append(file)
            self.total_num_generated_files += len(parsedTemplates)
            try:
                outputPath = Path(workspace.resolvePath(config[OUTPUT_DIR_KEY]))
            except TypeError as e:
                raise TypeError(f"Error in generator config: {str(e)}") from e
            newElement = generationElement(outputPath, parsedTemplates)
            newElement.registerHooks(
                self.__callPreFileGenerationPluginHooks,
                self.__callPostFileGenerationPluginHooks,
            )
            if TARGET_KEY in config:
                if not LOOP_KEY in config:
                    raise KeyError(
                        f'If a property "{TARGET_KEY}" exists the "{LOOP_KEY}" must also exist'
                    )
                newElement.setTargetName(config[TARGET_KEY])
            if LOOP_KEY in config:
                self.total_num_generated_files += newElement.addLoop(
                    config[LOOP_KEY], SysConfig
                )
            if FILE_NAME_KEY in config:
                newElement.setOutName(config[FILE_NAME_KEY])
            if PATTERN_KEY in config:
                newElement.setPattern(config[PATTERN_KEY])

            GeneratorConfig.append(newElement)
        return GeneratorConfig

    def __callPreGenerationPluginHooks(
        self, systemConfig: configTypes.Configuration, num_of_files: int
    ):
        for plugin in self.__pluginList:
            plugin.preGeneration(systemConfig, num_of_files)

    def __callPreFileGenerationPluginHooks(
        self,
        currentTemplateDict: dict,
        systemConfig: configTypes.Configuration,
        file_path: Path,
    ):
        for plugin in self.__pluginList:
            currentTemplateDict = plugin.preFileGeneration(
                currentTemplateDict, systemConfig, file_path
            )

    def __callPostFileGenerationPluginHooks(self, file_path: Path, file_content: str):
        fileShouldBeGenerated = True
        for plugin in self.__pluginList:
            fileShouldBeGenerated &= plugin.postFileGeneration(file_path, file_content)
        return fileShouldBeGenerated

    def __callPostGenerationPluginHooks(self, file_paths: List[Path]):
        for plugin in self.__pluginList:
            plugin.postGeneration(file_paths)

    def generate(self, systemConfig: configTypes.Configuration = None):
        if systemConfig is None:
            try:
                parser = Parser.ConfigParser(self.__workspace)
                systemConfig = parser.parse()
            except Exception as e:
                raise Exception(f"The input config was not valid: \n{str(e)}") from e
        try:
            self.__genConfig = self.__parseGeneratorConfig(
                self.__workspace, systemConfig
            )
        except Exception as e:
            raise Exception(f"The generator config was not valid: \n{str(e)}") from e
        self.__callPreGenerationPluginHooks(
            systemConfig, self.total_num_generated_files
        )
        generatedFiles = []
        for genConf in self.__genConfig:
            generatedFiles += genConf.generate(systemConfig)
        self.__callPostGenerationPluginHooks(generatedFiles)

    def registerPlugin(
        self,
        plugin: Union[
            GeneratorPlugins.GeneratorPlugin, List[GeneratorPlugins.GeneratorPlugin]
        ],
    ):
        if type(plugin) is list:
            self.__pluginList.extend(plugin)
        elif type(plugin) is GeneratorPlugins.GeneratorPlugin:
            self.__pluginList.append(plugin)
        else:
            raise TypeError(
                f'Plugin registration only works with lists of plugins or single plugins. But the plugin that was passed was of type "{type(plugin)}".'
            )


if __name__ == "__main__":
    args = Parser.Workspace.getReqiredArgparse().parse_args()
    workspace = Parser.Workspace(args.WORKSPACE)
    myGenerator = Generator(workspace)
    myGenerator.generate()
