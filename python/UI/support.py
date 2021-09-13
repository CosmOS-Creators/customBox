from typing import Union
from PySide6.QtWidgets import QFrame
from PySide6.QtGui import QIcon
from pathlib import Path


class Icons():
	def __init__(self, icon_folder: Union[str, Path, None] = None):
		if(icon_folder):
			self.set_icon_folder(icon_folder)
		else:
			self.icon_folder = Path(__file__).with_name("icons")

	def set_icon_folder(self, icon_folder: Union[str, Path]):
		if(not isinstance(icon_folder, Path)):
			self.icon_folder = Path(icon_folder)
		else:
			self.icon_folder = icon_folder

	def Icon(self, icon_name: str, color: str = "white"):
		if(icon_name):
			icon_name = f"{icon_name}_{color}"
			for file in self.icon_folder.glob('*.svg'):
				if(file.name.startswith(icon_name)):
					return QIcon(str(file))
		return None

icons = Icons()

def clear_layout(layout):
	while layout.count():
		child = layout.takeAt(0)
		if child.widget() is not None:
			child.widget().deleteLater()
		elif child.layout() is not None:
			clear_layout(child.layout())

class SeperatorLine(QFrame):
	def __init__(self, parent):
		super().__init__(parent)
		self.setObjectName("seperatorLine")
		self.setFrameShape(QFrame.HLine)
		self.setFrameShadow(QFrame.Sunken)
