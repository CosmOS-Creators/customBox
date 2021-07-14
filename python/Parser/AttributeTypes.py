import re
import Parser.ConfigTypes 	as ConfigTypes
import Parser.helpers		as helpers
from typing 				import List, Union
from Parser.helpers 		import overrides
from Parser.LinkElement		import Link

LABEL_KEY 					= "label"
TYPE_KEY 					= "type"
TOOLTIP_KEY					= "tooltip"
INHERIT_KEY					= "inherit"
PLACEHOLDER_KEY				= "placeholder"
HIDDEN_KEY					= "hidden"
PARENT_REFERENCE_TYPE_KEY	= "parentReference"
# special keys
VALIDATION_KEY				= "validation"
ELEMENTS_KEY				= "elements"
STEP_KEY					= "step"
MIN_KEY						= "min"
MAX_KEY						= "max"

baseKeys = [LABEL_KEY, TOOLTIP_KEY, HIDDEN_KEY, PLACEHOLDER_KEY, TYPE_KEY]

class AttributeType():
	""" Base class attribute type. Specifics should be overwritten in inherited classes
		The base type itself should never be instantiated.
	"""
	_comparison_type 		= None
	_needs_linking			= False
	_typeSpecificKeys		= []

	def __init__(self, attribute_definition: dict, globalID: str):
		# internal helpers
		self._is_inherited 			= False
		self._attribute_definition 	= attribute_definition.copy()

		# check if any forbidden keys exist:
		try:
			self.checkForForbiddenKeys(self._typeSpecificKeys)
		except KeyError as e:
			raise KeyError(f"Error in attribute \"{globalID}\" of type \"{self._comparison_type}\" : {str(e)}")

		# special helpers
		self._is_placeholder 		= self.checkForKey(PLACEHOLDER_KEY, False)
		# required properties
		self.globalID 				= globalID
		self.id 					= globalID.split("/")[1]

		error_message = "Attribute \"" + self.globalID + "\" is missing the required \"{}\" key."
		if(TYPE_KEY in attribute_definition):
			self.type 				= attribute_definition[TYPE_KEY]
		else:
			raise AttributeError(error_message.format(TYPE_KEY))

		# optional properties
		self.tooltip 				= self.checkForKey(TOOLTIP_KEY, "")
		self.hidden 				= self.checkForKey(HIDDEN_KEY, False)
		if(LABEL_KEY in attribute_definition):
			self.label 				= attribute_definition[LABEL_KEY]
		elif(self.hidden == False and not self._is_placeholder and not self.type == PARENT_REFERENCE_TYPE_KEY):
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
		return valueInput

	def link(self, objConfig: ConfigTypes.Configuration, targetConfigObject: ConfigTypes.ConfigElement, targetAttributeName: str, fromPopulate: bool = False):
		pass

	def checkForForbiddenKeys(self, listOfAllowedKeys: List[str]):
		global baseKeys
		AllAllowedKeys = baseKeys + listOfAllowedKeys
		for key in self._attribute_definition:
			if(not key in AllAllowedKeys):
				raise KeyError(f"The key \"{key}\" is not valid for this attribute type")

	def checkForKey(self, key: str, defaultValue):
		if(key in self._attribute_definition):
			return self._attribute_definition[key]
		else:
			return defaultValue

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
	_comparison_type 	= "string"
	_typeSpecificKeys	= [VALIDATION_KEY]

	@overrides(AttributeType)
	def __init__(self, attribute_definition: dict, globalID: str):
		super().__init__(attribute_definition, globalID)
		self.validation = self.checkForKey(VALIDATION_KEY, "")

	@overrides(AttributeType)
	def checkValue(self, valueInput: str):
		if(self.validation != ""):
			try:
				regex = re.compile(self.validation)
			except Exception as e:
				raise ValueError(f"The regex \"{self.validation}\" is not valid: \"{str(e)}\"")
			if(not type(valueInput) is str):
				reportValidationError(f"Input value \"{valueInput}\" is not of type str but the attribute definition was expecting a string")
			if(not regex.match(valueInput)):
				reportValidationError(f"\"{valueInput}\" does not match the validation regex \"{self.validation}\"")
		return valueInput

	@overrides(AttributeType)
	def getDefault(self) -> str:
		return str("")

class BoolType(AttributeType):
	_comparison_type 	= "bool"

	@overrides(AttributeType)
	def checkValue(self, valueInput: bool):
		return valueInput

	@overrides(AttributeType)
	def getDefault(self) -> bool:
		return False

class IntType(AttributeType):
	_comparison_type 	= "int"
	_typeSpecificKeys	= [MIN_KEY, MAX_KEY]

	@overrides(AttributeType)
	def __init__(self, attribute_definition: dict, globalID: str):
		super().__init__(attribute_definition, globalID)
		self.min 			= self.checkForKey(MIN_KEY, None)
		self.max 			= self.checkForKey(MAX_KEY, None)

	@overrides(AttributeType)
	def checkValue(self, valueInput: int):
		if(not self.min is None):
			if(valueInput < self.min):
				reportValidationError(f"The input value ({valueInput}) is lower than the minimum value({self.min}) for this attribute")
		if(not self.max is None):
			if(valueInput > self.max):
				reportValidationError(f"The input value ({valueInput}) is higher than the maximum value({self.min}) for this attribute")
		return int(valueInput)

	@overrides(AttributeType)
	def getDefault(self) -> int:
		return int(0)

class FloatType(IntType):
	_comparison_type 	= "float"

	@overrides(AttributeType)
	def getDefault(self) -> float:
		return float(0)

class ReferenceListType(AttributeType):
	_comparison_type 	= "referenceList"
	_needs_linking		= True
	_typeSpecificKeys	= [ELEMENTS_KEY]

	@overrides(AttributeType)
	def __init__(self, attribute_definition: dict, globalID: str):
		super().__init__(attribute_definition, globalID)
		self.elements: List[Link] = self.checkForKey(ELEMENTS_KEY, None)
		if(not self.elements is None):
			if(not type(self.elements) is list):
				raise TypeError(f'The elements property must always be a list for reference list attribute types but found type "{type(self.elements)}" instead for attribute "{self.globalID}"')
			elementLinks = []
			for i, element in enumerate(self.elements):
				try:
					link = Link.force(element)
				except Exception as e:
					raise Exception(f'Every list item of the elements property of the attribute "{self.globalID}" has to be a link but parsing of item {i} was unsuccessful: {str(e)}')
				elementLinks.append(link)
			self.elements = elementLinks

	@overrides(AttributeType)
	def checkValue(self, valueInput: List[Union[str, Link, ConfigTypes.ConfigElement]]):
		# just check the syntax here as no info about any valid choices is avaliable and validation will be done in the link method
		if(type(valueInput) is list):
			for i, value in enumerate(valueInput):
				if(type(value) is str or type(value) is Link):
					if(not Link.isGlobal(value)):
						raise ValueError(f"All elements of a reference list must be global links but element {i} ({value}) was not")
				elif(type(value) is ConfigTypes.ConfigElement):
					if(not value.link.isValidElementLink()):
						raise ValueError(f"Reference list for attribute \"{self.globalID}\" contained a ConfigElement object with an invalid link. The link \"{value.link.getLink()}\" cannot be used to link to an element")
		else:
			raise TypeError(f"Values of reference list attribute types must be of type list but found type \"{type(valueInput)}\" instead")
		return valueInput

	@overrides(AttributeType)
	def getDefault(self) -> List[ConfigTypes.ConfigElement]:
		return []

	@overrides(AttributeType)
	def link(self, objConfig: ConfigTypes.Configuration, targetConfigObject: ConfigTypes.ConfigElement, targetAttributeName: Union[Link, str], fromPopulate: bool = False):
		targetAttributeLink = Link.force(targetAttributeName, emphasize=Link.EMPHASIZE_ATTRIBUTE)
		value = getattr(targetConfigObject, targetAttributeLink.attribute)
		if(not type(value) is list):
			raise TypeError(f"Values for elements of reference list attribute types must be of type list but found type \"{type(value)}\" instead")
		linkedTargets = []
		if(not self.elements is None):
			objConfig.require(self.elements)
		for targetLink in value:
			link = Link.force(targetLink)
			if(not self.elements is None):
				linkFoundMatch = False
				for element in self.elements:
					if(element.config == link.config):
						linkFoundMatch = True
				if(linkFoundMatch == False):
					raise ValueError(f'Error for attribute definition \"{self.globalID}\": Provided link in the value list ({link.getLink()}) does not match any of the allowed links for this attributes reference list ({self.elements})')
			try:
				targetElement = link.resolveElement(objConfig)
			except AttributeError as e:
				raise AttributeError(f"Error for attribute definition \"{self.globalID}\" while resolving references: {str(e)}")
			linkedTargets.append(targetElement)
		if(fromPopulate):
			targetConfigObject._setattr_direct(targetAttributeLink.attribute, linkedTargets)
		else:
			setattr(targetConfigObject, targetAttributeLink.attribute, linkedTargets)

class StringListType(AttributeType):
	_comparison_type 	= "stringList"

	@overrides(AttributeType)
	def checkValue(self, valueInput: List[str]):
		# The only requirement here is for the value to be of type list.
		if(type(valueInput) is list):
			for i, item in enumerate(valueInput):
				if(not type(item) is str):
					raise ValueError(f"All elements of a string list must be strings but element {i} was not. Found type \"{type(item)}\" instead")
		else:
			raise TypeError(f"Values of string list attribute types must be of type list but found type \"{type(valueInput)}\" instead")
		return valueInput

	@overrides(AttributeType)
	def getDefault(self) -> List[str]:
		return []

class SelectionType(AttributeType):
	_comparison_type 	= "selection"
	_needs_linking		= True
	_typeSpecificKeys	= [ELEMENTS_KEY]

	@overrides(AttributeType)
	def __init__(self, attribute_definition: dict, globalID: str):
		super().__init__(attribute_definition, globalID)
		if(ELEMENTS_KEY in attribute_definition):
			self.elements 			= attribute_definition[ELEMENTS_KEY]
			self.resolvedElements	= None
			if(type(self.elements) is list):
				self._needs_linking		= False
			elif(type(self.elements) is str):
				self._needs_linking		= True
			else:
				raise TypeError(f"Attribute \"{self.globalID}\" only allows string and list types for \"{ELEMENTS_KEY}\" property but found type \"{type(self.elements)}\"")
		else:
			raise AttributeError(f"Property \"{ELEMENTS_KEY}\" is required for type \"{self._comparison_type}\" but was missing for attribute \"{self.globalID}\"")

	@overrides(AttributeType)
	def checkValue(self, valueInput: str):
		if(type(self.elements) is list):
			if(not valueInput in self.elements):
				reportValidationError(f"The input value ({valueInput}) does not match any of the specified elements ({self.elements})")
		return valueInput

	@overrides(AttributeType)
	def getDefault(self) -> ConfigTypes.ConfigElement:
		return None

	@overrides(AttributeType)
	def link(self, objConfig: ConfigTypes.Configuration, targetConfigObject: ConfigTypes.ConfigElement, targetAttributeName: Union[Link, str], fromPopulate: bool = False):
		if(self._needs_linking):
			possibleValues = []
			foundMatch = False
			link = Link(self.elements)
			targetAttributeLink = Link.force(targetAttributeName, emphasize=Link.EMPHASIZE_ATTRIBUTE)
			try:
				subconfig = link.resolveSubconfig(objConfig)
			except AttributeError as e:
				raise AttributeError(f"Error for attribute definition \"{self.globalID}\" while resolving references: {str(e)}")
			for element in subconfig.iterator:
				try:
					targetValue = getattr(element, link.element)
				except AttributeError:
					print(f"WARNING: Attribute definition \"{self.globalID}\" requested an attribute instance named \"{link.element}\" from the config \"{link.config}\" but the element \"{element.id}\" does not have an instance of that attribute. Skipping this element.")
					continue
				possibleValues.append(targetValue)
				value = getattr(targetConfigObject, targetAttributeLink.attribute)
				if(value == targetValue):
					setattr(targetConfigObject, targetAttributeLink.attribute, element)
					foundMatch = True
			if(self.resolvedElements is None):
				self.resolvedElements = possibleValues
			if(foundMatch == False):
				raise NameError(f"\"{value}\" is not a valid choice for Attribute instances of \"{self.globalID}\". Valid choices are: {possibleValues}")

class HexType(IntType):
	_comparison_type 	= "hex"
	_typeSpecificKeys	= [MIN_KEY, MAX_KEY]

	@overrides(AttributeType)
	def checkValue(self, valueInput: str):
		convertedInput = helpers.toInt(valueInput)
		if(not self.min is None):
			convertedMin = helpers.toInt(self.min)
			if(convertedInput < convertedMin):
				reportValidationError(f"The input value ({valueInput}) is lower than the minimum value({self.min}) for this attribute")
		if(not self.max is None):
			convertedMax = helpers.toInt(self.max)
			if(convertedInput > convertedMax):
				reportValidationError(f"The input value ({valueInput}) is higher than the maximum value({self.min}) for this attribute")
		return convertedInput

	@overrides(AttributeType)
	def getDefault(self) -> int:
		return int(0)

class SliderType(IntType):
	_comparison_type 	= "slider"
	_typeSpecificKeys	= [MIN_KEY, MAX_KEY, STEP_KEY]

	@overrides(AttributeType)
	def __init__(self, attribute_definition: dict, globalID: str):
		super().__init__(attribute_definition, globalID)
		self.step 			= self.checkForKey(STEP_KEY, 1)

	@overrides(AttributeType)
	def checkValue(self, valueInput: int):
		super().checkValue(valueInput)
		if(not self.step is None):
			if(valueInput % self.step != 0):
				raise ValueError(f"The value of a slider attribute must be a multiple of {self.step} but {valueInput} is not.")
		return valueInput

	@overrides(AttributeType)
	def getDefault(self) -> float:
		return int(0)

class ParentReferenceType(AttributeType):
	_comparison_type 	= "parentReference"
	_needs_linking		= True

	@overrides(AttributeType)
	def __init__(self, attribute_definition: dict, globalID: str):
		if(HIDDEN_KEY in attribute_definition or PLACEHOLDER_KEY in attribute_definition):
			raise KeyError(f"Attributes of type parent reference are not allowed to contain either the \"{HIDDEN_KEY}\" nor the \"{PLACEHOLDER_KEY}\" key.")
		super().__init__(attribute_definition, globalID)

	@overrides(AttributeType)
	def checkValue(self, valueInput: List[str]):
		# just check if it is a valid link syntax
		try:
			link = Link.parse(valueInput)
		except Exception as e:
			reportValidationError(f"Values of type parent reference must have a link valid link. But parsing the link \"{valueInput}\" threw errors: {str(e)}")
		if(not link.config or not link.element or link.attribute):
			reportValidationError(f"Values of type parent reference must have a link which points to another config element but \"{valueInput}\" does not.")
		return valueInput

	@overrides(AttributeType)
	def getDefault(self) -> None:
		return None

	@overrides(AttributeType)
	def link(self, objConfig: ConfigTypes.Configuration, targetConfigObject: ConfigTypes.ConfigElement, targetAttributeName: Union[Link, str], fromPopulate: bool = False):
		targetAttributeLink = Link.force(targetAttributeName, emphasize=Link.EMPHASIZE_ATTRIBUTE)
		value = getattr(targetConfigObject, targetAttributeLink.attribute)
		link = Link.force(value)
		parentElement = link.resolveElement(objConfig)
		targetObjectLink = Link.force(targetConfigObject.link)

		# add this object to the parent
		if(hasattr(parentElement, targetObjectLink.config)):
			temp = getattr(parentElement, targetObjectLink.config)
			if(type(temp) is ConfigTypes.ConfigElement):
				raise AttributeError(f"Error during linking the element \"{targetObjectLink.getLink()}\" to the parent element \"{link.getLink()}\": The parent already has an attribute with the name \"{targetObjectLink.config}\"")
		else:
			temp = ConfigTypes.Subconfig(None)
			setattr(parentElement, targetObjectLink.config, temp)

		temp.iterator.append(targetConfigObject)
		if(hasattr(temp, targetObjectLink.element)):
			raise Exception(f"In config \"{targetObjectLink.config}\" in element \"{targetObjectLink.element}\" is was requested to create an element for the parent object \"{link.getLink()}\" but a property with the name \"{link.element}\" already exists.")
		else:
			setattr(temp, targetObjectLink.element, targetConfigObject)
		# add the parent to this object
		if(fromPopulate):
			targetConfigObject._setattr_direct(targetAttributeLink.attribute, parentElement)
		else:
			setattr(targetConfigObject, targetAttributeLink.attribute, parentElement)

attributeTypeList = [StringType, BoolType, IntType, FloatType, ReferenceListType, StringListType, SelectionType, SelectionType, HexType, SliderType, ParentReferenceType]

def reportValidationError(errorMsg: str):
	raise ValueError(errorMsg)

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
		raise KeyError(f"The type \"{parseType}\" is not a supported type")
	return newAttribute
