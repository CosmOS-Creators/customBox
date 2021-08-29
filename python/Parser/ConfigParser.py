import json
import os
import Parser.VersionHandling 	as vh
import Parser.AttributeTypes 	as AttributeTypes
import Parser.ConfigTypes 		as ConfigTypes
import Parser.WorkspaceParser 	as WorkspaceParser
import Parser.constants			as const
from pathlib 					import Path
from typing 					import Dict, List, Union, NewType
from Parser.LinkElement 		import Link

# type definitions for better linting
AttributeCollectionType 	= NewType('AttributeCollectionType', Dict[str, AttributeTypes.AttributeType])

def processAttributes(config: Dict[str, object]) -> AttributeCollectionType:
	attributeCollection: AttributeCollectionType = {}
	AttributesToInherit: AttributeCollectionType = {}
	for configName in config:
		for attribute in config[configName][const.ATTRIBUTES_KEY]:
			currentAttribute = config[configName][const.ATTRIBUTES_KEY][attribute]
			globalIdentifier = Link.construct(config=configName, attribute=attribute)
			if(const.INHERIT_KEY in currentAttribute):
				if(not Link.isGlobal(currentAttribute[const.INHERIT_KEY])):
					currentAttribute[const.INHERIT_KEY] = Link.construct(config=configName, attribute=currentAttribute[const.INHERIT_KEY]).getLink()
				AttributesToInherit[globalIdentifier.getLink()] = currentAttribute
			else:
				try:
					attributeCollection[globalIdentifier.getLink()] = AttributeTypes.parseAttribute(currentAttribute, globalIdentifier)
				except KeyError as e:
					raise KeyError(f"Invalid attribute in config \"{configName}\" for attribute \"{attribute}\": {e}")
	for attribLink in AttributesToInherit:
		attrib = AttributesToInherit[attribLink]
		link = Link(attribLink)
		try:
			baseAttribute = attributeCollection[attrib[const.INHERIT_KEY]]
		except KeyError:
			raise KeyError(f"In config \"{link.config}\" the attribute inherit target \"{attrib[const.INHERIT_KEY]}\" does not match any known attributes")
		if(baseAttribute.is_inherited):
			raise Exception(f"In config \"{link.config}\" it was tried to inherit from \"{attrib[const.INHERIT_KEY]}\" but this attribute is already inherited and inheritance nesting is not supported at the moment.")
		attributeCollection[attribLink] = baseAttribute.create_inheritor(attrib, attribLink)

	return attributeCollection

def processConfig(config: dict, configName: str, completeConfig: ConfigTypes.Configuration, source_file: Path):
	file_version = vh.Version(config[const.VERSION_KEY])
	if(not vh.CompatabilityManager.is_compatible(file_version)):
		config = vh.CompatabilityManager.upgrade(config)
	if(completeConfig.hasSubConfig(configName)):
		subconfig = completeConfig.getSubconfig(configName)
	else:
		subconfig = completeConfig.createSubconfig(configName, source_file, config[const.VERSION_KEY])
	for element in config[const.ELEMENTS_KEY]:
		currentElement = config[const.ELEMENTS_KEY][element]
		newElement = subconfig.createElement(element)
		if(not type(currentElement) is list):
			raise Exception(f"In config \"{configName}\" the \"{const.ELEMENTS_KEY}\" property is required to be a list but found {type(currentElement)}")
		for attributeInstance in currentElement:
			newElement.createAttributeInstanceFromDefinition(attributeInstance)
	if(const.UI_PAGE_KEY in config):
		for pageName, uiPage in config[const.UI_PAGE_KEY].items():
			completeConfig.UiConfig.createpage(pageName, uiPage)
	if(const.UI_KEY in config):
		if(const.UI_USE_PAGE_KEY in config[const.UI_KEY]):
			subconfig = completeConfig.getSubconfig(configName)
			subconfig.assignToUiPage(config[const.UI_KEY][const.UI_USE_PAGE_KEY])

def linkParents(objConfigs: ConfigTypes.Configuration):
	for subConfig in objConfigs.configs.values():
		for element in subConfig:
			for attribInst in element:
				if(type(attribInst) is ConfigTypes.AttributeInstance):
					attribInst.ResolveValueLink()
		subConfig.resolveUiAssignment()

def config_file_sanity_check(config: dict):
	for required_key in const.required_json_config_keys:
		if(not required_key in config):
			raise KeyError(f"Every config file must have a key named \"{required_key}\"")

def discoverConfigFiles(configPath: Union[str,List[str]]) -> List[Path]:
	configPaths: List[str] = []
	if(type(configPath) is str):
		configPaths = [configPath]
	elif(type(configPath) is list):
		configPaths = configPath
	configFiles = []
	for currentConfigPath in configPaths:
		if(not os.path.exists(currentConfigPath) or not os.path.isdir(currentConfigPath)):
			raise FileNotFoundError("Input path was not valid or not a directory")
		for path in Path(currentConfigPath).rglob('*.json'):
			configFiles.append(path.absolute())
	return configFiles

class ConfigParser():
	def __init__(self, workspace: WorkspaceParser.Workspace):
		workspace.requireFolder(["config"])
		self.__workspace 	= workspace

	def parse(self)  -> ConfigTypes.Configuration:
		configFiles = discoverConfigFiles(self.__workspace.config)
		jsonConfigs = dict()
		configFileNames = dict()
		for configFile in configFiles:
			with configFile.open("r") as currentFile:
				configCleanName = configFile.stem
				if(not const.configFileNameRegex.match(configCleanName)):
					raise Exception(f"Config file names are oly allowed to contain lower case alphanumeric characters but the file \"{configFile}\" would generate a config named \"{configCleanName}\" which would violate this restriction")
				if(configCleanName in jsonConfigs):
					raise Exception(f"Config file names have to be unique but the files \"{configFileNames[configCleanName]}\" and \"{configFile}\" have the same name({configCleanName}) thus are considered duplicated.")
				try:
					loaded_json_config = json.load(currentFile)
				except json.JSONDecodeError as e:
					raise Exception(f"Config file \"{configFile}\" is not a valid json: {str(e)}")
				try:
					config_file_sanity_check(loaded_json_config)
				except KeyError as e:
					raise KeyError(f"Error in config file \"{configFile}\": {str(e)}")
				configFileNames[configCleanName] = configFile
				jsonConfigs[configCleanName] = loaded_json_config

		# make sure to load all attributes before loading all configs
		self.__attributeCollection = processAttributes(jsonConfigs)
		configuration = ConfigTypes.Configuration(self.__attributeCollection)
		for config in jsonConfigs:
			processConfig(jsonConfigs[config], config, configuration, configFileNames[config])
		linkParents(configuration)
		return configuration

if __name__ == "__main__":
	parser = WorkspaceParser.Workspace.getReqiredArgparse()
	args = parser.parse_args()
	workspace = WorkspaceParser.Workspace(args.WORKSPACE)
	parser = ConfigParser(workspace)
	fullConfig = parser.parse()
	fullConfig.require(['tasks/task_0:uniqueId'])
	fullConfig.tasks.task_0.uniqueId = 5
	fullConfig.cores.core_0.corePrograms = [fullConfig.programs.program_0]
	configStr = ConfigTypes.formatConfig(fullConfig)
	with open("ConfigDump", "w") as file:
		file.write(configStr)
	print(configStr)
