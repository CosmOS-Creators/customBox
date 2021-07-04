from pathlib import Path

import GeneratorCorePlugins as GeneratorPlugins
from Parser.helpers 		import overrides
from Parser.ConfigTypes		import Configuration

class loggerPlugin(GeneratorPlugins.GeneratorPlugin):
	@overrides(GeneratorPlugins.GeneratorPlugin)
	def preGeneration(self, systemConfig: Configuration):
		print(f'Starting file generation...')

	@overrides(GeneratorPlugins.GeneratorPlugin)
	def postGeneration(self, file_paths: list[Path]):
		print(f'All files have been generated successfully:')
		for file in file_paths:
			print(f'\t{file.name}')

	@overrides(GeneratorPlugins.GeneratorPlugin)
	def preFileGeneration(self, currentTemplateDict: dict, systemConfig: Configuration, file_path: Path):
		print(f'Starting file generation for: {file_path}')
		return currentTemplateDict

	@overrides(GeneratorPlugins.GeneratorPlugin)
	def postFileGeneration(self, file_path: Path):
		print(f'File generated successfully: {file_path}')
