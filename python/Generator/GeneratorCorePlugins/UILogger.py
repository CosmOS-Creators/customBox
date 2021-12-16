from pathlib import Path
from typing import List
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QProgressDialog, QWidget


import Generator.GeneratorPluginSkeleton as PluginSkeleton
from Parser.helpers import overrides
from Parser.ConfigTypes import Configuration


class UILoggerPlugin(PluginSkeleton.GeneratorPlugin):
    def __init__(self, parent: QWidget, cancel_callback = None) -> None:
        super().__init__()
        self.parent = parent
        self.cancel = cancel_callback

    @overrides(PluginSkeleton.GeneratorPlugin)
    def preGeneration(self, systemConfig: Configuration, num_of_files: int):
        self.pd = QProgressDialog(f"Generating {num_of_files + 1} files...", "Cancel", 0, num_of_files + 1, self.parent)
        if(self.cancel is None):
            self.pd.setCancelButton(None)
        else:
            self.pd.canceled.connect(self.cancel)
        self.pd.setWindowModality(Qt.WindowModal)
        self.pd.show()

    @overrides(PluginSkeleton.GeneratorPlugin)
    def postGeneration(self, file_paths: List[Path]):
        self.pd.close()
        self.pd.deleteLater()

    @overrides(PluginSkeleton.GeneratorPlugin)
    def preFileGeneration(
        self, currentTemplateDict: dict, systemConfig: Configuration, file_path: Path
    ):
        return currentTemplateDict

    @overrides(PluginSkeleton.GeneratorPlugin)
    def postFileGeneration(self, file_path: Path, file_content: str):
        self.pd.setValue(self.pd.value() + 1)
        return True

    def register_cancel_callback(self, cancel_callback):
        self.cancel = cancel_callback
