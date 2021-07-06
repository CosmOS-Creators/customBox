import json
import os
import jinja2
from datetime 	import datetime
from pathlib 	import Path
from typing 	import Dict, List, Union
import Parser
import Parser.helpers 		as helpers
import Parser.ConfigTypes 	as configTypes
import GeneratorCorePlugins as GeneratorPlugins

templateExtension = ".j2"

TEMPLATES_KEY 			= "templates"
OUTPUT_DIR_KEY			= "outputDir"
LOOP_KEY				= "loop"
FILE_NAME_KEY			= "fileName"
TARGET_KEY				= "target"
PATTERN_KEY				= "pattern"

TARGET_PLACEHOLDER		= "{target}"
TEMPLATE_PLACEHOLDER	= "{template}"

mandatoryKeys = [TEMPLATES_KEY, OUTPUT_DIR_KEY]

timestampFormat = "%Y-%m-%d"

__version__ = "0.0.1"

class generationElement():
	__outputPath 		= ""
	__templates 		= []
	__loopElements 		= None
	__specialOutName	= None
	__targetConfig 		= None
	__targetName		= None
	__pattern			= None
	__preFileGenHook	= None
	__postFileGenHook	= None

	def __init__(self, outPath: str, templateFiles: List[Union[str, Path]]):
		self.__outputPath 	= outPath
		self.__templates 	= templateFiles

	def addLoop(self, loopConfigTarget: str, config: configTypes.Configuration):
		config.require(loopConfigTarget)
		Link = Parser.Link(loopConfigTarget)
		self.__loopElements = Link.resolve(config)
		self.__targetConfig = Link.config

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

	def injectTemplates(self, config: Dict[str, configTypes.Configuration], fileNamePattern: str):
		generatedFiles = []
		for template in self.__templates:
			templateName = Path(template).stem
			temp = Path(templateName)
			outFileSuffix = temp.suffix
			if(fileNamePattern is None):
				outFileName = temp.stem
			else:
				outFileName = Path(fileNamePattern.replace(TEMPLATE_PLACEHOLDER, templateName)).stem

			outputFilePath = Path.joinpath(self.__outputPath, outFileName + outFileSuffix)
			config["filename"] = outFileName + outFileSuffix
			if(not self.__pattern is None):
				for pattern in self.__pattern:
					if(pattern in outFileSuffix):
						outputDir = Path.joinpath(self.__outputPath, self.__pattern[pattern])
						outputFilePath = outputDir.joinpath(outFileName + outFileSuffix)
						if(not outputDir.exists()):
							os.makedirs(outputDir)
						break

			with open(template, "r") as template:
				templateContent = template.read()
			jinjaTemplate = jinja2.Template(templateContent)
			self.__preFileGenHook(config, config["config"], outputFilePath)
			try:
				renderedFile = jinjaTemplate.render(config)
			except Exception as e:
				raise Exception(f"Error while rendering template \"{str(template.name)}\" to file \"{outputFilePath}\": {str(e)}")
			with open(outputFilePath, "w") as file:
				file.write(renderedFile)
			self.__postFileGenHook(outputFilePath)
			generatedFiles.append(outputFilePath)
		return generatedFiles

	def generate(self, config: configTypes.Configuration):
		now = datetime.now()
		configDict = {
			"config": config,
			"version": __version__,
			"date": now.strftime(timestampFormat)}
		generatedFiles = []
		if(self.__loopElements is None):
			if(not self.__specialOutName is None):
				if(TARGET_PLACEHOLDER in self.__specialOutName):
					raise AttributeError("The value for the key \"fileName\" included a placeholder for the target name but no loop property was defined. This is an invalid combination")
			generatedFiles += self.injectTemplates(configDict, self.__specialOutName)
		else:
			if(not self.__targetConfig is None):
				link = Parser.Link.construct(config=self.__targetConfig)
				config.require(link)
				configDict[self.__targetConfig] = link.resolve(config)
			for element in self.__loopElements:
				filename = self.__specialOutName
				if(not self.__targetName is None):
					configDict[self.__targetName] = element["element"]
				if(not filename is None):
					filename = filename.replace(TARGET_PLACEHOLDER, element["target"])

				generatedFiles += self.injectTemplates(configDict, filename)
		return generatedFiles

class Generator():
	__pluginList:List[GeneratorPlugins.GeneratorPlugin] = []

	def __init__(self, workspace: Parser.Workspace):
		try:
			workspace.requireFolder(["config", "CoreConfig", "DefaultConfig", "TemplateDir"])
			workspace.requireFile(["GeneratorConfig"])
		except AttributeError as e:
			raise AttributeError(f"Workspace file is missing some required keys: {str(e)}")
		try:
			parser = Parser.ConfigParser(workspace)
			self.__sysConfig = parser.parse()
		except Exception as e:
			raise Exception(f"The input config was not valid: \n{str(e)}")
		try:
			self.__genConfig = self.__parseGeneratorConfig(workspace, self.__sysConfig)
		except Exception as e:
			raise Exception(f"The generator config was not valid: \n{str(e)}")

	def __parseGeneratorConfig(self, workspace: Parser.Workspace, SysConfig: configTypes.Configuration):
		filepath = workspace.GeneratorConfig
		with open(filepath, "r") as file:
			jsonData = json.load(file)
		GeneratorConfig: List[generationElement] = []
		for i, config in enumerate(jsonData):
			for key in mandatoryKeys:
				if(not key in config):
					raise KeyError(f"The key \"{key}\" is mandatory but element {i} is missing it.")
			try:
				templates = helpers.forceStrList(config[TEMPLATES_KEY])
			except TypeError as e:
				raise TypeError(f"Error in the generator config for values of the \"templates\" property: {str(e)}")
			parsedTemplates = []
			for template in templates:
				foundMatch = False
				try:
					workspaceTemplateDirs = helpers.forceStrList(workspace.TemplateDir)
				except TypeError as e:
					raise TypeError(f"Error in the workspace config for values of the \"TemplateDir\" property: {str(e)}")
				for templateDir in workspaceTemplateDirs:
					templateFileDir = Path(template).parent
					testpath = Path.joinpath(Path(templateDir), templateFileDir)
					if(os.path.isdir(testpath)):
						foundMatch = True
						break
				if(foundMatch):
					pattern = Path(template).stem + '*' + templateExtension
					for file in testpath.rglob(pattern):
						parsedTemplates.append(file)
			try:
				outputPath = Path(workspace.resolvePath(config[OUTPUT_DIR_KEY]))
			except TypeError as e:
				raise TypeError(f"Error in generator config: {str(e)}")
			if(not outputPath.exists()):
					os.makedirs(outputPath)
			newElement = generationElement(outputPath, parsedTemplates)
			newElement.registerHooks(self.__callPreFileGenerationPluginHooks, self.__callPostFileGenerationPluginHooks)
			if(TARGET_KEY in config):
				if(not LOOP_KEY in config):
					raise KeyError(f"If a property \"{TARGET_KEY}\" exists the \"{LOOP_KEY}\" must also exist")
				newElement.setTargetName(config[TARGET_KEY])
			if(LOOP_KEY in config):
				newElement.addLoop(config[LOOP_KEY], SysConfig)
			if(FILE_NAME_KEY in config):
				newElement.setOutName(config[FILE_NAME_KEY])
			if(PATTERN_KEY in config):
				newElement.setPattern(config[PATTERN_KEY])

			GeneratorConfig.append(newElement)
		return GeneratorConfig

	def __callPreGenerationPluginHooks(self, systemConfig: configTypes.Configuration):
		for plugin in self.__pluginList:
			plugin.preGeneration(systemConfig)

	def __callPreFileGenerationPluginHooks(self, currentTemplateDict: dict, systemConfig: configTypes.Configuration, file_path: Path):
		for plugin in self.__pluginList:
			currentTemplateDict = plugin.preFileGeneration(currentTemplateDict, systemConfig, file_path)

	def __callPostFileGenerationPluginHooks(self, file_path: Path):
		for plugin in self.__pluginList:
			plugin.postFileGeneration(file_path)

	def __callPostGenerationPluginHooks(self, file_paths: List[Path]):
		for plugin in self.__pluginList:
			plugin.postGeneration(file_paths)

	def generate(self):
		self.__callPreGenerationPluginHooks(self.__sysConfig)
		generatedFiles = []
		for genConf in self.__genConfig:
			generatedFiles += genConf.generate(self.__sysConfig)
		self.__callPostGenerationPluginHooks(generatedFiles)

	def registerPlugin(self, plugin: Union[GeneratorPlugins.GeneratorPlugin, List[GeneratorPlugins.GeneratorPlugin]]):
		if(type(plugin) is list):
			self.__pluginList.extend(plugin)
		elif(type(plugin) is GeneratorPlugins.GeneratorPlugin):
			self.__pluginList.append(plugin)
		else:
			raise TypeError(f'Plugin registration only works with lists of plugins or single plugins. But the plugin that was passed was of type "{type(plugin)}".')

if __name__ == "__main__":
	from Model import InitializerLogic, MemoryMapperLogic, PermissionerLogic
	args 				= Parser.Workspace.getReqiredArgparse().parse_args()
	workspace 			= Parser.Workspace(args.WORKSPACE)
	loggerPlugin 		= GeneratorPlugins.loggerPlugin()
	sectionPlugin 		= GeneratorPlugins.sectionParserPlugin()
	logicRunnerPlugin 	= GeneratorPlugins.logicRunnerPlugin()
	logicRunnerPlugin.registerLogic([InitializerLogic(), MemoryMapperLogic(), PermissionerLogic()])
	# try:
	myGenerator = Generator(workspace)
	myGenerator.registerPlugin([loggerPlugin, sectionPlugin, logicRunnerPlugin])
	myGenerator.generate()
	# except Exception as e:
	# 	print(f"[ERROR] Aborting execution of DefaultConfig.py: {str(e)}")
	# 	exit(1)
