from __future__ 				import annotations
from types 						import SimpleNamespace
from typing 					import Dict, List, Union
from Parser.LinkElement 		import Link
from Parser.helpers 			import overrides
import Parser.AttributeTypes 	as AttributeTypes
import Parser.constants			as const

def formatConfig(config: Configuration, indent: int = 1):
	stringRepresentation = ""
	indentStr = " "*indent
	crossingStr = "|-"
	lineStr = "|"
	for name, subconfig in config.configs.items():
		stringRepresentation += f'{crossingStr}Subconfig({name})\n'
		for name, configElement in subconfig.elements.items():
			stringRepresentation += f'{lineStr}{indentStr}{crossingStr}ConfigElement({name})\n'
			for name, attributeInstance in configElement.attributeInstances.items():
				stringRepresentation += f'{lineStr}{indentStr}{lineStr}{indentStr}{crossingStr}AttributeInstance({name}: {attributeInstance.value})\n'
			for name, reference in configElement.references.items():
				stringRepresentation += f'{lineStr}{indentStr}{lineStr}{indentStr}{crossingStr}Reference({name}: {reference})\n'
	return stringRepresentation

class dynamicObject:
	def __init__(self, className: str, nameClashError: str, duplicatedError: str, notExistantError: str):
		self.dynamic_items 			= dict()
		self.__name_clash_error 	= nameClashError
		self.__duplicate_error		= duplicatedError
		self.__non_existant_error	= notExistantError
		self.__class_name 			= className
		self.initFinished 			= True

	def __repr__(self):
		return f"{self.__class_name}({list(self.dynamic_items.values())})"

	def __iter__(self):
		return iter(self.dynamic_items.values())

	def __len__(self):
		return len(self.dynamic_items)

	def _getItems(self):
		return self.dynamic_items

	def _create(self, name: str, element):
		if(name in self.__dict__):
			raise AttributeError(self.__name_clash_error.format(name))
		if(name in self.dynamic_items):
			raise AttributeError(self.__duplicate_error.format(name))
		self.dynamic_items[name] = element
		return element

	def _has(self, name: str):
		return name in self.dynamic_items

	def _get(self, name: str):
		items = object.__getattribute__(self, 'dynamic_items')
		if(name in items):
			return items[name]
		else:
			raise AttributeError(self.__non_existant_error.format(name))

	def __setattr__(self, name, value):
		own_attribs = object.__getattribute__(self, '__dict__')
		if("initFinished" in own_attribs):
			if(name in own_attribs):
				object.__setattr__(self, name, value)
			else:
				try:
					object.__getattribute__(self, 'dynamic_items')[name] = value
				except (KeyError, AttributeError):
					object.__setattr__(self, name, value)
		else:
			object.__setattr__(self, name, value)

	def __getattribute__(self, name):
		try:
			return object.__getattribute__(self, name)
		except AttributeError:
			return self._get(name)

class Configuration(dynamicObject):
	def __init__(self):
		forbidden = 'Creating a subconfig with the name "{0}" is not permitted as "{0}" is a reserved keyword'
		duplicated = 'It was requested to create a subconfig named "{0}" but a subconfig with that name already exists'
		doesNotExist = 'Config has no subconfig named "{0}"'
		super().__init__("Configuration", forbidden, duplicated, doesNotExist)

	def require(self, requiredProperties : Union[List[Union[str, Link]], Union[str, Link]]):
		if(not type(requiredProperties) is list):
			requiredProperties = [requiredProperties]
		for prop in requiredProperties:
			link = Link.force(prop, Link.EMPHASIZE_CONFIG)
			try:
				link.resolve(self)
			except Exception as e:
				raise AttributeError(f'The link "{link}" was listed as required but it could not be resolved: {str(e)}')

	@property
	def configs(self):
		return self._getItems()

	def createSubconfig(self, name: Union[str,Link]) -> Subconfig:
		link = Link.force(name, Link.EMPHASIZE_CONFIG)
		return self._create(link.config, Subconfig(link.config, self))

	def hasSubConfig(self, name: Union[str,Link]):
		link = Link.force(name, Link.EMPHASIZE_CONFIG)
		return self._has(link.config)

	def getSubconfig(self, name: Union[str,Link]) -> Subconfig:
		link = Link.force(name, Link.EMPHASIZE_CONFIG)
		return self._get(link.config)


class Subconfig(dynamicObject):
	def __init__(self, name: str, parent: Configuration):
		self.__link								= Link.construct(config=name)  # example: cores/
		self.__parent: Configuration			= parent
		forbidden = f'Creating an element with the name "{{0}}" in the subconfig "{self.link.config}" is not permitted as "{{0}}" is a reserved keyword'
		duplicated = f'The creation of a new element named "{{0}}" was requested for subconfig "{self.link.config}" but an element with that name already exists for this subconfig'
		doesNotExist = f'Tried to get element "{{0}}" from subconfig "{self.link.config}" but this subconfig has no element with that name'
		super().__init__("Subconfig", forbidden, duplicated, doesNotExist)

	def hasElement(self, name: Union[str, Link]):
		elementLink = Link.force(name, Link.EMPHASIZE_ELEMENT)
		return self._has(elementLink.element)

	def createElement(self, name: Union[str, Link]) -> ConfigElement:
		elementLink = Link.force(name, Link.EMPHASIZE_ELEMENT)
		elementName = elementLink.element
		return self._create(elementName, ConfigElement(elementName, self))

	def getElement(self, name: Union[str, Link]) -> ConfigElement:
		elementLink = Link.force(name, Link.EMPHASIZE_ELEMENT)
		return self._get(elementLink.element)

	@property
	def elements(self) -> List[ConfigElement]:
		return self._getItems()

	@property
	def link(self):
		return self.__link

	@property
	def parent(self):
		return self.__parent

class ConfigElement(dynamicObject):
	def __init__(self, name: str, parent: Subconfig):
		self.__name 				= name
		self.__link					= parent.link.copy()
		self.__link.element			= name 				# example: cores/core_0
		self.__parent				= parent
		forbidden = f'Creating an attribute named "{{0}}" within the element "{self.link}" is not permitted as "{{0}}" is a reserved keyword'
		duplicated = f'The creation of a new attribute named "{{0}}" was requested for element "{self.link}" but an attribute with that name already exists for this element'
		doesNotExist = f'Tried to get attribute "{{0}}" from element "{self.link}" but this element has no attribute with that name'
		super().__init__("ConfigElement", forbidden, duplicated, doesNotExist)

	@overrides(dynamicObject)
	def __repr__(self):
		return f"ConfigElement({self.__name})"

	@property
	def link(self):
		return self.__link

	@property
	def parent(self):
		return self.__parent

	@property
	def attributes(self) -> Dict[str, Union[ReferenceCollection, AttributeInstance]]:
		return self._getItems()

	@property
	def attributeInstances(self) -> Dict[str, AttributeInstance]:
		AttributeInstances = dict()
		items = self._getItems()
		for name, item in items.items():
			itemValue = self._get(name)
			if(type(itemValue) is AttributeInstance):
				AttributeInstances[name] = itemValue
		return AttributeInstances

	@property
	def references(self) -> Dict[str, ReferenceCollection]:
		References = dict()
		items = self._getItems()
		for name, item in items.items():
			itemValue = self._get(name)
			if(type(itemValue) is ReferenceCollection):
				References[name] = itemValue
		return References

	def getAttribute(self, name: str):
		return self._get(name)

	def addReferenceObject(self, name: str, objectLinkName: str, ObjectLink):
		if(self._has(name)):
			item = self._get(name)
			if(not type(item) is ReferenceCollection):
				raise AttributeError(f'The creation of a new reference object named "{name}" was requested for element "{self.link}" but an attribute instanace with that name already exists for this element')
		else:
			item = self._create(name, ReferenceCollection(name, self))
		item.addReference(objectLinkName, ObjectLink)

	def getReferenceObject(self, name: str) -> ReferenceCollection:
		item = self._get(name)
		if(not type(item) is ReferenceCollection):
			raise TypeError(f'The requested reference object named "{name}" from element "{self.link}" was not of type ReferenceCollection instead it was of type "{type(item)}"')
		return item

	def hasAttributeInstance(self, name: Union[str, Link]):
		attributeInstanceLink = Link.force(name, Link.EMPHASIZE_ATTRIBUTE)
		return self._has(attributeInstanceLink.attribute)

	def getAttributeInstance(self, name: Union[str, Link]) -> AttributeInstance:
		AttributeInstanceLink = Link.force(name, Link.EMPHASIZE_ATTRIBUTE)
		item = self._get(AttributeInstanceLink.attribute)
		if(not type(item) is AttributeInstance):
			raise TypeError(f'The requested reference object named "{name}" from element "{self.link}" was not of type AttributeInstance instead it was of type "{type(item)}"')
		return item

	def createAttributeInstance(self, element_definition: dict, attribute_lookup: dict[str,AttributeTypes.AttributeType]):
		if(not const.TARGET_KEY in element_definition):
			raise KeyError(f'Error creating an attribute instance in "{self.parent.link}", Element definition "{element_definition}" is missing the mandatory key "{const.TARGET_KEY}"')
		targetLink = Link.force(element_definition[const.TARGET_KEY], Link.EMPHASIZE_ATTRIBUTE)
		targetLink = self.link.merge(targetLink, Link.EMPHASIZE_ATTRIBUTE)
		attribute_lookup_key = targetLink.getLink(Element=False)
		if(targetLink.attribute in self.__dict__):
			raise KeyError(f'Creating an attribute instance named "{targetLink.attribute}" within the element "{self.link}" is not permitted as "{targetLink.attribute}" is a reserved keyword')
		if(not attribute_lookup_key in attribute_lookup):
			raise KeyError(f'Target attribute "{attribute_lookup_key}" could not be found')
		targetedAttribute 							= attribute_lookup[attribute_lookup_key]
		AttributeInstanceLink 						= self.link.copy()
		AttributeInstanceLink.attribute 			= targetedAttribute.id
		if(const.TARGET_NAME_OVERWRITE_KEY in element_definition):
			AttributeInstanceLink.attribute = element_definition[const.TARGET_NAME_OVERWRITE_KEY]
		if(targetedAttribute.is_placeholder):
			if(const.VALUE_KEY in element_definition):
				raise Exception(f'Element "{self.link}" instantiates the attribute definition "{AttributeInstanceLink}" which is a placeholder but the value key ist also defined, which is an invalid combination for placeholder entries.')
			newAttributeInstance = AttributeInstance(AttributeInstanceLink, self, targetedAttribute)
		elif(const.VALUE_KEY in element_definition): # this is a normal attribute instance
			newAttributeInstance = AttributeInstance(AttributeInstanceLink, self, targetedAttribute, element_definition[const.VALUE_KEY])
		else:
			raise Exception(f'Invalid attribute instance formatting in element "{self.link}". The following element definition is missing the "{const.VALUE_KEY}" property: {element_definition}')
		return self._create(targetedAttribute.id, newAttributeInstance)

	def populate(self, property_name: str, value, isPlaceholder: bool = True):
		attributeInstance = self.getAttributeInstance(property_name)
		attributeInstance.populate(value, isPlaceholder)

	@overrides(dynamicObject)
	def __setattr__(self, name, value):
		own_attribs = object.__getattribute__(self, '__dict__')
		if("initFinished" in own_attribs):
			if(name in own_attribs):
				object.__setattr__(self, name, value)
			else:
				try:
					object.__getattribute__(self, 'dynamic_items')[name].value = value
				except (KeyError, AttributeError):
					object.__setattr__(self, name, value)
		else:
			object.__setattr__(self, name, value)

	@overrides(dynamicObject)
	def __getattribute__(self, name):
		try:
			return object.__getattribute__(self, name)
		except AttributeError:
			items = object.__getattribute__(self, 'dynamic_items')
			if(name in items):
				return items[name].value
			else:
				error_msg = object.__getattribute__(self, '_dynamicObject__non_existant_error')
				raise AttributeError(error_msg.format(name))

class AttributeInstance(SimpleNamespace):
	def __init__(self, name: Union[str, Link], parent: ConfigElement, attribute: AttributeTypes.AttributeType, value = None):
		link = Link.force(name, Link.EMPHASIZE_ATTRIBUTE)
		self.__attribute 		= attribute
		self.__link 			= parent.link.copy() #example: cores/core_0:name
		self.__link.attribute	= link.attribute
		self.__configLookup 	= parent.parent.parent
		self.__parent			= parent
		if(attribute.is_placeholder and value is None):
			self.__value = attribute.getDefault()
		elif(type(value) is AttributeInstance or type(value) is ConfigElement):
			self.__value = value
		else:
			self.__value = attribute.checkValue(value)

	def __repr__(self):
		return f"AttributeInstance({self.__attribute.id}: {self.__value})"

	def setValueDirect(self, value):
		self.__value = value

	@property
	def value(self):
		return self.__value

	@property
	def datatype(self):
		return self.__attribute.type

	@property
	def attributeDefinition(self):
		return self.__attribute

	@property
	def link(self):
		return self.__link

	@property
	def parent(self):
		return self.__parent

	@value.setter
	def value(self, value):
		self.populate(value)

	def ResolveValueLink(self):
		self.__attribute.link(self.__configLookup, self)

	def populate(self, value, isPlaceholder: bool = True):
		"""
			Populate any attribute with a value. If the attribute is not a placeholder isPlaceholder has to be set to False explicitly
		"""
		if(not self.__attribute.is_placeholder and isPlaceholder == True):
			raise AttributeError(f"Element \"{self.__link.getLink(Attribute=False)}\" is not a placeholder but the populate method was expecting a placeholder attribute. If a non placeholder attribute should be written to on purpose call populate with isPlaceholder set to False")
		try:
			self.__value = self.__attribute.checkValue(value)
		except ValueError as e:
			raise ValueError(f"Error validating the new value for the placeholder \"{self.__link}\": {str(e)}")

		try:
			self.ResolveValueLink()
		except Exception as e:
			raise Exception(f'Error while linking element "{self.__link}" of type "{self.__attribute.type}": {str(e)}')

class ReferenceCollection(dynamicObject):
	def __init__(self, name: Union[str, Link], parent: ConfigElement):
		link = Link.force(name, Link.EMPHASIZE_ATTRIBUTE)
		self.__link 			= parent.link.copy() #example: cores/core_0:name
		self.__link.attribute	= link.attribute
		self.__parent			= parent
		forbidden = f'Creating a reference with the name "{{0}}" is not permitted as "{{0}}" is a reserved keyword'
		duplicated = f'The creation of a new reference named "{{0}}" was requested but a reference with that name already exists for this reference collection'
		doesNotExist = f'Tried to get reference "{{0}}" from reference collection but this reference collection has no reference with that name'
		super().__init__("ReferenceCollection", forbidden, duplicated, doesNotExist)

	@property
	def link(self):
		return self.__link

	@property
	def parent(self):
		return self.__parent

	@property
	def references(self):
		return self._getItems()

	def hasReference(self, name: str):
		return self._has(name)

	def addReference(self, name: str, value):
		return self._create(name, value)

	def getReference(self, name: str):
		return self._get(name)
