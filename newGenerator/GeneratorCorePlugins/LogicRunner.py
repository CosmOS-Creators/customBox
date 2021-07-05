from typing import Union
import GeneratorCorePlugins.GeneratorPluginSkeleton as GeneratorPulgins
import Parser.ConfigTypes as ConfigTypes

class logicRunner():
	def doMagic(self, config: ConfigTypes.Configuration):
		""" Changes to the object model can be done here.
			Just mutate the config object in place and any changes done to it will be automagically used to generate files
		"""
		pass

class logicRunnerPlugin(GeneratorPulgins.GeneratorPlugin):
	logicRunners = [] # type: list[logicRunner]

	def registerLogic(self, logic: Union[logicRunner, list[logicRunner]]):
		if(type(logic) is list):
			self.logicRunners.extend(logic)
		elif(type(logic) is logicRunner):
			self.logicRunners.append(logic)
		else:
			raise TypeError(f'Logic runner registration only works with lists of logic runners or single logic runners. But the logic runner that was passed was of type "{type(logic)}".')

	def preGeneration(self, systemConfig: ConfigTypes.Configuration):
		for logic in self.logicRunners:
			logic.doMagic(systemConfig)
