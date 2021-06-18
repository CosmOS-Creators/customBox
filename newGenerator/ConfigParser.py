import json
import os
from types import SimpleNamespace
from pathlib import Path
import AttributeTypes
from AttributeTypes import AttributeType
from typing import Dict, List, Union, NewType

ELEMENTS_KEY				= "elements"
ATTRIBUTES_KEY				= "attributes"
VERSION_KEY					= "version"

TARGET_KEY					= "target"
VALUE_KEY					= "value"
INHERIT_KEY					= "inherit"

PARENT_REFERENCE_KEY		= "parentReference"
PARENT_REFERENCE_NAME_KEY	= "name"
TARGET_NAME_OVERWRITE_KEY	= "targetNameOverwrite"

OBJECT_ID_ATTRIBUTE			= "id"
OBJECT_ITERATOR_ATTRIBUTE	= "iterator"

required_json_config_keys	= [ELEMENTS_KEY, ATTRIBUTES_KEY, VERSION_KEY]

# type definitions for better linting
jsonConfigType 				= NewType('jsonConfigType', Dict[str, object])
AttributeCollectionType 	= NewType('AttributeCollectionType', Dict[str, AttributeType])

def processAttributes(config: jsonConfigType) -> AttributeCollectionType:
	attributeCollection: AttributeCollectionType = {}
	AttributesToInherit: Dict[str, AttributeType] = {}
	for configName in config:
		for attribute in config[configName][ATTRIBUTES_KEY]:
			currentAttribute = config[configName][ATTRIBUTES_KEY][attribute]
			if(INHERIT_KEY in currentAttribute):
				if(not "/" in currentAttribute[INHERIT_KEY]):
					currentAttribute[INHERIT_KEY] = getGlobalLink(configName, currentAttribute[INHERIT_KEY])
				AttributesToInherit[getGlobalLink(configName, attribute)] = currentAttribute
			else:
				try:
					attributeCollection[getGlobalLink(configName, attribute)] = AttributeTypes.parseAttribute(currentAttribute)
				except KeyError as e:
					raise KeyError(f"Invalid attribute in config {configName} for attribute {attribute}: {e}")
	for attribLink in AttributesToInherit:
		attrib = AttributesToInherit[attribLink]
		configName = getConfigNameFromLink(attribLink)
		baseAttribute = attributeCollection[attrib[INHERIT_KEY]]
		if(baseAttribute.is_inherited):
			raise Exception(f"In config {configName} it was tried to inherit from {attrib[INHERIT_KEY]} but this attribute is already inherited and inheritance nesting is not supported at the moment.")
		attributeCollection[attribLink] = baseAttribute.create_inheritor(attrib)

	return attributeCollection

def processConfig(config: dict, configName: str, completeConfig: SimpleNamespace, attributeCollection: AttributeCollectionType):
	for element in config[ELEMENTS_KEY]:
		currentElement = config[ELEMENTS_KEY][element]
		if(not hasattr(completeConfig, configName)):
			setattr(completeConfig, configName, SimpleNamespace())
			currentConfig = getattr(completeConfig, configName)
			setattr(currentConfig, OBJECT_ITERATOR_ATTRIBUTE, [])
		else:
			currentConfig = getattr(completeConfig, configName)

		newElement = SimpleNamespace()
		setattr(currentConfig, element, newElement)
		setattr(newElement, OBJECT_ID_ATTRIBUTE, element) # add the key of the element as an id inside the object so that it can be accessed also when iterating over the elements
		iterator = getattr(currentConfig, OBJECT_ITERATOR_ATTRIBUTE)
		iterator.append(newElement)
		if(not type(currentElement) is list):
			raise Exception(f"In config {configName} the {ELEMENTS_KEY} property is required to be a list but found {type(currentElement)}")
		for attributeInstance in currentElement:
			if(TARGET_KEY in attributeInstance and VALUE_KEY in attributeInstance): # this is a normal attribute instance
				attribute = resolveAttributeLink(attributeCollection, configName, attributeInstance[TARGET_KEY])
				propertyName = attributeInstance[TARGET_KEY]
				if(TARGET_NAME_OVERWRITE_KEY in attributeInstance):
					propertyName = attributeInstance[TARGET_NAME_OVERWRITE_KEY]
				setattr(newElement, propertyName, attribute.checkValue(attributeInstance[VALUE_KEY]))
			elif(TARGET_KEY in attributeInstance): # might be a placeholder instance
				attribute = resolveAttributeLink(attributeCollection, configName, attributeInstance[TARGET_KEY])
				if(attribute.is_placeholder):
					setattr(newElement, attributeInstance[TARGET_KEY], attribute.getDefault())
				else:
					raise Exception(f"Invalid attribute instance formatting in {configName} config. The following property is missing the {VALUE_KEY} property: {attributeInstance}")
			elif(not PARENT_REFERENCE_KEY in attributeInstance): # this is parent reference special attribute instance
				raise Exception(f"Invalid attribute instance formatting in {configName} config. The following property is invalid: {attributeInstance}")

def resolveElementLink(globalConfig: SimpleNamespace, localConfig: SimpleNamespace, link: str):
	if('/' in link):
		config, target = link.split('/')
		try:
			targetConfig = getattr(globalConfig, config)
		except AttributeError:
			raise AttributeError(f"Configuration has no subconfig named {config}")
		try:
			linkTarget = getattr(targetConfig, target)
		except AttributeError:
			raise AttributeError(f"Configuration {config} has no element named {target}")
	else:
		try:
			linkTarget = getattr(localConfig, link)
		except AttributeError:
			raise AttributeError(f"Configuration has no element named {link}")
	return linkTarget

def resolveAttributeLink(attributeCollection: AttributeCollectionType, localConfig: str, link: str) -> AttributeType:
	if('/' in link):
		try:
			linkTarget = attributeCollection[link]
		except KeyError:
			raise KeyError(f"Could not find a target attribute for {link} in {localConfig} config")
	else:
		globalLink = getGlobalLink(localConfig, link)
		try:
			linkTarget = attributeCollection[globalLink]
		except KeyError:
			raise KeyError(f"Could not find a target attribute for {link} in {localConfig} config")
	return linkTarget

def getGlobalLink(location: str, target: str):
	return location + "/" + target

def getConfigNameFromLink(globalLink: str):
	return globalLink.split("/")[0]

def linkParents(jsonConfigs: jsonConfigType, objConfigs: SimpleNamespace, attributeCollection: AttributeCollectionType):
	for config in jsonConfigs:
		for element in jsonConfigs[config][ELEMENTS_KEY]:
			for attributeInstance in jsonConfigs[config][ELEMENTS_KEY][element]:
				if(PARENT_REFERENCE_KEY in attributeInstance):
					local_config = getattr(objConfigs, config)
					try:
						parentObject = resolveElementLink(objConfigs, local_config, attributeInstance[PARENT_REFERENCE_KEY])
					except AttributeError as e:
						raise AttributeError(f"Error in {config} config. Target link was invalid: " + str(e))
					if(not hasattr(parentObject, config)):
						setattr(parentObject, config, SimpleNamespace())
						parentLink_obj = getattr(parentObject, config)
						setattr(parentLink_obj, OBJECT_ITERATOR_ATTRIBUTE, [])
					else:
						parentLink_obj = getattr(parentObject, config)
					element_obj = getattr(local_config, element)
					setattr(parentLink_obj, element, element_obj)
					iterator = getattr(parentLink_obj, OBJECT_ITERATOR_ATTRIBUTE)
					iterator.append(element_obj)
					if(PARENT_REFERENCE_NAME_KEY in attributeInstance):
						setattr(element_obj, attributeInstance[PARENT_REFERENCE_NAME_KEY], parentObject)
				else:
					attribTarget = attributeCollection[getGlobalLink(config, attributeInstance[TARGET_KEY])]
					if(attribTarget.needsLinking):
						None

def config_file_sanity_check(config: dict):
	for required_key in required_json_config_keys:
		if(not required_key in config):
			raise KeyError(f"Every config file must have a key named {required_key}")

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

def loadConfig(configPath: Union[str,List[str]]) -> SimpleNamespace:
	configuration = SimpleNamespace()
	configFiles = discoverConfigFiles(configPath)

	jsonConfigs = {}
	for configFile in configFiles:
		with open(configFile, "r") as currentFile:
			try:
				loaded_json_config = json.load(currentFile)
			except json.JSONDecodeError as e:
				raise Exception(f"Config file \"{configFile}\" is not a valid json: {str(e)}")
			try:
				config_file_sanity_check(loaded_json_config)
			except KeyError as e:
				raise KeyError(f"Error in config file \"{configFile}\": {str(e)}")
			configCleanName = Path(configFile).stem
			jsonConfigs[configCleanName] = loaded_json_config

	# make sure to load all attributes before loading all configs
	attributeCollection = processAttributes(jsonConfigs)

	for config in jsonConfigs:
		processConfig(jsonConfigs[config], config, configuration, attributeCollection)
	linkParents(jsonConfigs, configuration, attributeCollection)
	return configuration

if __name__ == "__main__":
	from pretty_simple_namespace import pprint
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("INPUT", help="Input config file path", type=str, metavar='N', nargs='+')
	args = parser.parse_args()
	fullConfig = loadConfig(args.INPUT)
	pprint(fullConfig)
