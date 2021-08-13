from typing import Union
from PySide6.QtGui import QIcon
from pathlib import Path

class Icons():
	def __init__(self, icon_folder: Union[str, Path, None]):
		if(icon_folder):
			if(not isinstance(icon_folder, Path)):
				self.icon_folder = Path(icon_folder)
			else:
				self.icon_folder = icon_folder
		else:
			self.icon_folder = Path(__file__).with_name("icons")

	def Icon(self, icon_name: str, color: str = "white"):
		if(icon_name):
			icon_name = f"{icon_name}_{color}"
			for file in self.icon_folder.glob('*.svg'):
				if(file.name.startswith(icon_name)):
					return QIcon(str(file))
		return None
