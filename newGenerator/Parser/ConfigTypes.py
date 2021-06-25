from types import SimpleNamespace
from typing import List, Union
import Parser.helpers as helpers

class Configuration(SimpleNamespace):
	def require(self, requiredProperties : Union[List[Union[str, helpers.Link]], Union[str, helpers.Link]]):
		if(not type(requiredProperties) is list):
			requiredProperties = [requiredProperties]
		for prop in requiredProperties:
			link = helpers.forceLink(prop)
			if(link.element and not link.config and not link.attribute): # dirty hack for the edge case where only a config is listed
				link.config = link.element
				link.element = None
			try:
				link.resolve(self)
			except Exception as e:
				raise AttributeError(f"The link \"{link.getLink()}\" was listed as required but it could not be resolved: {str(e)}")

class Subconfig(SimpleNamespace):
	def __init__(self):
		self.iterator = []

	def __repr__(self):
		return f"Subconfig({self.iterator})"

class ConfigElement(SimpleNamespace):
	__attributeLookup 	= {}
	__configLookup		= None
	__link 				= ""
	def __init__(self, config, attribute, link):
		self.id = None
		self.__attributeLookup	= attribute
		self.__configLookup		= config
		self.__link				= link

	def __repr__(self):
		return f"ConfigElement({self.id})"

	def populatePlaceholder(self, attribute: str, value):
		link = helpers.forceLink(self.__link)
		link.attribute = attribute
		if(not link.isGlobal()):
			raise ValueError(f"Target link must be global but \"{link}\" is not")
		attributeDefinitionTarget 	= link.getLink(Element=False)
		targetAttributeDefinition 	= self.__attributeLookup[attributeDefinitionTarget]
		try:
			validatedValue 			= targetAttributeDefinition.checkValue(value)
		except ValueError as e:
			raise ValueError(f"Error validating the new value for the placeholder \"{link.getLink()}\": {str(e)}")
		try:
			setattr(self, link.attribute, validatedValue)
		except AttributeError:
			raise AttributeError(f"Element \"{link.getLink(Attribute=False)}\" has no attribute called \"{link.attribute}\"")
		if(targetAttributeDefinition.needsLinking):
			targetAttributeDefinition.link(self.__configLookup, self, link.attribute)
