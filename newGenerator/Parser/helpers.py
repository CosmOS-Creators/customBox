from __future__ import annotations
from typing import List, Union

import Parser.ConfigTypes as ConfigTypes
import Parser.AttributeTypes as AttributeTypes

# helper decorator to ensure proper naming of functions
def overrides(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider

class Link():
	def __init__(self, link: str = None):
		self.isGlobal 			= self.__isGlobal
		if(link):
			self.config, self.element, self.attribute = self.split(link)
		else:
			self.config 		= None
			self.element		= None
			self.attribute		= None

	def __repr__(self):
		return "Link(" + self.getLink() + ")"

	def __str__(self) -> str:
		return self.getLink()

	def __eq__(self, o: Link) -> bool:
		return o.config == self.config and o.element == self.element and o.attribute == self.attribute

	def __hash__(self) -> int:
		return hash((self.config, self.element, self.attribute))

	@staticmethod
	def split(link: str):
		config 		= None
		element 	= None
		attribute 	= None
		temp = link.split(":")
		if(len(temp) == 2):
			attribute = temp[1]
			temp = temp[0].split("/")
			if(len(temp) == 2):
				config = temp[0]
				element = temp[1]
			else:
				element = temp[0]
		elif(len(temp) == 1):
			temp = temp[0].split("/")
			if(len(temp) == 2):
				config = temp[0]
				element = temp[1]
			else:
				element = temp[0]
		else:
			raise ValueError(f"The link \"{link}\" does not have a valid format in the form of \"config/element:attribute\"")
		if(not config):
			config = None
		if(not element):
			element = None
		if(not attribute):
			attribute = None
		return config, element, attribute

	@staticmethod
	def construct(config: str = None, element: str = None, attribute: str = None):
		newLink = Link()
		newLink.set(config, element, attribute)
		return newLink

	@staticmethod
	def parse(link: str):
		newLink = Link(link)
		return newLink

	@staticmethod
	def isGlobal(link: Union[str, Link]):
		newLink = forceLink(link)
		if(newLink.config):
			return True
		else:
			return False

	def __isGlobal(self):
		if(self.config):
			return True
		else:
			return False

	def isValidElementLink(self):
		return (not self.config is None) and (not self.element is None)

	def set(self, config: str = None, element: str = None, attribute: str = None):
		self.config		= config
		self.element	= element
		self.attribute	= attribute

	def getLink(self, Config: bool = True, Element: bool = True, Attribute: bool = True) -> str:
		config 			= self.config if not self.config is None else ""
		element 		= self.element if not self.element is None else ""
		attribute 		= self.attribute if not self.attribute is None else ""
		if(Config == False):
			config 		= ""
		if(Element == False):
			element 	= ""
		if(Attribute == False):
			attribute 	= ""
		if(self.attribute):
			return f"{config}/{element}:{attribute}"
		elif(self.element):
			return f"{config}/{element}"
		else:
			return config

	def __getSubconfig(self, config: ConfigTypes.Configuration) -> ConfigTypes.Subconfig:
		try:
			return getattr(config, self.config)
		except AttributeError:
			raise AttributeError(f"Error resolving link \"{self.getLink()}\": Config has no subconfig named \"{self.config}\"")

	def __getElement(self, subconfig: ConfigTypes.Subconfig) -> ConfigTypes.ConfigElement:
		try:
			return getattr(subconfig, self.element)
		except AttributeError:
			raise AttributeError(f"Error resolving link \"{self.getLink()}\": subconfig \"{self.config}\" has no element named \"{self.element}\"")

	def __getAttribute(self, element: ConfigTypes.ConfigElement) -> AttributeTypes.AttributeType:
		try:
			return getattr(element, self.attribute)
		except AttributeError:
			raise AttributeError(f"Error resolving link \"{self.getLink()}\": element \"{element.id}\" has no attribute named \"{self.attribute}\"")

	def resolveElement(self, config: ConfigTypes.Configuration) -> ConfigTypes.ConfigElement:
		if(self.config and self.element):
			subconfig = self.__getSubconfig(config)
			return self.__getElement(subconfig)
		else:
			raise ValueError(f"The link \"{self.getLink()}\" cannot be resolved. Either the config or the element part of the link are missing but they are mandatory for resolving an element.")

	def resolveAttributeList(self, config: ConfigTypes.Configuration) -> list[AttributeTypes.AttributeType]:
		subconfig = self.__getSubconfig(config)
		if(self.config and self.attribute):
			attributeCollection = []
			for element in subconfig.iterator:
				targetAttribute = self.__getAttribute(element)
				attributeCollection.append({"target": targetAttribute, "element": element})
			return attributeCollection
		else:
			raise ValueError(f"The link \"{self.getLink()}\" cannot be resolved. Either the config or the attribute part of the link are missing but they are mandatory for resolving an attribute list.")

	def resolveAttribute(self, config: ConfigTypes.Configuration) -> AttributeTypes.AttributeType:
		if(self.config and self.attribute and self.element):
			subconfig = self.__getSubconfig(config)
			element = self.__getElement(subconfig)
			return self.__getAttribute(element)
		else:
			raise ValueError(f"The link \"{self.getLink()}\" cannot be resolved as it is missing at least one part. All three parts of the link are mandatory for resolving an attribute value.")

	def resolveSubconfig(self, config: ConfigTypes.Configuration) -> ConfigTypes.Subconfig:
		if(self.config):
			return self.__getSubconfig(config)
		else:
			raise ValueError(f"The link \"{self.getLink()}\" cannot be resolved. The link is missing the config part which is mandatory for resolving subconfigs.")

	def resolve(self, config: ConfigTypes.Configuration) -> Union[ConfigTypes.ConfigElement, list[AttributeTypes.AttributeType], AttributeTypes.AttributeType, ConfigTypes.Subconfig]:
		if(self.config is None):
			raise AttributeError(f"For resolving a link at least the config must be set.")
		if(self.config and self.element and not self.attribute): # link to an element
			return self.resolveElement(config)
		elif(self.config and not self.element and self.attribute): # link to list of attributes of all elements in config
			return self.resolveAttributeList(config)
		elif(self.config and self.attribute and self.element): # link to the value of an attribute inside an element
			return self.resolveAttribute(config)
		elif(self.config and not self.element and not self.attribute): # link to a subconfig
			return self.resolveSubconfig(config)
		else:
			raise ValueError(f"The link \"{self.getLink()}\" cannot be resolved as it is missing at least one part of the link.")

	@property
	def parts(self):
		return self.config, self.element, self.attribute

	@property
	def config(self):
		return self.__config

	@config.setter
	def config(self, value):
		if(value):
			if("/" in value):
				raise ValueError(f"A link part is not allowed to contain a \"/\" character. But the config part \"{value}\" does.")
		self.__config = value

	@property
	def element(self):
		return self.__element

	@element.setter
	def element(self, value):
		if(value):
			if("/" in value):
				raise ValueError(f"A link part is not allowed to contain a \"/\" character. But the element part \"{value}\" does.")
		self.__element = value

	@property
	def attribute(self):
		return self.__attribute

	@attribute.setter
	def attribute(self, value):
		if(value):
			if("/" in value):
				raise ValueError(f"A link part is not allowed to contain a \"/\" character. But the attribute part \"{value}\" does.")
		self.__attribute = value

def forceLink(input: Union[Link, str, ConfigTypes.ConfigElement]) -> Link:
	if(input is None):
		return Link()
	if(type(input) is Link):
		return input
	elif(type(input) is ConfigTypes.ConfigElement):
		return input.link
	elif(type(input) is str):
		return Link(input)
	else:
		raise TypeError(f'Inputs of type "{type(input)}" cannot be converted to a Link object')

def toInt(hexValue: str):
	return int(hexValue, 16)

def toHex(intValue: int):
	return hex(intValue)

def forceStrList(input: Union[List[str], str]):
	out = input
	valid = True
	if(type(input) is str):
		out = [input]
	else:
		if(type(input) is list):
			for item in input:
				if(not type(item) is str):
					valid = False
					break
		else:
			valid = False
		if(valid == False):
			raise TypeError(f"Allowed types are only str or List[str] but found type \"{str(type(input))}\" instead.")
	return out
