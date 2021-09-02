from __future__ 				import annotations
import hashlib
from typing 					import Dict, List, Union
from pathlib 					import Path
import Parser
from Parser.LinkElement 		import Link
import Parser.Serializer 		as serializer
import Parser.VersionHandling 	as vh
from Parser.helpers 			import overrides
import Parser.AttributeTypes 	as AttributeTypes
import Parser.constants			as const
import json

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

class UiViewType():
	def __init__(self, key):
		self.key = key

class UiViewTypes():
	tabbed 		= UiViewType(const.UI_VIEW_TYPE_TABBED_KEY)
	carded 		= UiViewType(const.UI_VIEW_TYPE_CARDED_KEY)
	__allTypes 	= [tabbed, carded]

	@staticmethod
	def getViewType(type: str):
		for t in UiViewTypes.__allTypes:
			if(t.key == type):
				return t
		return None

class UiPage():
	def __init__(self, label: str, viewType: UiViewType, icon: str = None):
		self.label 		= label
		self.icon 		= icon
		self.viewType 	= viewType
		self.assignedSubconfigs: Dict[str, Subconfig] = dict()

	def assignSubconfig(self, name: str, config: Subconfig):
		self.assignedSubconfigs[name] = config

class UiConfiguration(dynamicObject):
	def __init__(self):
		forbidden 		= 'Creating a user interface page with the name "{0}" is not permitted as "{0}" is a reserved keyword'
		duplicated 		= 'It was requested to create a user interface page named "{0}" but a page with that name already exists'
		doesNotExist 	= 'Config has no UI page named "{0}"'
		super().__init__("UiConfiguration", forbidden, duplicated, doesNotExist)

	@property
	def pages(self) -> Dict[str, UiPage]:
		return self._getItems()

	def createpage(self, id: str, pageDefinition: Dict[str,str]) -> UiPage:
		for requiredKey in const.ui_page_required_json_keys:
			if(requiredKey not in pageDefinition):
				raise KeyError(f'A UI page with the name "{id}" could not be created because it\'s definition is missing the reqired "{requiredKey}" key.')
			if(const.UI_TAB_ICON_KEY in pageDefinition):
				icon = pageDefinition[const.UI_TAB_ICON_KEY]
			else:
				icon = None
			viewType = UiViewTypes.getViewType(pageDefinition[const.UI_VIEW_TYPE_KEY])
		return self._create(id, UiPage(pageDefinition[const.UI_TAB_LABEL_KEY], viewType, icon))

	def haspage(self, id: str):
		return self._has(id)

	def getpage(self, id: str) -> UiPage:
		return self._get(id)

class Configuration(dynamicObject):
	def __init__(self, attribute_lookup: Dict[str, AttributeTypes.AttributeType]):
		self.__attribute_lookup = attribute_lookup
		self.UiConfig 	= UiConfiguration()
		forbidden 		= 'Creating a subconfig with the name "{0}" is not permitted as "{0}" is a reserved keyword'
		duplicated 		= 'It was requested to create a subconfig named "{0}" but a subconfig with that name already exists'
		doesNotExist 	= 'Config has no subconfig named "{0}"'
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
	def configs(self) -> Dict[str, Subconfig]:
		return self._getItems()

	@property
	def attribute_lookup(self):
		return self.__attribute_lookup

	def createSubconfigFromDefinition(self, configName: str, config: dict, source_file: Path):
		file_version = vh.Version(config[const.VERSION_KEY])
		if(not vh.CompatabilityManager.is_compatible(file_version)):
			config = vh.CompatabilityManager.upgrade(config)
		subconfig = self.createSubconfig(configName, source_file, config[const.VERSION_KEY], config[const.CHECKSUM_KEY])
		for element in config[const.ELEMENTS_KEY]:
			currentElement = config[const.ELEMENTS_KEY][element]
			newElement = subconfig.createElement(element)
			if(not type(currentElement) is list):
				raise Exception(f'In config "{configName}" the "{const.ELEMENTS_KEY}" property is required to be a list but found {type(currentElement)}')
			for attributeInstance in currentElement:
				newElement.createAttributeInstanceFromDefinition(attributeInstance)
		if(const.UI_PAGE_KEY in config):
			for pageName, uiPage in config[const.UI_PAGE_KEY].items():
				self.UiConfig.createpage(pageName, uiPage)
		if(const.UI_KEY in config):
			if(const.UI_USE_PAGE_KEY in config[const.UI_KEY]):
				subconfig.assignToUiPage(config[const.UI_KEY][const.UI_USE_PAGE_KEY])

	def createSubconfig(self, name: Union[str,Link], source_file: Path, file_format_version: str = None, file_element_hash: int = None) -> Subconfig:
		link = Link.force(name, Link.EMPHASIZE_CONFIG)
		if(not file_format_version):
			file_format_version = Parser.FILE_FORMAT_VERSION
		return self._create(link.config, Subconfig(link.config, self, source_file, file_format_version, file_element_hash))

	def hasSubConfig(self, name: Union[str,Link]):
		link = Link.force(name, Link.EMPHASIZE_CONFIG)
		return self._has(link.config)

	def getSubconfig(self, name: Union[str,Link]) -> Subconfig:
		link = Link.force(name, Link.EMPHASIZE_CONFIG)
		return self._get(link.config)

	def serialize(self):
		for subconfig in self.configs.values():
			Data = dict()
			with subconfig.source_file.open("r") as fp:
				Data = json.load(fp)
			Data.update(serializer.serialize(subconfig))
			with subconfig.source_file.open("w") as fp:
				json.dump(Data, fp, indent = '\t')
			subconfig._file_elements_hash = subconfig.elements_hash


class Subconfig(dynamicObject, serializer.serializeable):
	def __init__(self, name: str, parent: Configuration, source_file: Path, file_format_version: str, file_element_hash: int = None):
		self.__link								= Link.construct(config=name)  # example: cores/
		self.__parent: Configuration			= parent
		self.__source_config_file: Path			= source_file
		self.__ui_page_assignment				= None
		self.__file_format_version				= vh.Version(file_format_version)
		self._file_elements_hash				= file_element_hash
		if(not vh.CompatabilityManager.is_compatible(self.__file_format_version)):
			raise ValueError(f'The file structure of "{str(source_file)}" is specified as version "{str(file_format_version)}" but this version is not compatible with the parser which is on version {vh.CompatabilityManager.get_current_version()}')

		forbidden = f'Creating an element with the name "{{0}}" in the subconfig "{self.link.config}" is not permitted as "{{0}}" is a reserved keyword'
		duplicated = f'The creation of a new element named "{{0}}" was requested for subconfig "{self.link.config}" but an element with that name already exists for this subconfig'
		doesNotExist = f'Tried to get element "{{0}}" from subconfig "{self.link.config}" but this subconfig has no element with that name'
		super().__init__("Subconfig", forbidden, duplicated, doesNotExist)

	@property
	def elements(self) -> Dict[str, ConfigElement]:
		return self._getItems()

	@property
	def link(self):
		return self.__link

	@property
	def parent(self):
		return self.__parent

	@property
	def source_file(self):
		return self.__source_config_file

	@property
	def file_format_version(self):
		return self.__file_format_version

	@property
	def elements_hash(self):
		own_elements = self._serialize_elements()
		return self.__get_dict_hash(own_elements)

	@property
	def file_elements_hash(self):
		return self._file_elements_hash

	def __get_dict_hash(self, input):
		str			= json.dumps(input).encode('utf-8')
		str_hash 	= hashlib.md5(str).hexdigest()
		return str_hash

	def needs_serialization(self):
		return self.elements_hash != self._file_elements_hash

	def hasElement(self, name: Union[str, Link]):
		elementLink = Link.force(name, Link.EMPHASIZE_ELEMENT)
		return self._has(elementLink.element)

	def createElement(self, name: Union[str, Link], ) -> ConfigElement:
		elementLink = Link.force(name, Link.EMPHASIZE_ELEMENT)
		elementName = elementLink.element
		return self._create(elementName, ConfigElement(elementName, self))

	def getElement(self, name: Union[str, Link]) -> ConfigElement:
		elementLink = Link.force(name, Link.EMPHASIZE_ELEMENT)
		return self._get(elementLink.element)

	def assignToUiPage(self, page_id: str):
		self.__ui_page_assignment = page_id

	def _serialize_elements(self):
		data = dict()
		for element_name, element in self.elements.items():
			data[element_name] = serializer.serialize(element)
		return data

	def _serialize_attributes(self):
		attributes = dict()
		for attribute in self.parent.attribute_lookup.values():
			attribute: AttributeTypes.AttributeType
			if(attribute.globalID.config == self.link.config):
				name, attributeDef = attribute.serialize_attribute()
				attributes[name] = attributeDef
		return attributes

	@overrides(serializer.serializeable)
	def _serialize(self):
		data = dict()
		data[const.VERSION_KEY] 	= str(self.__file_format_version)
		serialized_elements 		= self._serialize_elements()
		serialized_attributes 		= self._serialize_attributes()
		data[const.ELEMENTS_KEY] 	= serialized_elements
		data[const.ATTRIBUTES_KEY] 	= serialized_attributes
		data[const.CHECKSUM_KEY] 	= self.__get_dict_hash(serialized_elements)
		return data

	def resolveUiAssignment(self):
		if(self.__ui_page_assignment):
			if(type(self.__ui_page_assignment) is str):
				if(self.parent.UiConfig.haspage(self.__ui_page_assignment)):
					self.__ui_page_assignment = self.parent.UiConfig.getpage(self.__ui_page_assignment)
					self.__ui_page_assignment.assignSubconfig(self.__link.config, self)
				else:
					raise ValueError(f'The subconfig "{self.__link}" was assigned to a UI page named "{self.__ui_page_assignment}" but a page with that name does not exist')

class ConfigElement(dynamicObject, serializer.serializeable):
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

	@overrides(serializer.serializeable)
	def _serialize(self) -> Dict:
		serialized_data = list()
		for attribute in self.attributeInstances.values():
			serialized_data.append(serializer.serialize(attribute))
		return serialized_data

	def getAttribute(self, name: str) -> Union[AttributeInstance, ReferenceCollection]:
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

	def createAttributeInstance(self, target: Link, value = None, attributeName: str = None):
		attribute_lookup 				= self.parent.parent.attribute_lookup
		targetLink 						= Link.force(target, Link.EMPHASIZE_ATTRIBUTE)
		targetLink 						= self.link.merge(targetLink, Link.EMPHASIZE_ATTRIBUTE)
		attribute_lookup_key 			= targetLink.getLink(Element=False)
		if(targetLink.attribute in self.__dict__):
			raise KeyError(f'Creating an attribute instance named "{targetLink.attribute}" within the element "{self.link}" is not permitted as "{targetLink.attribute}" is a reserved keyword')
		if(not attribute_lookup_key in attribute_lookup):
			raise KeyError(f'Target attribute "{attribute_lookup_key}" could not be found')
		targetedAttribute 				= attribute_lookup[attribute_lookup_key]
		AttributeInstanceLink 			= self.link.copy()
		AttributeInstanceLink.attribute = targetedAttribute.id
		if(attributeName):
			AttributeInstanceLink.attribute = attributeName
		if(targetedAttribute.is_placeholder):
			if(value is not None):
				raise Exception(f'Element "{self.link}" instantiates the attribute definition "{AttributeInstanceLink}" which is a placeholder but the value key ist also defined, which is an invalid combination for placeholder entries.')
			newAttributeInstance = AttributeInstance(AttributeInstanceLink, self, targetedAttribute)
		elif(value is not None):
			newAttributeInstance = AttributeInstance(AttributeInstanceLink, self, targetedAttribute, value)
		else:
			raise ValueError(f'The attribute instance for "{self.link}" could not be created because there was no value provided which is mandatory for attributes which are not placeholders')
		return self._create(targetedAttribute.id, newAttributeInstance)

	def createAttributeInstanceFromDefinition(self, element_definition: dict):
		if(not const.TARGET_KEY in element_definition):
			raise KeyError(f'Error creating an attribute instance in "{self.parent.link}", Element definition "{element_definition}" is missing the mandatory key "{const.TARGET_KEY}"')
		target = element_definition[const.TARGET_KEY]
		name_overwrite = None
		value = None
		if(const.TARGET_NAME_OVERWRITE_KEY in element_definition):
			name_overwrite = element_definition[const.TARGET_NAME_OVERWRITE_KEY]
		if(const.VALUE_KEY in element_definition):
			value = element_definition[const.VALUE_KEY]
		return self.createAttributeInstance(target, value, name_overwrite)

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

class AttributeInstance(serializer.serializeable):
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

	@overrides(serializer.serializeable)
	def _serialize(self) -> Dict:
		own_subconfig = self.parent.parent.link
		return self.__attribute.serialize_value(self.value, own_subconfig)

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
