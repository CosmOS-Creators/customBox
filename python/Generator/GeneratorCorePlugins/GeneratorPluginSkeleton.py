from pathlib import Path
from typing import List
from Parser.ConfigTypes  import Configuration

class GeneratorPlugin():
	def preGeneration(self, systemConfig: Configuration):
		""" called once after parsing of inputs is finished
		"""
		pass

	def postGeneration(self, file_paths: List[Path]):
		""" called once after all files have been generated
		"""
		pass

	def preFileGeneration(self, currentTemplateDict: dict, systemConfig: Configuration, file_path: Path):
		""" called once for every file before it is generated
		"""
		return currentTemplateDict

	def postFileGeneration(self, file_path: Path, file_content: str):
		""" Called once for every file after the template was populated.
			If this hook returns false the file will not be stored in the output folder.
			If this hook returns true the output file will be generated normally.
		"""
		return True
