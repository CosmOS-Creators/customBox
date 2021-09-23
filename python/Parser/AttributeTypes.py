from collections import OrderedDict
import re
import Parser.ConfigTypes 	as ConfigTypes
import Parser.helpers		as helpers
import Parser.constants		as const
from typing 				import List, Type, Union
from Parser.helpers 		import overrides
from Parser.LinkElement		import Link

class AttributeType():
	""" Base class attribute type. Specifics should be overwritten in inherited classes
		The base type itself should never be instantiated.
	"""
	_comparison_type 		= None
	_needs_linking			= False
	_typeSpecificKeys		= []

	def __init__(self, attribute_definition: dict, globalID: Union[Link, str]):
		globalID = Link.force(globalID, Link.EMPHASIZE_ATTRIBUTE)
		if(globalID.isGlobal()):
			if(not globalID.hasAttribute()):
				raise ValueError(f'An attribute link must have a attribute name specified but "{globalID}" did not')
		else:
			raise ValueError(f'An attribute link must be global but "{globalID}" was not.')
		# internal helpers
		self._inherit_from: AttributeType	= None
		self._attribute_definition 			= attribute_definition.copy()

		# check if any forbidden keys exist:
		try:
			self.checkForForbiddenKeys(self._typeSpecificKeys)
		except KeyError as e:
			raise KeyError(f'Error in attribute "{globalID}" of type "{self._comparison_type}" : {str(e)}')

		# special helpers
		self._is_placeholder 		= self.checkForKey(const.PLACEHOLDER_KEY, False)
		# required properties
		self.globalID 				= globalID
		self.id 					= globalID.attribute

		if(const.TYPE_KEY in attribute_definition):
			self.type 				= attribute_definition[const.TYPE_KEY]
		else:
			raise AttributeError(f'Attribute "{self.globalID}" is missing the required "{const.TYPE_KEY}" key.')

		# optional properties
		self.tooltip 				= self.checkForKey(const.TOOLTIP_KEY, "")
		self.hidden 				= self.checkForKey(const.HIDDEN_KEY, False)
		self.label					= self.checkForKey(const.LABEL_KEY, "")

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

	def link(self, objConfig: ConfigTypes.Configuration, attributeInstance: ConfigTypes.AttributeInstance):
		pass

	def checkForForbiddenKeys(self, listOfAllowedKeys: List[str]):
		global baseKeys
		AllAllowedKeys = const.baseKeys + listOfAllowedKeys
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
		return self._inherit_from is not None

	@classmethod
	def is_type(cls, type: str) -> bool:
		if(cls._comparison_type is None):
			return False
		else:
			return type == cls._comparison_type

	def create_inheritor(self, inherit_properties: dict, globalID: str):
		overwriteWith 				= inherit_properties.copy()
		del overwriteWith[const.INHERIT_KEY]
		newAttributeDefinition 		= self._attribute_definition.copy()
		newAttributeDefinition.update(overwriteWith)
		newAttribute 				= parseAttribute(newAttributeDefinition, globalID)
		newAttribute._inherit_from 	= self
		return newAttribute

	def _serialize_value(self, value):
		return value

	def serialize_value(self, value, context: Link = None):
		target = str(self.globalID)
		if(context):
			if(context.config == self.globalID.config):
				target = self.globalID.attribute
		data = {
			const.TARGET_KEY: target
			}
		if(not self.is_placeholder):
			data[const.VALUE_KEY] = self._serialize_value(value)
		return data

	def _get_serialization_specifics(self):
		return OrderedDict()

	def serialize_attribute(self):
		attributeDef = OrderedDict()
		attributeDef[const.TYPE_KEY] = self.type
		if(self.label):
			attributeDef[const.LABEL_KEY] = self.label
		if(self.tooltip):
			attributeDef[const.TOOLTIP_KEY] = self.tooltip
		if(self.hidden):
			attributeDef[const.HIDDEN_KEY] = self.hidden
		if(self.is_placeholder):
			attributeDef[const.PLACEHOLDER_KEY] = self.is_placeholder

		serialization_specifics = self._get_serialization_specifics()
		for specific_key, specific_value in serialization_specifics.items():
			attributeDef[specific_key] = specific_value

		if(self.is_inherited):
			non_modified_keys = list()
			_ ,inherited_attrib_def = self._inherit_from.serialize_attribute()
			for property_key, attrib_property in attributeDef.items():
				if(property_key in inherited_attrib_def):
					if(inherited_attrib_def[property_key] == attrib_property):
						non_modified_keys.append(property_key)
			for key in non_modified_keys:
				del attributeDef[key]
			attributeDef[const.INHERIT_KEY] = str(self._inherit_from.globalID)
		return self.id, attributeDef

class StringType(AttributeType):
	_comparison_type 	= "string"
	_typeSpecificKeys	= [const.VALIDATION_KEY]

	@overrides(AttributeType)
	def __init__(self, attribute_definition: dict, globalID: str):
		super().__init__(attribute_definition, globalID)
		self.validation = self.checkForKey(const.VALIDATION_KEY, "")

	@overrides(AttributeType)
	def checkValue(self, valueInput: str):
		if(not type(valueInput) is str):
			reportValidationError(f"Input value \"{valueInput}\" is not of type str but the attribute definition was expecting a string")
		if(self.validation != ""):
			try:
				regex = re.compile(self.validation)
			except Exception as e:
				raise ValueError(f"The regex \"{self.validation}\" is not valid: \"{str(e)}\"")
			if(not regex.match(valueInput)):
				reportValidationError(f"\"{valueInput}\" does not match the validation regex \"{self.validation}\"")
		return valueInput

	@overrides(AttributeType)
	def getDefault(self) -> str:
		return str("")

	@overrides(AttributeType)
	def _get_serialization_specifics(self):
		specifics = OrderedDict()
		if(self.validation is not None):
			specifics[const.VALIDATION_KEY] = self.validation
		return specifics

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
	_typeSpecificKeys	= [const.MIN_KEY, const.MAX_KEY]

	@overrides(AttributeType)
	def __init__(self, attribute_definition: dict, globalID: str):
		super().__init__(attribute_definition, globalID)
		self.min 			= self.checkForKey(const.MIN_KEY, None)
		self.max 			= self.checkForKey(const.MAX_KEY, None)

	def _checkMinMax(self, value):
		if(type(value) is int or type(value) is float):
			if(not self.min is None):
				if(value < self.min):
					reportValidationError(f"The input value ({value}) is lower than the minimum value({self.min}) for this attribute")
			if(not self.max is None):
				if(value > self.max):
					reportValidationError(f"The input value ({value}) is higher than the maximum value({self.max}) for this attribute")
			return value
		else:
			reportValidationError(f"The input value ({value}) must be of type int or float but got type ({type(value)}) instead")

	@overrides(AttributeType)
	def checkValue(self, valueInput):
		return int(self._checkMinMax(valueInput))

	@overrides(AttributeType)
	def getDefault(self) -> int:
		return int(0)

	@overrides(AttributeType)
	def _get_serialization_specifics(self):
		specifics = OrderedDict()
		if(self.min is not None):
			specifics[const.MIN_KEY] = self.min
		if(self.max is not None):
			specifics[const.MAX_KEY] = self.max
		return specifics

class FloatType(IntType):
	_comparison_type 	= "float"

	@overrides(AttributeType)
	def getDefault(self) -> float:
		return float(0)

	@overrides(AttributeType)
	def checkValue(self, valueInput):
		return float(self._checkMinMax(valueInput))

class ReferenceListType(AttributeType):
	_comparison_type 	= "referenceList"
	_needs_linking		= True
	_typeSpecificKeys	= [const.ELEMENTS_LIST_KEY]

	@overrides(AttributeType)
	def __init__(self, attribute_definition: dict, globalID: str):
		super().__init__(attribute_definition, globalID)
		self.elements: List[Link] = self.checkForKey(const.ELEMENTS_LIST_KEY, None)
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
	def link(self, objConfig: ConfigTypes.Configuration, attributeInstance: ConfigTypes.AttributeInstance):
		if(not type(attributeInstance.value) is list):
			raise TypeError(f"Values for elements of reference list attribute types must be of type list but found type \"{type(attributeInstance.value)}\" instead")
		linkedTargets = []
		if(not self.elements is None):
			objConfig.require(self.elements)
		for targetLink in attributeInstance.value:
			link = Link.force(targetLink)
			if(not self.elements is None):
				linkFoundMatch = False
				for element in self.elements:
					if(element.config == link.config):
						linkFoundMatch = True
						break
				if(linkFoundMatch == False):
					raise ValueError(f'Error for attribute definition \"{self.globalID}\": Provided link in the value list ({link.getLink()}) does not match any of the allowed links for this attributes reference list ({self.elements})')
			try:
				targetElement = link.resolveElement(objConfig)
			except AttributeError as e:
				raise AttributeError(f"Error for attribute definition \"{self.globalID}\" while resolving references: {str(e)}")
			linkedTargets.append(targetElement.getObjReference(linkedTargets))
		attributeInstance.setValueDirect(linkedTargets)

	@overrides(AttributeType)
	def _serialize_value(self, value: List[ConfigTypes.ConfigElement]):
		data = list()
		for v in value:
			data.append(str(v.link))
		return data

	@overrides(AttributeType)
	def _get_serialization_specifics(self):
		specifics = OrderedDict()
		if(self.elements is not None):
			elements_str = list()
			for elementLink in self.elements:
				elements_str.append(str(elementLink))
			specifics[const.ELEMENTS_LIST_KEY] = elements_str
		return specifics

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
	_typeSpecificKeys	= [const.ELEMENTS_LIST_KEY]

	@overrides(AttributeType)
	def __init__(self, attribute_definition: dict, globalID: str):
		super().__init__(attribute_definition, globalID)
		if(const.ELEMENTS_LIST_KEY in attribute_definition):
			self.elements: Union[str, list[str]] 			= attribute_definition[const.ELEMENTS_LIST_KEY]
			self.resolvedElements: Union[None, ]	= None
			self.targetedAttribute	= None
			if(type(self.elements) is list):
				self._needs_linking		= False
			elif(type(self.elements) is str):
				self._needs_linking		= True
			else:
				raise TypeError(f"Attribute \"{self.globalID}\" only allows string and list types for \"{const.ELEMENTS_LIST_KEY}\" property but found type \"{type(self.elements)}\"")
		else:
			raise AttributeError(f"Property \"{const.ELEMENTS_LIST_KEY}\" is required for type \"{self._comparison_type}\" but was missing for attribute \"{self.globalID}\"")

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
	def link(self, objConfig: ConfigTypes.Configuration, attributeInstance: ConfigTypes.AttributeInstance):
		if(self._needs_linking):
			possibleValues = []
			foundMatch = False
			link = Link(self.elements, Link.EMPHASIZE_ELEMENT)
			try:
				subconfig = link.resolveSubconfig(objConfig)
			except AttributeError as e:
				raise AttributeError(f"Error for attribute definition \"{self.globalID}\" while resolving references: {str(e)}")
			for name, element in subconfig.elements.items():
				element: ConfigTypes.ConfigElement = element
				if(not link.hasAttribute()):
					raise ValueError(f'The link "{link}" for the allowed elements of the attribute {self.globalID} seems to be invalid. Make sure the link is in the format of "config/:attribute"')
				if(element.hasAttributeInstance(link.attribute)):
					targetValue = element.getAttribute(link.attribute)
				else:
					print(f"WARNING: Attribute definition \"{self.globalID}\" requested an attribute instance named \"{link.element}\" from the config \"{link.config}\" but the element \"{name}\" does not have an instance of that attribute. Skipping this element.")
					continue
				possibleValues.append(targetValue)
				if(attributeInstance.value == targetValue.value or attributeInstance.value == targetValue):
					attributeInstance.setValueDirect(targetValue.parent.getObjReference(attributeInstance))
					foundMatch = True
					if(self.resolvedElements is not None):
						break
			if(self.resolvedElements is None):
				self.resolvedElements = possibleValues
				self.targetedAttribute = link.attribute
			if(foundMatch == False):
				raise NameError(f'"{attributeInstance.value}" is not a valid choice for Attribute instances of "{self.globalID}". Valid choices are: {possibleValues}')

	@overrides(AttributeType)
	def _serialize_value(self, value: Union[ConfigTypes.ConfigElement, str]):
		if(type(value) is str):
			return value
		else:
			attr = self.targetedAttribute
			return str(value.getAttribute(attr).value)

	@overrides(AttributeType)
	def _get_serialization_specifics(self):
		specifics = OrderedDict()
		if(self.elements is not None):
			specifics[const.ELEMENTS_LIST_KEY] = self.elements
		return specifics


class HexType(IntType):
	_comparison_type 	= "hex"
	_typeSpecificKeys	= [const.MIN_KEY, const.MAX_KEY]

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

	@overrides(AttributeType)
	def _serialize_value(self, value):
		return helpers.toHex(value)

class SliderType(IntType):
	_comparison_type 	= "slider"
	_typeSpecificKeys	= [const.MIN_KEY, const.MAX_KEY, const.STEP_KEY]

	@overrides(AttributeType)
	def __init__(self, attribute_definition: dict, globalID: str):
		super().__init__(attribute_definition, globalID)
		self.step 			= self.checkForKey(const.STEP_KEY, 1)

	@overrides(AttributeType)
	def checkValue(self, valueInput: int):
		super().checkValue(valueInput)
		if(not self.step is None):
			if(valueInput % self.step != 0):
				raise ValueError(f"The value of a slider attribute must be a multiple of {self.step} but {valueInput} is not.")
		return valueInput

	@overrides(AttributeType)
	def getDefault(self) -> float:
		return float(0)

	@overrides(AttributeType)
	def _get_serialization_specifics(self):
		specifics = OrderedDict()
		if(self.min is not None):
			specifics[const.MIN_KEY] = self.min
		if(self.max is not None):
			specifics[const.MAX_KEY] = self.max
		if(self.step is not None):
			specifics[const.STEP_KEY] = self.step
		return specifics

class ParentReferenceType(AttributeType):
	_comparison_type 	= "parentReference"
	_needs_linking		= True

	@overrides(AttributeType)
	def __init__(self, attribute_definition: dict, globalID: str):
		if(const.HIDDEN_KEY in attribute_definition or const.PLACEHOLDER_KEY in attribute_definition):
			raise KeyError(f"Attributes of type parent reference are not allowed to contain either the \"{const.HIDDEN_KEY}\" nor the \"{const.PLACEHOLDER_KEY}\" key.")
		super().__init__(attribute_definition, globalID)

	@overrides(AttributeType)
	def checkValue(self, valueInput: Union[Link, str]):
		# just check if it is a valid link syntax
		try:
			link = Link.force(valueInput)
		except Exception as e:
			reportValidationError(f"Values of type parent reference must have a link valid link. But parsing the link \"{valueInput}\" threw errors: {str(e)}")
		if(not link.hasConfig() or not link.hasElement() or link.hasAttribute()):
			reportValidationError(f"Values of type parent reference must have a link which points to another config element but \"{valueInput}\" does not.")
		return valueInput

	@overrides(AttributeType)
	def getDefault(self) -> None:
		return None

	@overrides(AttributeType)
	def link(self, objConfig: ConfigTypes.Configuration, attributeInstance: ConfigTypes.AttributeInstance):
		linkTarget 		= Link.force(attributeInstance.value, Link.EMPHASIZE_ELEMENT)
		selfElement 	= attributeInstance.link.resolveElement(objConfig)
		targetedElement = linkTarget.resolveElement(objConfig)
		targetedElement.addReferenceObject(attributeInstance.link.config, attributeInstance.link.element, selfElement)
		targetedElement.getObjReference(attributeInstance.parent)
		attributeInstance.setValueDirect(targetedElement)

	@overrides(AttributeType)
	def _serialize_value(self, value: ConfigTypes.ConfigElement):
		if(value is None):
			raise ValueError(f'Serialization of attribute {self.globalID.attribute} failed as it is of type {self._comparison_type} and is not allowed to be None.')
		return str(value.link)

attributeTypeList = [StringType, BoolType, IntType, FloatType, ReferenceListType, StringListType, SelectionType, SelectionType, HexType, SliderType, ParentReferenceType]

def reportValidationError(errorMsg: str):
	raise ValueError(errorMsg)

def parseAttribute(attributeDefinition: dict, AttributeGlobalID: Union[Link, str]) -> AttributeType:
	if(not const.TYPE_KEY in attributeDefinition):
		raise KeyError("Type key is required for every attribute but it is missing")
	parseType = attributeDefinition[const.TYPE_KEY]
	newAttribute = None
	for attribType in attributeTypeList:
		if(attribType.is_type(parseType)):
			newAttribute = attribType(attributeDefinition, AttributeGlobalID)
			break
	if(newAttribute is None):
		raise KeyError(f"The type \"{parseType}\" is not a supported type")
	return newAttribute
