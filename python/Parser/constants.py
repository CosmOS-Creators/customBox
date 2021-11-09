import re

# attribute keys:
###################################################
LABEL_KEY = "label"  #: [ |JSON_PROPERTY_TYPE_STRING|, REQUIRED ] Used to define the label that is used in the UI this attribute definition
TYPE_KEY = "type"  #: [ |JSON_PROPERTY_TYPE_TYPE|, REQUIRED ] Selects the type of an attribute definition
TOOLTIP_KEY = "tooltip"  #: [ |JSON_PROPERTY_TYPE_STRING|, default = None ] Display a tooltip with additional information about this attribute definition
INHERIT_KEY = "inherit"  #: [ |JSON_PROPERTY_TYPE_LINK|, default = None ] Inherit all properties of an attribute definition to another attribute definition with the possibility to overwrite them if desidered
PLACEHOLDER_KEY = "placeholder"  #: [ |JSON_PROPERTY_TYPE_BOOL|, default = False ] Specify that an attribute definition has a value that is assigned during runtime, for example by a logic runner invoked by the generator, thus a attribute instance of this definition does not have a value property.
HIDDEN_KEY = "hidden"  #: [ |JSON_PROPERTY_TYPE_BOOL|, default = False ] Hides this attribute from the user interface if set to true
# special keys
VALIDATION_KEY = "validation"  #: [ |JSON_PROPERTY_TYPE_STRING|, default = None ] Used to specify a regex validation rule for this attribute definition
ELEMENTS_LIST_KEY = "elements"  #: [ |JSON_PROPERTY_TYPE_LIST|, REQUIRED in certain cases ] Used to specify a list of valid elements for this attribute definition. The list element types can differ depending on the attribute type.
STEP_KEY = "step"  #: [ |JSON_PROPERTY_TYPE_NUMBER|, default = 1 ] Used to specify a the step value for this attribute definition which will define how a spinner UI element will behave when the user clicks on the up or down arrow. If the value is an integer, the spinner will behave as a integer spinner. If the value is a float, the spinner will behave as a float spinner.
MIN_KEY = "min"  #: [ |JSON_PROPERTY_TYPE_NUMBER|, default = None ] Used to specify a the minimum value for this attribute definition which will define the minimum value for a spinner UI element.
MAX_KEY = "max"  #: [ |JSON_PROPERTY_TYPE_NUMBER|, default = None ] Used to specify a the maximum value for this attribute definition which will define the maximum value for a spinner UI element.
ALIGNMENT_KEY = "alignment"  #: [ |JSON_PROPERTY_TYPE_NUMBER|, default = None ] Used to specify a alignment value for this attribute definition which will define make sure any input is a multiple of this number.

baseKeys = [LABEL_KEY, TOOLTIP_KEY, HIDDEN_KEY, PLACEHOLDER_KEY, TYPE_KEY]

# attribute types:
###################################################
ATTRIB_TYPE_STRING = "string" #: defines an attribute that is a string. For further information see |STRING_ATTRIB|
ATTRIB_TYPE_INT = "int" #: defines an attribute that is an integer. For further information see |INT_ATTRIB|
ATTRIB_TYPE_FLOAT = "float" #: defines an attribute that is a float. For further information see |FLOAT_ATTRIB|
ATTRIB_TYPE_BOOL = "bool" #: defines an attribute that is a boolean. For further information see |BOOL_ATTRIB|
ATTRIB_TYPE_HEX = "hex" #: defines an attribute that is a hexadecimal number. For further information see |HEX_ATTRIB|
ATTRIB_TYPE_REFERENCE_LIST = "referenceList" #: defines an attribute that is a list of references. For further information see |REFERENCE_LIST_ATTRIB|
ATTRIB_TYPE_STRING_LIST = "stringList" #: defines an attribute that is a list of strings. For further information see |STRING_LIST_ATTRIB|
ATTRIB_TYPE_SELECTION = "selection" #: defines an attribute that is a selection. For further information see |SELECTION_ATTRIB|
ATTRIB_TYPE_SLIDER = "slider" #: defines an attribute that is a slider. For further information see |SLIDER_ATTRIB|
ATTRIB_TYPE_PARENT_REFERENCE = "parentReference" #: defines an attribute that is a reference to a parent attribute. For further information see |PARENT_REFERENCE_ATTRIB|


# config file root level keys:
###################################################
ELEMENTS_KEY = "elements"  #:
ATTRIBUTES_KEY = "attributes"  #:
VERSION_KEY = "version"  #:
CHECKSUM_KEY = "checksum"  #:
UI_KEY = "ui"  #:
UI_PAGE_KEY = "ui_page"  #:

configFileNameRegex = re.compile(r"^[A-Za-z0-9]+$")
required_json_config_keys = [ELEMENTS_KEY, ATTRIBUTES_KEY, VERSION_KEY]

# Config file elements keys:
###################################################
TARGET_KEY = "target"  #:
VALUE_KEY = "value"  #:
TARGET_NAME_OVERWRITE_KEY = "targetNameOverwrite"  #:

# workspace keys:
###################################################
WORKSPACE_PLACEHOLDER = "workspace"  #:

# user interface keys:
###################################################
UI_TAB_LABEL_KEY = "tab_label"  #:
UI_TAB_ICON_KEY = "tab_icon"  #:
UI_VIEW_TYPE_KEY = "view_type"  #:
UI_USE_PAGE_KEY = "use_page"  #:
UI_VIEW_TYPE_CARDED_KEY = "carded"  #:
UI_VIEW_TYPE_TABBED_KEY = "tabbed"  #:
UI_ALLOW_ELEMENT_DELETION = "allow_element_deletion"  #:
UI_ALLOW_ELEMENT_CREATION = "allow_element_creation"  #:

ui_page_required_json_keys = [UI_TAB_LABEL_KEY, UI_VIEW_TYPE_KEY]

# restriction keys:
###################################################
USE_RESTRICTION_KEY = "use_restriction"  #:
ELEMENT_RESTRICTIONS_KEY = "element_restrictions"  #:
RESTRICTION_REQUIRES_KEY = "requires"  #:
