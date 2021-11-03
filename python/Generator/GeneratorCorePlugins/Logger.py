from pathlib import Path
from typing import List
from tqdm import tqdm

import Generator.GeneratorPluginSkeleton as PluginSkeleton
from Parser.helpers import overrides
from Parser.ConfigTypes import Configuration


class loggerPlugin(PluginSkeleton.GeneratorPlugin):
    @overrides(PluginSkeleton.GeneratorPlugin)
    def preGeneration(self, systemConfig: Configuration, num_of_files: int):
        self.pbar = tqdm(total=num_of_files + 1)
        tqdm.write(f"Starting file generation for {num_of_files + 1} files...")

    @overrides(PluginSkeleton.GeneratorPlugin)
    def postGeneration(self, file_paths: List[Path]):
        tqdm.write(f"All files have been generated successfully")
        self.pbar.close()

    @overrides(PluginSkeleton.GeneratorPlugin)
    def preFileGeneration(
        self, currentTemplateDict: dict, systemConfig: Configuration, file_path: Path
    ):
        return currentTemplateDict

    @overrides(PluginSkeleton.GeneratorPlugin)
    def postFileGeneration(self, file_path: Path, file_content: str):
        self.pbar.update(1)
        return True
