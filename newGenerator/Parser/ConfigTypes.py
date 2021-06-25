from types import SimpleNamespace
from typing import List, Union
import Parser.helpers as helpers

class Configuration(SimpleNamespace):
	def require(self, requiredProperties : Union[List[Union[str, helpers.Link]], Union[str, helpers.Link]]):
		if(not type(requiredProperties) is list):
			requiredProperties = [requiredProperties]
		for prop in requiredProperties:
			link = helpers.forceLink(prop)
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
	def __init__(self):
		self.id = None
	def __repr__(self):
		return f"ConfigElement({self.id})"
