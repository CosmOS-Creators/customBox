from types import SimpleNamespace
from typing import List
from Parser.helpers import isGlobalLink, splitGlobalLink

class Configuration(SimpleNamespace):
	def require(self, requiredProperties : List[str]):
		if(not type(requiredProperties) is list):
			raise TypeError("Require only supports lists as input")
		for prop in requiredProperties:
			if(isGlobalLink(prop)):
				configStr = splitGlobalLink(prop)[0]
			else:
				configStr = prop
			try:
				configObj = getattr(self, configStr)
			except AttributeError:
				raise AttributeError(f"Configuration does not have a subconfig named \"{configStr}\" but it was listed as being required")
			if(isGlobalLink(prop)):
				attribStr = splitGlobalLink(prop)[1]
				for element in configObj.iterator:
					try:
						getattr(element, attribStr)
					except AttributeError:
						raise AttributeError(f"Element \"{element.id}\" has no attribute called \"{attribStr}\" but it was listed as being required")

class Subconfig(SimpleNamespace):
	def __init__(self):
		self.iterator = []

class ConfigElement(SimpleNamespace):
	def __init__(self):
		self.id = None
