from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QWidget

class CardWidget(QGroupBox):
	def __init__(self, parent: QWidget, widget: QWidget, name: str = None):
		if(name):
			super().__init__(name, parent)
		else:
			super().__init__(parent)
		layout = QVBoxLayout(self)
		widget.setStyleSheet("background-color: transparent")
		layout.addWidget(widget)
