from typing import List
from Parser.ConfigTypes import ConfigElement

LABEL_KEY 		= "label"
TYPE_KEY 		= "type"
TOOLTIP_KEY		= "tooltip"
INHERIT_KEY		= "inherit"
PLACEHOLDER_KEY	= "placeholder"
VALIDATION_KEY	= "validation"
HIDDEN_KEY		= "hidden"
# special keys
ELEMENTS_KEY	= "elements"
STEP_KEY		= "step"
MIN_KEY			= "min"
MAX_KEY			= "max"

# helper decorator to ensure proper naming of functions
def overrides(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider

class AttributeType():
	""" Base class attribute type. Specifics should be overwritten in inherited classes
		The base type itself should never be instantiated.
	"""
	_comparison_type 		= None
	_needs_linking			= False

	def __init__(self, attribute_definition: dict, globalID: str):

		# internal helpers
		self._is_inherited 			= False
		self._attribute_definition 	= attribute_definition.copy()
		self._value					= None

		# special helpers
		if(PLACEHOLDER_KEY in attribute_definition):
			self._is_placeholder 	= attribute_definition[PLACEHOLDER_KEY]
		else:
			self._is_placeholder	= False

		# required properties
		self.globalID 				= globalID
		self.id 					= globalID.split("/")[1]

		error_message = "Attribute \"" + self.globalID + "\" is missing the required \"{}\" key."
		if(TYPE_KEY in attribute_definition):
			self.type 				= attribute_definition[TYPE_KEY]
		else:
			raise AttributeError(error_message.format(TYPE_KEY))

		# optional properties
		if(TOOLTIP_KEY in attribute_definition):
			self.tooltip 			= attribute_definition[TOOLTIP_KEY]
		else:
			self.tooltip 			= ""
		if(VALIDATION_KEY in attribute_definition):
			self.validation 		= attribute_definition[VALIDATION_KEY]
		else:
			self.validation 		= ""
		if(HIDDEN_KEY in attribute_definition):
			self.hidden 			= attribute_definition[HIDDEN_KEY]
		else:
			self.hidden 			= False
		if(LABEL_KEY in attribute_definition):
			self.label 				= attribute_definition[LABEL_KEY]
		elif(self.hidden == False and not self._is_placeholder):
			raise AttributeError(error_message.format(LABEL_KEY))

	def __new__(cls, *args, **kwargs):
		""" Prevent the instantiation of the base class
		"""
		if cls is AttributeType:
			raise TypeError("Base class of AttributeType shall never be instantiated")
		return super().__new__(cls)

	def getDefault(self):
		raise NotImplementedError("getDefault of the base class AttributeType was called. But this method should always be overwritten by a more specific type")

	def checkValue(self, valueInput):
		self._value = valueInput
		return valueInput

	@property
	def needsLinking(self) -> bool:
		return self._needs_linking

	@property
	def is_placeholder(self) -> bool:
		return self._is_placeholder

	@property
	def is_inherited(self) -> bool:
		return self._is_inherited

	@classmethod
	def is_type(cls, type: str) -> bool:
		if(cls._comparison_type is None):
			return False
		else:
			return type == cls._comparison_type

	def create_inheritor(self, inherit_properties: dict, globalID: str):
		overwriteWith = inherit_properties.copy()
		del overwriteWith[INHERIT_KEY]
		newAttributeDefinition = self._attribute_definition.copy()
		newAttributeDefinition.update(overwriteWith)
		newAttribute = parseAttribute(newAttributeDefinition, globalID)
		newAttribute._is_inherited = True
		return newAttribute

class StringType(AttributeType):
	_comparison_type = "string"

	@overrides(AttributeType)
	def getDefault(self) -> str:
		return ""

class BoolType(AttributeType):
	_comparison_type = "bool"

	@overrides(AttributeType)
	def getDefault(self) -> bool:
		return False

class IntType(AttributeType):
	_comparison_type = "int"

	@overrides(AttributeType)
	def __init__(self, attribute_definition: dict, globalID: str):
		super().__init__(attribute_definition, globalID)
		if(MIN_KEY in attribute_definition):
			self.min 			= attribute_definition[MIN_KEY]
		else:
			self.min 			= None
		if(MAX_KEY in attribute_definition):
			self.max 			= attribute_definition[MAX_KEY]
		else:
			self.max 			= None

	@overrides(AttributeType)
	def getDefault(self) -> int:
		return int(0)

class FloatType(IntType):
	_comparison_type = "float"

	@overrides(AttributeType)
	def getDefault(self) -> float:
		return float(0)

class ReferenceListType(AttributeType):
	_comparison_type 	= "referenceList"
	_needs_linking		= True

	@overrides(AttributeType)
	def getDefault(self) -> List[ConfigElement]:
		return []

class StringListType(AttributeType):
	_comparison_type = "stringList"

	@overrides(AttributeType)
	def getDefault(self) -> List[str]:
		return []

class SelectionType(AttributeType):
	_comparison_type 	= "selection"
	_needs_linking		= True

	@overrides(AttributeType)
	def __init__(self, attribute_definition: dict, globalID: str):
		super().__init__(attribute_definition, globalID)
		if(ELEMENTS_KEY in attribute_definition):
			self.elements 			= attribute_definition[ELEMENTS_KEY]
		else:
			self.elements 			= None

	@overrides(AttributeType)
	def getDefault(self) -> ConfigElement:
		return None

class HexType(IntType):
	_comparison_type = "hex"

	@overrides(AttributeType)
	def getDefault(self) -> int:
		return int(0)

class SliderType(AttributeType):
	_comparison_type = "slider"

	@overrides(AttributeType)
	def __init__(self, attribute_definition: dict, globalID: str):
		super().__init__(attribute_definition, globalID)
		if(STEP_KEY in attribute_definition):
			self.step 			= attribute_definition[STEP_KEY]
		else:
			self.step 			= 1

	@overrides(AttributeType)
	def getDefault(self) -> float:
		return int(0)


attributeTypeList = [StringType, BoolType, IntType, FloatType, ReferenceListType, StringListType, SelectionType, SelectionType, HexType, SliderType]


def parseAttribute(attributeDefinition: dict, AttributeGlobalID: str) -> AttributeType:
	if(not TYPE_KEY in attributeDefinition):
		raise KeyError("Type key is required for every attribute but it is missing")
	parseType = attributeDefinition[TYPE_KEY]
	newAttribute = None
	for attribType in attributeTypeList:
		if(attribType.is_type(parseType)):
			newAttribute = attribType(attributeDefinition, AttributeGlobalID)
			break
	if(newAttribute is None):
		raise KeyError(f"The type {parseType} is not a supported type")
	return newAttribute
