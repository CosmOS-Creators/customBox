from pathlib import Path
from Parser.ConfigTypes  import Configuration

class GeneratorPlugin():
	def preGeneration(self, systemConfig: Configuration):
		""" called once after parsing of inputs is finished
		"""
		pass

	def postGeneration(self, file_paths: list[Path]):
		""" called once after all files have been generated
		"""
		pass

	def preFileGeneration(self, currentTemplateDict: dict, systemConfig: Configuration, file_path: Path):
		""" called once for every file before it is generated
		"""
		return currentTemplateDict

	def postFileGeneration(self, file_path: Path):
		""" called once for every file after it is generated
		"""
		pass
