LABEL_KEY 		= "label"
TYPE_KEY 		= "type"
TOOLTIP_KEY		= "tooltip"
INHERIT_KEY		= "inherit"
PLACEHOLDER_KEY	= "placeholder"
VALIDATION_KEY	= "validation"


class AttributeType():
	def __init__(self, attribute_definition: dict):
		# internal helpers
		self._is_inherited 			= False
		self._attribute_definition 	= attribute_definition.copy()
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


	def getDefault(self):
		return 0

	@property
	def is_placeholder(self):
		return self._is_placeholder

	@property
	def is_inherited(self):
		return self._is_inherited

	def create_inheritor(self, inherit_properties: dict):
		overwriteWith = inherit_properties.copy()
		del overwriteWith[INHERIT_KEY]
		newAttributeDefinition = self._attribute_definition.copy()
		newAttributeDefinition.update(overwriteWith)
		newAttribute = parseAttribute(newAttributeDefinition)
		newAttribute._is_inherited = True
		return newAttribute


class StringType(AttributeType):

	def getDefault(self):
		return ""

class BoolType(AttributeType):

	def getDefault(self):
		return False

class IntType(AttributeType):

	def getDefault(self):
		return int(0)

class FloatType(AttributeType):

	def getDefault(self):
		return float(0)

class ReferenceListType(AttributeType):
	def getDefault(self):
		return []

class StringListType(AttributeType):
	def getDefault(self):
		return []

class SelectionType(AttributeType):
	def getDefault(self):
		return ""

class HexType(AttributeType):
	def getDefault(self):
		return int(0)

class SliderType(AttributeType):
	def getDefault(self):
		return int(0)


def parseAttribute(attributeDefinition: dict):
	if(not TYPE_KEY in attributeDefinition):
		raise KeyError("Type key is required for every attribute but it is missing")
	newAttribute = AttributeType(attributeDefinition)
	return newAttribute
