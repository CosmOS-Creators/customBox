from types import SimpleNamespace

LABEL_KEY 		= "label"
TYPE_KEY 		= "type"
TOOLTIP_KEY		= "tooltip"
INHERIT_KEY		= "inherit"
PLACEHOLDER_KEY	= "placeholder"
VALIDATION_KEY	= "validation"

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

	def __init__(self, attribute_definition: dict):
		# internal helpers
		self._is_inherited 			= False
		self._attribute_definition 	= attribute_definition.copy()
		self._value					= None
		# required properties
		self.label 					= None
		self.type					= None
		# optional properties
		self.tooltip 				= ""
		self.validation				= ""
		self.hidden					= False
		self._is_placeholder		= False
		if(PLACEHOLDER_KEY in self._attribute_definition):
			self._is_placeholder = self._attribute_definition[PLACEHOLDER_KEY]

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
	def needsLinking(self):
		return self._needs_linking

	@property
	def is_placeholder(self):
		return self._is_placeholder

	@property
	def is_inherited(self):
		return self._is_inherited

	@classmethod
	def is_type(cls, type: str) -> bool:
		if(cls._comparison_type is None):
			return False
		else:
			return type == cls._comparison_type

	def create_inheritor(self, inherit_properties: dict):
		overwriteWith = inherit_properties.copy()
		del overwriteWith[INHERIT_KEY]
		newAttributeDefinition = self._attribute_definition.copy()
		newAttributeDefinition.update(overwriteWith)
		newAttribute = parseAttribute(newAttributeDefinition)
		newAttribute._is_inherited = True
		return newAttribute


class StringType(AttributeType):
	_comparison_type = "string"

	@overrides(AttributeType)
	def getDefault(self):
		return ""

class BoolType(AttributeType):
	_comparison_type = "bool"

	@overrides(AttributeType)
	def getDefault(self):
		return False

class IntType(AttributeType):
	_comparison_type = "int"

	@overrides(AttributeType)
	def getDefault(self):
		return int(0)

class FloatType(AttributeType):
	_comparison_type = "float"

	@overrides(AttributeType)
	def getDefault(self):
		return float(0)

class ReferenceListType(AttributeType):
	_comparison_type 	= "referenceList"
	_needs_linking		= True

	@overrides(AttributeType)
	def getDefault(self):
		return []

class StringListType(AttributeType):
	_comparison_type = "stringList"

	@overrides(AttributeType)
	def getDefault(self):
		return []

class SelectionType(AttributeType):
	_comparison_type 	= "selection"
	_needs_linking		= True

	@overrides(AttributeType)
	def getDefault(self):
		return ""

class HexType(AttributeType):
	_comparison_type = "hex"

	@overrides(AttributeType)
	def getDefault(self):
		return int(0)

class SliderType(AttributeType):
	_comparison_type = "slider"

	@overrides(AttributeType)
	def getDefault(self):
		return int(0)


attributeTypeList = [StringType, BoolType, IntType, FloatType, ReferenceListType, StringListType, SelectionType, SelectionType, HexType, SliderType]


def parseAttribute(attributeDefinition: dict):
	if(not TYPE_KEY in attributeDefinition):
		raise KeyError("Type key is required for every attribute but it is missing")
	parseType = attributeDefinition[TYPE_KEY]
	newAttribute = None
	for attribType in attributeTypeList:
		if(attribType.is_type(parseType)):
			newAttribute = attribType(attributeDefinition)
			break
	if(newAttribute is None):
		raise KeyError(f"The type {parseType} is not a supported type")
	return newAttribute
