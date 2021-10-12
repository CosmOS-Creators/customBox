from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

class CardWidget_old(QGroupBox):
	def __init__(self, parent: QWidget, widget: QWidget, name: str = None):
		if(name):
			super().__init__(name, parent)
		else:
			super().__init__(parent)
		layout = QVBoxLayout(self)
		widget.setStyleSheet("background-color: transparent")
		layout.addWidget(widget)

class CardWidget(QGroupBox):
	def __init__(self, parent: QWidget, widget: QWidget, name: str = None):
		if(name):
			super().__init__(name, parent)
		else:
			super().__init__(parent)
		self.__layout = QVBoxLayout(self)
		self.__header_layout = QHBoxLayout()
		self.__layout.addLayout(self.__header_layout)
		if(name is not None):
			heading = QLabel(name, self)
			self.__header_layout.addWidget(heading)

		widget.setStyleSheet("background-color: transparent")
		self.__layout.addWidget(widget)

	@property
	def header(self):
		return self.__header_layout
