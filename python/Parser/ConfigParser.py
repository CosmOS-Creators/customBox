import json
import os
from pathlib import Path
from typing import Dict, List, Union, NewType
import re

import Parser.AttributeTypes as AttributeTypes
import Parser.ConfigTypes as ConfigTypes
from Parser.helpers import Link, forceLink
import Parser.WorkspaceParser as WorkspaceParser

ELEMENTS_KEY				= "elements"
ATTRIBUTES_KEY				= "attributes"
VERSION_KEY					= "version"

TARGET_KEY					= "target"
VALUE_KEY					= "value"
INHERIT_KEY					= "inherit"

TARGET_NAME_OVERWRITE_KEY	= "targetNameOverwrite"

configFileNameRegex			= re.compile(r"^[A-Za-z0-9]+$")

required_json_config_keys	= [ELEMENTS_KEY, ATTRIBUTES_KEY, VERSION_KEY]

# type definitions for better linting
jsonConfigType 				= NewType('jsonConfigType', Dict[str, object])
AttributeCollectionType 	= NewType('AttributeCollectionType', Dict[str, AttributeTypes.AttributeType])

reservedConfigNames = ["require", "activateValueGuards"]
reservedElementNames = ["iterator", "activateValueGuards"]
reservedAttributeNames = ["id", "populate", "link", "activateValueGuards", "assignAttribute", "_setattr_direct"]

def processAttributes(config: jsonConfigType) -> AttributeCollectionType:
	attributeCollection: AttributeCollectionType = {}
	AttributesToInherit: Dict[str, AttributeTypes.AttributeType] = {}
	for configName in config:
		for attribute in config[configName][ATTRIBUTES_KEY]:
			currentAttribute = config[configName][ATTRIBUTES_KEY][attribute]
			globalIdentifier = Link.construct(config=configName, attribute=attribute).getLink()
			if(INHERIT_KEY in currentAttribute):
				if(not Link.isGlobal(currentAttribute[INHERIT_KEY])):
					currentAttribute[INHERIT_KEY] = Link.construct(config=configName, attribute=currentAttribute[INHERIT_KEY]).getLink()
				AttributesToInherit[globalIdentifier] = currentAttribute
			else:
				try:
					attributeCollection[globalIdentifier] = AttributeTypes.parseAttribute(currentAttribute, globalIdentifier)
				except KeyError as e:
					raise KeyError(f"Invalid attribute in config \"{configName}\" for attribute \"{attribute}\": {e}")
	for attribLink in AttributesToInherit:
		attrib = AttributesToInherit[attribLink]
		link = Link(attribLink)
		try:
			baseAttribute = attributeCollection[attrib[INHERIT_KEY]]
		except KeyError:
			raise KeyError(f"In config \"{link.config}\" the attribute inherit target \"{attrib[INHERIT_KEY]}\" does not match any known attributes")
		if(baseAttribute.is_inherited):
			raise Exception(f"In config \"{link.config}\" it was tried to inherit from \"{attrib[INHERIT_KEY]}\" but this attribute is already inherited and inheritance nesting is not supported at the moment.")
		attributeCollection[attribLink] = baseAttribute.create_inheritor(attrib, attribLink)

	return attributeCollection

def processConfig(config: dict, configName: str, completeConfig: ConfigTypes.Configuration, attributeCollection: AttributeCollectionType):
	if(configName in reservedConfigNames):
		raise Exception(f"Creating a config with the name \"{configName}\" is not permitted as \"{configName}\" is a reserved keyword")
	for element in config[ELEMENTS_KEY]:
		if(element in reservedElementNames):
			raise Exception(f"In config \"{configName}\" is was requested to create an element with the name \"{element}\" but this name is a reserved keyword thus the creation of such an element is prohibited")
		currentElement = config[ELEMENTS_KEY][element]
		if(not hasattr(completeConfig, configName)):
			currentConfig = ConfigTypes.Subconfig(Link.construct(config=configName))
			setattr(completeConfig, configName, currentConfig)
		else:
			currentConfig = getattr(completeConfig, configName)

		link 			= Link.construct(config=configName, element=element)
		newElement 		= ConfigTypes.ConfigElement(completeConfig, link)
		setattr(currentConfig, element, newElement)
		newElement.id 	= element # add the key of the element as an id inside the object so that it can be accessed also when iterating over the elements
		currentConfig.iterator.append(newElement)
		if(not type(currentElement) is list):
			raise Exception(f"In config \"{configName}\" the \"{ELEMENTS_KEY}\" property is required to be a list but found {type(currentElement)}")
		for attributeInstance in currentElement:
			if(not TARGET_KEY in attributeInstance):
				raise Exception(f"Invalid attribute instance formatting in \"{configName}\" config. The following property is invalid: {attributeInstance}")
			targetLink = Link(attributeInstance[TARGET_KEY], Link.EMPHASIZE_ATTRIBUTE)
			propertyName = targetLink.attribute
			attribute = resolveAttributeLink(attributeCollection, configName, targetLink)
			newElement.assignAttribute(propertyName, attribute)
			if(propertyName in reservedAttributeNames):
				raise Exception(f"In config \"{configName}\" is was requested to create an attribute with the name \"{propertyName}\" but this name is a reserved keyword thus the creation of such an attribute is prohibited")
			if(attribute.is_placeholder):
				if(VALUE_KEY in attributeInstance):
					raise Exception(f"In config \"{configName}\" element \"{element}\" instantiates the attribute definition \"{propertyName}\" which is a placeholder but the value key ist also defined which is invalid for placeholder entries.")
				if(hasattr(newElement, propertyName)):
					raise Exception(f"In config \"{configName}\" is was requested to create a property for the element \"{element}\" with the name \"{propertyName}\" but a property with that name already exists for that element")
				setattr(newElement, propertyName, attribute.getDefault())
			elif(VALUE_KEY in attributeInstance): # this is a normal attribute instance
				if(TARGET_NAME_OVERWRITE_KEY in attributeInstance):
					propertyName = attributeInstance[TARGET_NAME_OVERWRITE_KEY]
					attributeCollection[Link.construct(config=configName, attribute=propertyName)] = attribute # create an alias for the same attribute
				if(hasattr(newElement, propertyName)):
					raise Exception(f"In config \"{configName}\" is was requested to create a property for the element \"{element}\" with the name \"{propertyName}\" but a property with that name already exists for that element")
				try:
					parsedValue = attribute.checkValue(attributeInstance[VALUE_KEY])
				except ValueError as e:
					location = Link.construct(config=configName, element=element)
					raise Exception(f"Validation in \"{location}\" for property \"{propertyName}\" failed: {str(e)}")
				setattr(newElement, propertyName, parsedValue)
			else:
				raise Exception(f"Invalid attribute instance formatting in \"{configName}\" config. The following property is missing the \"{VALUE_KEY}\" property: {attributeInstance}")

def resolveElementLink(globalConfig: ConfigTypes.Configuration, localConfig: ConfigTypes.Subconfig, link: Union[str, Link]):
	link = forceLink(link)
	if(link.isGlobal()):
		return link.resolveElement(globalConfig)
	else:
		try:
			linkTarget = getattr(localConfig, link)
		except AttributeError:
			raise AttributeError(f"Configuration has no element named \"{link}\"")
		return linkTarget

def resolveAttributeLink(attributeCollection: AttributeCollectionType, localConfig: str, link: Union[str, Link]) -> AttributeTypes.AttributeType:
	link = forceLink(link)
	if(link.isGlobal()):
		try:
			linkTarget = attributeCollection[link.getLink()]
		except KeyError:
			raise KeyError(f"Could not find a target attribute for \"{link}\" in \"{localConfig}\" config")
	else:
		link.config = localConfig
		try:
			linkTarget = attributeCollection[link.getLink()]
		except KeyError:
			raise KeyError(f"Could not find a target attribute for \"{link}\" in \"{localConfig}\" config")
	return linkTarget

def linkParents(jsonConfigs: jsonConfigType, objConfigs: ConfigTypes.Configuration, attributeCollection: AttributeCollectionType):
	for config in jsonConfigs:
		for element in jsonConfigs[config][ELEMENTS_KEY]:
			for attributeInstance in jsonConfigs[config][ELEMENTS_KEY][element]:
				local_config = getattr(objConfigs, config)
				element_obj = getattr(local_config, element)
				if(Link.isGlobal(attributeInstance[TARGET_KEY])):
					link = Link(attributeInstance[TARGET_KEY])
				else:
					link = Link.construct(config=config, attribute=attributeInstance[TARGET_KEY])
				attribTarget = attributeCollection[link.getLink()]
				if(TARGET_NAME_OVERWRITE_KEY in attributeInstance):
					attributeName = attributeInstance[TARGET_NAME_OVERWRITE_KEY]
				else:
					attributeName = attributeInstance[TARGET_KEY]
				try:
					attribTarget.link(objConfigs, element_obj, attributeName)
				except NameError as e:
					raise NameError(f"Error in \"{config}\" config: {str(e)}")

def config_file_sanity_check(config: dict):
	for required_key in required_json_config_keys:
		if(not required_key in config):
			raise KeyError(f"Every config file must have a key named \"{required_key}\"")

def discoverConfigFiles(configPath: Union[str,List[str]]) -> List[str]:
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
		jsonConfigs = {}
		configFileNames = {}
		for configFile in configFiles:
			with open(configFile, "r") as currentFile:
				configCleanName = Path(configFile).stem
				if(not configFileNameRegex.match(configCleanName)):
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
		configuration = ConfigTypes.Configuration()

		# make sure to load all attributes before loading all configs
		self.__attributeCollection = processAttributes(jsonConfigs)
		for config in jsonConfigs:
			processConfig(jsonConfigs[config], config, configuration, self.__attributeCollection)
		linkParents(jsonConfigs, configuration, self.__attributeCollection)
		configuration.activateValueGuards(True)
		return configuration

if __name__ == "__main__":
	from pretty_simple_namespace import pprint, format
	parser = WorkspaceParser.Workspace.getReqiredArgparse()
	args = parser.parse_args()
	workspace = WorkspaceParser.Workspace(args.WORKSPACE)
	parser = ConfigParser(workspace)
	fullConfig = parser.parse()
	fullConfig.require(['tasks/task_0:uniqueId'])
	fullConfig.tasks.task_0.populate("uniqueId", 5)
	fullConfig.cores.core_0.populate("corePrograms", [fullConfig.programs.program_0])
	with open("ConfigDump", "w") as file:
		file.write(format(fullConfig))
	pprint(fullConfig)
