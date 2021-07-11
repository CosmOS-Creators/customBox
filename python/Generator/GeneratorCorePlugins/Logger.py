from pathlib import Path
from typing import List
from tqdm import tqdm

import Generator.GeneratorCorePlugins as GeneratorPlugins
from Parser.helpers 		import overrides
from Parser.ConfigTypes		import Configuration

class loggerPlugin(GeneratorPlugins.GeneratorPlugin):
	@overrides(GeneratorPlugins.GeneratorPlugin)
	def preGeneration(self, systemConfig: Configuration, num_of_files: int):
		self.pbar = tqdm(total=num_of_files)
		tqdm.write(f'Starting file generation for {num_of_files} files...')

	@overrides(GeneratorPlugins.GeneratorPlugin)
	def postGeneration(self, file_paths: List[Path]):
		tqdm.write(f'All files have been generated successfully')
		self.pbar.close()

	@overrides(GeneratorPlugins.GeneratorPlugin)
	def preFileGeneration(self, currentTemplateDict: dict, systemConfig: Configuration, file_path: Path):
		return currentTemplateDict

	@overrides(GeneratorPlugins.GeneratorPlugin)
	def postFileGeneration(self, file_path: Path, file_content: str):
		self.pbar.update(1)
		return True
