
from __future__ 				import annotations
from typing 					import List, Tuple, Union

import Parser.ConfigTypes 		as ConfigTypes
import Parser.AttributeTypes 	as AttributeTypes

class Link():
	EMPHASIZE_CONFIG	= 0
	EMPHASIZE_ELEMENT	= 1
	EMPHASIZE_ATTRIBUTE	= 2

	def __init__(self, link: Union[str, Link] = None, emphasize: int = EMPHASIZE_ELEMENT):
		self.isGlobal 			= self.__isGlobal
		if(link):
			if(type(link) is str):
				self.__config, self.__element, self.__attribute = self.split(link, emphasize)
			elif(type(link) is Link):
				self.__config, self.__element, self.__attribute = link.parts
			else:
				raise TypeError(f'Link elements can only be constructed from Link or string objects but the passed object was of type "{type(link).__name__}"')
		else:
			self.__config 		= None
			self.__element		= None
			self.__attribute	= None

	def __repr__(self):
		return "Link(" + self.getLink() + ")"

	def __str__(self) -> str:
		return self.getLink()

	def __eq__(self, o: Union[Link, str]) -> bool:
		if(not type(o) is Link):
			o = Link.force(o)
		return o.__config == self.__config and o.__element == self.__element and o.__attribute == self.__attribute

	def __hash__(self) -> int:
		return hash((self.__config, self.__element, self.__attribute))

	@staticmethod
	def split(link: str, emphasize: int = EMPHASIZE_ELEMENT):
		config 		= None
		element 	= None
		attribute 	= None
		if(link):
			if(type(link) is str):
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
					elif(len(temp) == 1):
						if(emphasize == Link.EMPHASIZE_CONFIG):
							config = temp[0]
						elif(emphasize == Link.EMPHASIZE_ELEMENT):
							element = temp[0]
						elif(emphasize == Link.EMPHASIZE_ATTRIBUTE):
							attribute = temp[0]
						else:
							raise ValueError(f'The emphasize parameter of the Link.split method only allows values in the range of 0 to 2 but the passed value was "{emphasize}" which is considered invalid')
					else:
						raise ValueError(f'The link "{link}" does not have a valid format in the form of "config/element:attribute"')
				else:
					raise ValueError(f'The link "{link}" does not have a valid format in the form of "config/element:attribute"')
				if(not config):
					config = None
				if(not element):
					element = None
				if(not attribute):
					attribute = None
			else:
				raise TypeError(f'The Link.split method was called with the input being of type "{type(link)}" but only inputs of type "str" are supported')
		return config, element, attribute

	@staticmethod
	def parse_with_context(link: str, context: Union[ConfigTypes.Subconfig, Link], emphasize: int = EMPHASIZE_ELEMENT):
		newLink = Link(link, emphasize)
		if(not newLink.hasConfig()):
			if(isinstance(context, ConfigTypes.Subconfig)):
				newLink.config = context.link.config
			elif(isinstance(context, Link)):
				newLink.config = context.config
			else:
				raise TypeError(f'Can only handle context of types Subconfig or Link but not {type(context)}')
		return newLink

	@staticmethod
	def construct(config: str = None, element: str = None, attribute: str = None):
		newLink = Link()
		newLink.set(config, element, attribute)
		return newLink

	@staticmethod
	def isGlobal(link: Union[str, Link]):
		newLink = Link.force(link)
		if(newLink.__config):
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
		if(self.__config):
			return True
		else:
			return False

	def isValidElementLink(self):
		return (not self.__config is None) and (not self.__element is None)

	def set(self, config: str = None, element: str = None, attribute: str = None):
		self.__config: str	= config
		self.__element: str	= element
		self.__attribute:str	= attribute

	def getLink(self, Config: bool = True, Element: bool = True, Attribute: bool = True) -> str:

		config 			= self.__config if not self.__config is None else ""
		element 		= self.__element if not self.__element is None else ""
		attribute 		= self.__attribute if not self.__attribute is None else ""
		if(Config == False):
			config 		= ""
		if(Element == False):
			element 	= ""
		if(Attribute == False):
			attribute 	= ""
		if(not config and not element and not attribute):
			return ""
		if(attribute and element and not config):
			return f"{element}:{attribute}"
		elif(attribute and not element and not config):
			return f":{attribute}"
		elif(not attribute):
			return f"{config}/{element}"
		return f"{config}/{element}:{attribute}"

	def resolveElement(self, config: ConfigTypes.Configuration) -> ConfigTypes.ConfigElement:
		if(self.__config and self.__element):
			subconfig = config.getSubconfig(self)
			return subconfig.getElement(self)
		else:
			raise ValueError(f"The link \"{self.getLink()}\" cannot be resolved. Either the config or the element part of the link are missing but they are mandatory for resolving an element.")

	def resolveAttributeList(self, config: ConfigTypes.Configuration) -> List[Tuple[ConfigTypes.AttributeInstance, ConfigTypes.ConfigElement]]:
		if(self.__config and self.__attribute):
			subconfig = config.getSubconfig(self)
			attributeCollection = []
			for element in subconfig:
				targetAttribute = element.getAttributeInstance(self)
				attributeCollection.append((targetAttribute, element))
			return attributeCollection
		else:
			raise ValueError(f"The link \"{self.getLink()}\" cannot be resolved. Either the config or the attribute part of the link are missing but they are mandatory for resolving an attribute list.")

	def resolveAttribute(self, config: ConfigTypes.Configuration) -> AttributeTypes.AttributeType:
		if(self.__config and self.__attribute and self.__element):
			subconfig = config.getSubconfig(self)
			element = subconfig.getElement(self)
			return element.getAttributeInstance(self)
		else:
			raise ValueError(f"The link \"{self.getLink()}\" cannot be resolved as it is missing at least one part. All three parts of the link are mandatory for resolving an attribute value.")

	def resolveSubconfig(self, config: ConfigTypes.Configuration) -> ConfigTypes.Subconfig:
		if(self.__config):
			return config.getSubconfig(self)
		else:
			raise ValueError(f"The link \"{self.getLink()}\" cannot be resolved. The link is missing the config part which is mandatory for resolving subconfigs.")

	def resolve(self, config: ConfigTypes.Configuration) -> Union[ConfigTypes.ConfigElement, List[Tuple[ConfigTypes.AttributeInstance, ConfigTypes.ConfigElement]], AttributeTypes.AttributeType, ConfigTypes.Subconfig]:
		if(self.__config is None):
			raise AttributeError(f"For resolving a link at least the config must be set.")
		if(self.__element and not self.__attribute): # link to an element
			return self.resolveElement(config)
		elif(not self.__element and self.__attribute): # link to list of attributes of all elements in config
			return self.resolveAttributeList(config)
		elif(self.__attribute and self.__element): # link to the value of an attribute inside an element
			return self.resolveAttribute(config)
		else: # link to a subconfig
			return self.resolveSubconfig(config)

	def copy(self):
		return Link.construct(config=self.__config, element=self.__element, attribute=self.__attribute)

	def merge(self, override: Union[str, Link], emphasize: int = EMPHASIZE_ELEMENT):
		overrideLink = Link.force(override, emphasize)
		mergedLink = self.copy()
		if(overrideLink.__config):
			mergedLink.__config = overrideLink.__config
		if(overrideLink.__element):
			mergedLink.__element = overrideLink.__element
		if(overrideLink.__attribute):
			mergedLink.__attribute = overrideLink.__attribute
		return mergedLink

	def hasAnyParts(self, config = False, element = False, attribute = False):
		""" Retruns True if the link element has all parts that are specified in the parameters
			True means this part of the link has to be set
			False means this part of the link may be set or empty
		"""
		result = True
		if(config and not self.__config):
			result = False
		if(element and not self.__element):
			result = False
		if(attribute and not self.__attribute):
			result = False
		return result

	def hasConfig(self):
		if(self.__config):
			return True
		else:
			return False

	def hasElement(self):
		if(self.__element):
			return True
		else:
			return False

	def hasAttribute(self):
		if(self.__attribute):
			return True
		else:
			return False

	@property
	def parts(self):
		return self.__config, self.__element, self.__attribute

	@property
	def config(self):
		if(self.__config):
			return self.__config
		else:
			raise ValueError(f"The config part of the link {self} was requested but that part is empty. Make sure that the link is in the correct format.")

	@config.setter
	def config(self, value):
		if(value):
			if("/" in value or ":" in value):
				raise ValueError(f'A link part is not allowed to contain a "/" or a ":" character. But the attribute part "{value}" does.')
		self.__config = value

	@property
	def element(self):
		if(self.__element):
			return self.__element
		else:
			raise ValueError(f"The element part of the link {self} was requested but that part is empty. Make sure that the link is in the correct format.")

	@element.setter
	def element(self, value):
		if(value):
			if("/" in value or ":" in value):
				raise ValueError(f'A link part is not allowed to contain a "/" or a ":" character. But the attribute part "{value}" does.')
		self.__element = value

	@property
	def attribute(self):
		if(self.__attribute):
			return self.__attribute
		else:
			raise ValueError(f"The attribute part of the link {self} was requested but that part is empty. Make sure that the link is in the correct format.")

	@attribute.setter
	def attribute(self, value):
		if(value):
			if("/" in value or ":" in value):
				raise ValueError(f'A link part is not allowed to contain a "/" or a ":" character. But the attribute part "{value}" does.')
		self.__attribute = value
