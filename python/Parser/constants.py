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
CHECKSUM_KEY				= "checksum"
UI_KEY						= "ui"
UI_PAGE_KEY					= "ui_page"

configFileNameRegex			= re.compile(r"^[A-Za-z0-9]+$")
required_json_config_keys	= [ELEMENTS_KEY, ATTRIBUTES_KEY, VERSION_KEY]

# Config file elements keys:
###################################################
TARGET_KEY					= "target"
VALUE_KEY					= "value"
TARGET_NAME_OVERWRITE_KEY	= "targetNameOverwrite"

# workspace keys:
###################################################
WORKSPACE_PLACEHOLDER 		= "workspace"

# user interface keys:
###################################################
UI_TAB_LABEL_KEY			= "tab_label"
UI_TAB_ICON_KEY				= "tab_icon"
UI_VIEW_TYPE_KEY			= "view_type"
UI_USE_PAGE_KEY				= "use_page"
UI_VIEW_TYPE_CARDED_KEY		= "carded"
UI_VIEW_TYPE_TABBED_KEY		= "tabbed"
UI_ALLOW_ELEMENT_DELETION	= "allow_element_deletion"
UI_ALLOW_ELEMENT_CREATION	= "allow_element_creation"

ui_page_required_json_keys	= [UI_TAB_LABEL_KEY, UI_VIEW_TYPE_KEY]

# restriction keys:
###################################################
USE_RESTRICTION_KEY			= "use_restriction"
ELEMENT_RESTRICTIONS_KEY	= "element_restrictions"
RESTRICTION_REQUIRES_KEY	= "requires"
