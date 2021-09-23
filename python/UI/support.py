from typing import Union
from PySide6.QtWidgets import QFrame, QLabel
from PySide6.QtGui import QIcon, QMovie
from pathlib import Path


class Icons():
	def __init__(self, icon_folder: Union[str, Path, None] = None):
		if(icon_folder):
			self.set_icon_folder(icon_folder)
		else:
			self.icon_folder = Path(__file__).with_name("icons")

	def set_resources_folder(self, icon_folder: Union[str, Path]):
		if(not isinstance(icon_folder, Path)):
			self.icon_folder = Path(icon_folder)
		else:
			self.icon_folder = icon_folder

	def __file(self, name: str, color: str, extentsion: str):
		if(name):
			icon_name = f"{name}_{color}"
			for file in self.icon_folder.rglob(extentsion):
				if(file.name.startswith(icon_name)):
					return str(file)
		print(f'WARNING: Icon "{name}" could not be loaded, ignoring...')
		return None

	def Icon(self, icon_name: str, color: str = "white"):
		return QIcon(self.__file(icon_name, color, "*.svg"))

	def Amimation(self, icon_name: str, color: str = "white"):
		# animation = QMovie(self.__file(icon_name, color, "*.gif"))
		# animation.setCacheMode(QMovie.CacheAll)
		# animation.setSpeed(100)
		# animation_widget = QLabel()
		# animation_widget.setMovie(animation)
		return QIcon(self.__file(icon_name, color, "*.gif"))

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
