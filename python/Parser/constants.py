import re

# attribute keys:
###################################################
LABEL_KEY 					= "label"
TYPE_KEY 					= "type"
TOOLTIP_KEY					= "tooltip"
INHERIT_KEY					= "inherit"
PLACEHOLDER_KEY				= "placeholder"
HIDDEN_KEY					= "hidden"
PARENT_REFERENCE_TYPE_KEY	= "parentReference"
# special keys
VALIDATION_KEY				= "validation"
ELEMENTS_LIST_KEY			= "elements"
STEP_KEY					= "step"
MIN_KEY						= "min"
MAX_KEY						= "max"

baseKeys = [LABEL_KEY, TOOLTIP_KEY, HIDDEN_KEY, PLACEHOLDER_KEY, TYPE_KEY]


# config file root level keys:
###################################################
ELEMENTS_KEY				= "elements"
ATTRIBUTES_KEY				= "attributes"
VERSION_KEY					= "version"

configFileNameRegex			= re.compile(r"^[A-Za-z0-9]+$")
required_json_config_keys	= [ELEMENTS_KEY, ATTRIBUTES_KEY, VERSION_KEY]

# Config file elements keys:
###################################################
TARGET_KEY					= "target"
VALUE_KEY					= "value"
TARGET_NAME_OVERWRITE_KEY	= "targetNameOverwrite"

# workspace keys:
###################################################
WORKSPACE_PLACEHOLDER 	= "workspace"
