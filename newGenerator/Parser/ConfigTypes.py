from types import SimpleNamespace
from typing import List, Union
import Parser.helpers as helpers

class Configuration(SimpleNamespace):
	def require(self, requiredProperties : Union[List[str], str]):
		requiredProperties = helpers.forceStrList(requiredProperties)
		for prop in requiredProperties:
			if(helpers.isGlobalLink(prop)):
				configStr = helpers.splitGlobalLink(prop)[0]
			else:
				configStr = prop
			try:
				configObj = getattr(self, configStr)
			except AttributeError:
				raise AttributeError(f"Configuration does not have a subconfig named \"{configStr}\" but it was listed as being required")
			if(helpers.isGlobalLink(prop)):
				attribStr = helpers.splitGlobalLink(prop)[1]
				for element in configObj.iterator:
					try:
						getattr(element, attribStr)
					except AttributeError:
						raise AttributeError(f"Element \"{element.id}\" has no attribute called \"{attribStr}\" but it was listed as being required")

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
