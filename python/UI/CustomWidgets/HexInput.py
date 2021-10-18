from PySide6.QtCore import QObject, QRegularExpression, Signal
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
from UI.CustomWidgets.IconButton import iconButton
from Parser.helpers import toHex, toInt

HEX_VALIDATOR_REGEX = r"^[0-9A-Fa-f]+$"

class hexInputSignals(QObject):
	valueChanged = Signal(int)

class hexInput(QWidget):
	def __init__(self, value: int, parent: QWidget):
		super().__init__(parent)
		self.setContentsMargins(0,0,0,0)
		self.__signals 		= hexInputSignals()
		self.__layout 		= QHBoxLayout(self)
		self.__layout.setContentsMargins(0,0,0,0)
		self.__value		= value
		self.__maximum 		= None
		self.__minimum 		= None
		self.valueChanged	= self.__signals.valueChanged
		self.__text_field 	= QLineEdit(self.hexValue(), self)
		self.__text_field.setValidator(QRegularExpressionValidator(QRegularExpression(HEX_VALIDATOR_REGEX)))
		self.__text_field.textChanged.connect(self.__changed_callback)
		self.__hex_prefix_label = QLabel("0x", self)
		self.__hex_prefix_label.setObjectName("hexInputPrefixLabel")
		self.__layout.addWidget(self.__hex_prefix_label)
		self.__layout.addWidget(self.__text_field)
		self.__button_layout = QVBoxLayout()
		self.__button_layout.setContentsMargins(0,0,0,0)
		self.__button_layout.setSpacing(0)
		self.__button_layout.setObjectName("noSpaces")
		self.__layout.addLayout(self.__button_layout)
		self.__up_button = iconButton(self, "arrow_drop_up", clicked=self.__upButtonClicked)
		self.__down_button = iconButton(self, "arrow_drop_down", clicked=self.__downButtonClicked)
		self.__button_layout.addWidget(self.__up_button)
		self.__button_layout.addWidget(self.__down_button)

	def setMaximum(self, maximum: int):
		self.__maximum = maximum

	def setMinimum(self, minimum: int):
		self.__minimum = minimum

	def __changed_callback(self, value):
		try:
			value = toInt(value)
			if(self.__maximum is not None):
				if(value > self.__maximum):
					self.__text_field.setText(self.hexValue())
					return
			if(self.__minimum is not None):
				if(value < self.__minimum):
					self.__text_field.setText(self.hexValue())
					return
		except ValueError:
			pass

		self.__value = value
		self.valueChanged.emit(self.__value)

	def value(self):
		return self.__value

	def hexValue(self):
		return  toHex(self.__value, False)

	def setValue(self, value: int):
		self.__value = value
		self.__text_field.setText(toHex(value))

	def __upButtonClicked(self):
		pass

	def __downButtonClicked(self):
		pass
