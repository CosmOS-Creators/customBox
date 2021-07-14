from __future__ import annotations

from types import SimpleNamespace
from typing import List, Union
import Parser.helpers as helpers
import Parser.AttributeTypes as AttributeTypes

class Configuration(SimpleNamespace):
	__allConfigs: List[Subconfig] = []
	def require(self, requiredProperties : Union[List[Union[str, helpers.Link]], Union[str, helpers.Link]]):
		if(not type(requiredProperties) is list):
			requiredProperties = [requiredProperties]
		for prop in requiredProperties:
			link = helpers.forceLink(prop, helpers.Link.EMPHASIZE_CONFIG)
			try:
				link.resolve(self)
			except Exception as e:
				raise AttributeError(f"The link \"{link.getLink()}\" was listed as required but it could not be resolved: {str(e)}")

	def __setattr__(self, name, val):
		if(name != "require" and not name in self.__allConfigs and type(val) is Subconfig):
			self.__allConfigs.append(val)
		object.__setattr__(self, name, val)

	def activateValueGuards(self, activate: bool = False):
		for subconfig in self.__allConfigs:
			subconfig.activateValueGuards(activate)

class Subconfig(SimpleNamespace):
	def __init__(self, link: Union[str, helpers.Link, None]):
		self.iterator: List[ConfigElement] 	= []
		self.link							= helpers.forceLink(link)

	def __repr__(self):
		return f"Subconfig({self.iterator})"

	def activateValueGuards(self, activate: bool = False):
		for element in self.iterator:
			element.activateValueGuards(activate)

class ConfigElement(SimpleNamespace):
	__attributeLookup 		= {}
	__setting_guard_active 	= False
	link 					= None
	def __init__(self, config: ConfigElement, link: Union[str, helpers.Link]):
		self.id 				= None
		self.__configLookup		= config
		self.link				= helpers.forceLink(link)

	def __repr__(self):
		return f"ConfigElement({self.id})"

	def assignAttribute(self, propertyName: str, attribute: AttributeTypes.AttributeType):
		self.__attributeLookup[propertyName] = attribute

	def activateValueGuards(self, activate: bool = False):
		self.__setting_guard_active = activate

	def populate(self, property_name: str, value, isPlaceholder: bool = True):
		"""
			Populate any attribute with a value. If the attribute is not a placeholder isPlaceholder has to be set to False explicitly
		"""
		link = helpers.forceLink(self.link)
		link.attribute = property_name
		if(not link.isGlobal()):
			raise ValueError(f"Target link must be global but \"{link}\" is not")
		if(not property_name in self.__attributeLookup):
			raise AttributeError(f"Element \"{link.getLink()}\" does not point to an exiting attribute definition. Most likely the link is pointing to a wrong location")
		targetAttributeDefinition 	= self.__attributeLookup[property_name]
		if(not targetAttributeDefinition.is_placeholder and isPlaceholder == True):
			raise AttributeError(f"Element \"{link.getLink(Attribute=False)}\" is not a placeholder but the populate method was expecting a placeholder attribute. If a non placeholder attribute should be written to on purpose call populate with isPlaceholder set to False")
		try:
			validatedValue 			= targetAttributeDefinition.checkValue(value)
		except ValueError as e:
			raise ValueError(f"Error validating the new value for the placeholder \"{link.getLink()}\": {str(e)}")
		try:
			object.__setattr__(self, property_name, validatedValue)
			pass
		except AttributeError:
			raise AttributeError(f"Element \"{link.getLink(Attribute=False)}\" has no attribute called \"{link.attribute}\"")
		try:
			if(targetAttributeDefinition.needsLinking):
				targetAttributeDefinition.link(self.__configLookup, self, link.attribute, True)
				pass
		except Exception as e:
			raise Exception(f'Error while linking element "{link.getLink()}" of type "{targetAttributeDefinition.type}": {str(e)}')

	def __setattr__(self, name, val):
		if(self.__setting_guard_active and not name in ["id", "link"]):
			try:
				self.populate(name, val)
			except Exception as e:
				print(f"Error while populating property {name}: {str(e)}")
				object.__setattr__(self, name, val)
		else:
			object.__setattr__(self, name, val)

	def _setattr_direct(self, name, val):
		object.__setattr__(self, name, val)
