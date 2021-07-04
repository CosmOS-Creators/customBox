from __future__ import annotations

from types import SimpleNamespace
from typing import List, Union
import Parser.helpers as helpers
import Parser.AttributeTypes as AttributeTypes

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
	def __init__(self, link: Union[str, helpers.Link, None]):
		self.iterator 	= []
		self.link		= helpers.forceLink(link)

	def __repr__(self):
		return f"Subconfig({self.iterator})"

class ConfigElement(SimpleNamespace):
	__attributeLookup 	= {}
	__configLookup		= None
	link 				= None
	def __init__(self, config: ConfigElement, attribute: dict[str, AttributeTypes.AttributeType], link: Union[str, helpers.Link]):
		self.id 				= None
		self.__attributeLookup	= attribute
		self.__configLookup		= config
		self.link				= helpers.forceLink(link)

	def __repr__(self):
		return f"ConfigElement({self.id})"

	def populate(self, attribute: str, value, isPlaceholder: bool = True):
		"""
			Populate any attribute with a value. If the attribute is not a placeholder isPlaceholder has to be set to False explicitly
		"""
		link = helpers.forceLink(self.link)
		link.attribute = attribute
		if(not link.isGlobal()):
			raise ValueError(f"Target link must be global but \"{link}\" is not")
		attributeDefinitionTarget 	= link.getLink(Element=False)
		if(not attributeDefinitionTarget in self.__attributeLookup):
			raise AttributeError(f"Element \"{link.getLink()}\" does not point to an exiting attribute definition. Most likely the link is pointing to a wrong location")
		targetAttributeDefinition 	= self.__attributeLookup[attributeDefinitionTarget]
		if(not targetAttributeDefinition.is_placeholder and isPlaceholder == True):
			raise AttributeError(f"Element \"{link.getLink(Attribute=False)}\" is not a placeholder but the populate method was expecting a placeholder attribute. If a non placeholder attribute should be written to on purpose call populate with isPlaceholder set to False")
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
