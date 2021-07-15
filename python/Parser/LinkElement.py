
from __future__ 				import annotations
from typing 					import List, Union

import Parser.ConfigTypes 		as ConfigTypes
import Parser.AttributeTypes 	as AttributeTypes

class Link():
	EMPHASIZE_CONFIG	= 0
	EMPHASIZE_ELEMENT	= 1
	EMPHASIZE_ATTRIBUTE	= 2

	def __init__(self, link: str = None, emphasize: int = EMPHASIZE_ELEMENT):
		self.isGlobal 			= self.__isGlobal
		if(link):
			self.config, self.element, self.attribute = self.split(link, emphasize)
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
	def split(link: str, emphasize: int):
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
				if(emphasize == Link.EMPHASIZE_CONFIG):
					config = temp[0]
				elif(emphasize == Link.EMPHASIZE_ELEMENT):
					element = temp[0]
				elif(emphasize == Link.EMPHASIZE_ATTRIBUTE):
					attribute = temp[0]
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
		newLink = Link.force(link)
		if(newLink.config):
			return True
		else:
			return False

	@staticmethod
	def force(input: Union[Link, str, ConfigTypes.ConfigElement, ConfigTypes.AttributeInstance], emphasize: int = EMPHASIZE_ELEMENT) -> Link:
		if(input is None):
			return Link()
		if(type(input) is Link):
			return input
		elif(type(input) is ConfigTypes.ConfigElement or
			 type(input) is ConfigTypes.AttributeInstance):
			return input.link
		elif(type(input) is str):
			return Link(input, emphasize)
		else:
			raise TypeError(f'Inputs of type "{type(input)}" cannot be converted to a Link object')

	def __isGlobal(self):
		if(self.config):
			return True
		else:
			return False

	def isValidElementLink(self):
		return (not self.config is None) and (not self.element is None)

	def set(self, config: str = None, element: str = None, attribute: str = None):
		self.config: str	= config
		self.element: str	= element
		self.attribute:str	= attribute

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

	def resolveElement(self, config: ConfigTypes.Configuration) -> ConfigTypes.ConfigElement:
		if(self.config and self.element):
			subconfig = config.getSubconfig(self)
			return subconfig.getElement(self)
		else:
			raise ValueError(f"The link \"{self.getLink()}\" cannot be resolved. Either the config or the element part of the link are missing but they are mandatory for resolving an element.")

	def resolveAttributeList(self, config: ConfigTypes.Configuration) -> List[AttributeTypes.AttributeType]:
		subconfig = config.getSubconfig(self)
		if(self.config and self.attribute):
			attributeCollection = []
			for element in subconfig.iterator:
				targetAttribute = element.getAttributeInstance(self)
				attributeCollection.append({"target": targetAttribute, "element": element})
			return attributeCollection
		else:
			raise ValueError(f"The link \"{self.getLink()}\" cannot be resolved. Either the config or the attribute part of the link are missing but they are mandatory for resolving an attribute list.")

	def resolveAttribute(self, config: ConfigTypes.Configuration) -> AttributeTypes.AttributeType:
		if(self.config and self.attribute and self.element):
			subconfig = config.getSubconfig(self)
			element = subconfig.getElement(self)
			return element.getAttributeInstance(self)
		else:
			raise ValueError(f"The link \"{self.getLink()}\" cannot be resolved as it is missing at least one part. All three parts of the link are mandatory for resolving an attribute value.")

	def resolveSubconfig(self, config: ConfigTypes.Configuration) -> ConfigTypes.Subconfig:
		if(self.config):
			return config.getSubconfig(self)
		else:
			raise ValueError(f"The link \"{self.getLink()}\" cannot be resolved. The link is missing the config part which is mandatory for resolving subconfigs.")

	def resolve(self, config: ConfigTypes.Configuration) -> Union[ConfigTypes.ConfigElement, List[AttributeTypes.AttributeType], AttributeTypes.AttributeType, ConfigTypes.Subconfig]:
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

	def copy(self):
		return Link.construct(config=self.config, element=self.element, attribute=self.attribute)

	def merge(self, override: Union[str, Link], emphasize: int = EMPHASIZE_ELEMENT):
		overrideLink = Link.force(override, emphasize)
		mergedLink = self.copy()
		if(overrideLink.config):
			mergedLink.config = overrideLink.config
		if(overrideLink.element):
			mergedLink.element = overrideLink.element
		if(overrideLink.attribute):
			mergedLink.attribute = overrideLink.attribute
		return mergedLink

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
