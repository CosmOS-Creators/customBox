from PySide6.QtWidgets import QFrame, QPushButton, QWidget
from UI.StyleDimensions import styleExtensions
from UI.support import icons

class hexInput(QFrame):
	def __init__(self, parent: QWidget, icon: str, tooltip=None, clicked=None):
		super().__init__(icons.Icon(icon), "", parent, clicked=clicked)
		self.setToolTip(tooltip)
		self.setProperty("class", "iconButton")
		self.setIconSize(styleExtensions.ICON_BUTTON_SIZE)
