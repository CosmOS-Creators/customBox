import json
import os
from types import SimpleNamespace

ELEMENTS_KEY    = "elements"
ATTRIBUTES_KEY  = "attributes"
VERSION_KEY     = "version"

TARGET_KEY      = "target"
VALUE_KEY       = "value"

PARENT_REFERENCE_KEY = "parentReference"

OBJECT_ID_ATTRIBUTE = "id"
OBJECT_ITERATOR_ATTRIBUTE = "iterator"

required_json_config_keys = [ELEMENTS_KEY, ATTRIBUTES_KEY, VERSION_KEY]

def processConfig(config: dict, configName: str, completeConfig: object):
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
        for attributeInstance in currentElement:
            if(TARGET_KEY in attributeInstance and VALUE_KEY in attributeInstance): # this is a normal attribute instance
                setattr(newElement, attributeInstance[TARGET_KEY], attributeInstance[VALUE_KEY])
            elif(not PARENT_REFERENCE_KEY in attributeInstance): # this is parent reference special attribute instance
                raise Exception(f"Invalid attribute instance formatting in {configName} config. The following property is invalid: {attributeInstance}")

def resolveElementLink(configObj: object, link: str):
    config, target = link.split('/')
    targetConfig = getattr(configObj, config)
    return getattr(targetConfig, target)

def linkParents(jsonConfigs: dict, objConfigs: object):
    for config in jsonConfigs:
        for element in jsonConfigs[config][ELEMENTS_KEY]:
            for attributeInstance in jsonConfigs[config][ELEMENTS_KEY][element]:
                if(PARENT_REFERENCE_KEY in attributeInstance):
                    parentObject = resolveElementLink(objConfigs, attributeInstance[PARENT_REFERENCE_KEY])
                    link = SimpleNamespace()
                    if(not hasattr(parentObject, config)):
                        setattr(parentObject, config, link)
                        config_obj = getattr(objConfigs, config)
                        parentLink_obj = getattr(parentObject, config)
                        setattr(parentLink_obj, OBJECT_ITERATOR_ATTRIBUTE, [])
                    else:
                        config_obj = getattr(objConfigs, config)
                        parentLink_obj = getattr(parentObject, config)
                    element_obj = getattr(config_obj, element)
                    setattr(parentLink_obj, element, element_obj)
                    iterator = getattr(parentLink_obj, OBJECT_ITERATOR_ATTRIBUTE)
                    iterator.append(element_obj)

def config_file_sanity_check(config: dict, filepath: str):
    for required_key in required_json_config_keys:
        if(not required_key in config):
            raise KeyError(f"Every config file must have a key named {required_key} but the file \"{filepath}\" didn't")

def loadConfig(configPath: str):
    configuration = SimpleNamespace()
    if(not os.path.exists(configPath) or not os.path.isdir(configPath)):
        raise FileNotFoundError("Input path was not valid or not a directory")
    configFiles = [f for f in os.listdir(configPath) if f.endswith('.json')]
    jsonConfigs = {}
    for configFile in configFiles:
        filepath = os.path.join(configPath, configFile)
        with open(filepath, "r") as currentFile:
            loaded_json_config = json.load(currentFile)
            config_file_sanity_check(loaded_json_config, filepath)
            configCleanName = os.path.splitext(configFile)[0]
            jsonConfigs[configCleanName] = loaded_json_config

    for config in jsonConfigs:
        processConfig(jsonConfigs[config], config, configuration)
    linkParents(jsonConfigs, configuration)
    return configuration

if __name__ == "__main__":
    from pretty_simple_namespace import pprint
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("INPUT", help="Input config file path")
    args = parser.parse_args()
    fullConfig = loadConfig(args.INPUT)
    pprint(fullConfig)
