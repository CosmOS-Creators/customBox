from PySide6.QtWidgets import QSpinBox

SPIN_BOX_MAX_DEFAULT_VALUE = 2147483647

class customSpinner(QSpinBox):

	def __init__(self, parent) -> None:
		super().__init__(parent=parent)
		self.setMaximum(SPIN_BOX_MAX_DEFAULT_VALUE)

	def wheelEvent(self, event):
		pass
