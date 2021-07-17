from typing import List, Union
import Generator.GeneratorPluginSkeleton as PluginSkeleton
import Parser.ConfigTypes as ConfigTypes
from Parser.helpers import overrides

class logicRunner():
	def doMagic(self, config: ConfigTypes.Configuration):
		""" Changes to the object model can be done here.
			Just mutate the config object in place and any changes done to it will be automagically used to generate files
		"""
		pass

class logicRunnerPlugin(PluginSkeleton.GeneratorPlugin):
	logicRunners = [] # type: List[logicRunner]

	def registerLogic(self, logic: Union[logicRunner, List[logicRunner]]):
		if(type(logic) is list):
			self.logicRunners.extend(logic)
		elif(type(logic) is logicRunner):
			self.logicRunners.append(logic)
		else:
			raise TypeError(f'Logic runner registration only works with lists of logic runners or single logic runners. But the logic runner that was passed was of type "{type(logic)}".')

	@overrides(PluginSkeleton.GeneratorPlugin)
	def preGeneration(self, systemConfig: ConfigTypes.Configuration, num_of_files: int):
		for logic in self.logicRunners:
			logic.doMagic(systemConfig)
