import json
import os

configInPath = r"C:\Files\Projects\Developement\CosmOS\reference_project_stmIDE\Cosmos\generated\integration\systemConfig\configDef"

ELEMENTS_KEY    = "elements"
ATTRIBUTES_KEY  = "attributes"
VERSION_KEY     = "version"

TARGET_KEY      = "target"
VALUE_KEY       = "value"

PARENT_REFERENCE_KEY = "parentReference"




PARENT_REFERENCE_PLACEHOLDER_KEY = "parentReferenceNeedsToBeLinked"

required_json_config_keys = [ELEMENTS_KEY, ATTRIBUTES_KEY, VERSION_KEY]

configuration = {}


def processConfig(config, configName):
    global configuration
    for element in config[ELEMENTS_KEY]:
        currentElement = config[ELEMENTS_KEY][element]
        if(not configName in configuration):
            configuration[configName] = {}
        configuration[configName][element] = {}
        for attributeInstance in currentElement:
            if(TARGET_KEY in attributeInstance and VALUE_KEY in attributeInstance): # this is a normal attribute instance
                configuration[configName][element][attributeInstance[TARGET_KEY]] = attributeInstance[VALUE_KEY]
            elif(PARENT_REFERENCE_KEY in attributeInstance): # this is parent reference special attribute instance
                configuration[configName][element][PARENT_REFERENCE_PLACEHOLDER_KEY] = attributeInstance[PARENT_REFERENCE_KEY]
            else:
                raise Exception(f"Invalid attribute instance formatting in {configName} config. The following property is invalid: {attributeInstance}")


def linkParents(config):
    pass


def config_file_sanity_check(config, filepath):
    for required_key in required_json_config_keys:
        if(not (required_key in config)):
            raise KeyError(f"Every config file must have a key named {required_key} but the file \"{filepath}\" didn't")


def loadConfig(configPath: str):
    global configuration
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
        processConfig(jsonConfigs[config], config)
    with open("dump", "w") as file:
        json.dump(configuration,file)
    linkParents(configuration)
    None

loadConfig(configInPath)
