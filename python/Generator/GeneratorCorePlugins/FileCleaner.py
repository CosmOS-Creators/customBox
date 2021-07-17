import os
from pathlib import Path
from typing import List
from tqdm import tqdm

import Generator.GeneratorPluginSkeleton as PluginSkeleton
from Parser.helpers 		import overrides

class fileCleanerPlugin(PluginSkeleton.GeneratorPlugin):
	def __init__(self, outputPaths: List[str]):
		self.__output_paths = []
		for item in outputPaths:
			self.__output_paths.append(Path(item))

	@overrides(PluginSkeleton.GeneratorPlugin)
	def postGeneration(self, file_paths: List[Path]):
		fileList = []
		for out_path in self.__output_paths:
			for root, subFolder, files in os.walk(out_path):
				for item in files:
					path = os.path.join(root,item)
					fileList.append(Path(path))
		for file in file_paths:
			if(file in fileList):
				fileList.remove(file)

		for file in fileList:
			tqdm.write(f'Removing not generated file "{file}"" from output directory')
			os.remove(file)
