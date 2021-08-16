from typing import List, Union
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator

from PySide6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QLabel, QLayout, QLineEdit, QSpinBox, QWidget
from Parser.AttributeTypes import BoolType, FloatType, IntType, SelectionType, StringType
from Parser.ConfigTypes import AttributeInstance, ConfigElement


class Ui_element(QWidget):
	comparisonType = ""
	def __init__(self, parent: QWidget, attribute: AttributeInstance, layout: QLayout):
		super().__init__(parent)
		self.ui_element: QWidget	= None
		self.label: QLabel			= None
		self.attributeDef 			= attribute.attributeDefinition
		self.Layout 				= layout
		self.setLayout(self.Layout)
		self.Layout.setContentsMargins(0,0,0,0)

	def get_label_width(self):
		self.label.adjustSize()
		return self.label.width()

	def set_label_width(self, label_width):
		self.label.setMinimumWidth(label_width)
		self.label.setMaximumWidth(label_width)

class String_element(Ui_element):
	comparisonType = "string"
	def __init__(self, parent: QWidget, attribute: AttributeInstance):
		super().__init__(parent, attribute, QHBoxLayout())
		self.attributeDef: StringType
		self.label 		= QLabel(self.attributeDef.label, parent)
		self.ui_element = QLineEdit(parent)
		if(self.attributeDef.validation):
			self.ui_element.setValidator(QRegularExpressionValidator(QRegularExpression(self.attributeDef.validation)))
		self.ui_element.setText(attribute.value)
		self.Layout.addWidget(self.label, 0)
		self.Layout.addWidget(self.ui_element, 1)

class Bool_element(Ui_element):
	comparisonType = "bool"
	def __init__(self, parent: QWidget, attribute: AttributeInstance):
		super().__init__(parent, attribute, QHBoxLayout())
		self.attributeDef: BoolType
		self.label 		= QLabel(self.attributeDef.label, parent)
		self.ui_element = QCheckBox(parent)
		self.ui_element.setChecked(attribute.value)
		self.Layout.addWidget(self.label, 0)
		self.Layout.addWidget(self.ui_element, 1)

class Int_element(Ui_element):
	comparisonType = "int"
	def __init__(self, parent: QWidget, attribute: AttributeInstance):
		super().__init__(parent, attribute, QHBoxLayout())
		self.attributeDef: IntType
		self.label 		= QLabel(self.attributeDef.label, parent)
		self.ui_element = QSpinBox(parent)
		if(self.attributeDef.min):
			self.ui_element.setMinimum(self.attributeDef.min)
		if(self.attributeDef.max):
			self.ui_element.setMaximum(self.attributeDef.max)
		self.ui_element.setSingleStep(1)
		self.ui_element.setValue(attribute.value)
		self.Layout.addWidget(self.label, 0)
		self.Layout.addWidget(self.ui_element, 1)

class Float_element(Ui_element):
	comparisonType = "float"
	def __init__(self, parent: QWidget, attribute: AttributeInstance):
		super().__init__(parent, attribute, QHBoxLayout())
		self.attributeDef: FloatType
		self.label 		= QLabel(self.attributeDef.label, parent)
		self.ui_element = QSpinBox(parent)
		if(self.attributeDef.min):
			self.ui_element.setMinimum(self.attributeDef.min)
		if(self.attributeDef.max):
			self.ui_element.setMaximum(self.attributeDef.max)
		self.ui_element.setValue(attribute.value)
		self.ui_element.setSingleStep(0.1)
		self.Layout.addWidget(self.label, 0)
		self.Layout.addWidget(self.ui_element, 1)

class Selection_element(Ui_element):
	comparisonType = "selection"
	def __init__(self, parent: QWidget, attribute: AttributeInstance):
		super().__init__(parent, attribute, QHBoxLayout())
		self.attributeDef: SelectionType
		self.label 		= QLabel(self.attributeDef.label, parent)
		self.ui_element = QComboBox(parent)
		if(type(self.attributeDef.elements) is list):
			for selectionElement in self.attributeDef.elements:
				self.ui_element.addItem(selectionElement)
			self.ui_element.setCurrentText(attribute.value)
		else:
			for selectionElement in self.attributeDef.resolvedElements:
				self.ui_element.addItem(selectionElement.value)
			selected_element: ConfigElement = attribute.value
			selected_attrib = selected_element.getAttribute(self.attributeDef.targetedAttribute)
			self.ui_element.setCurrentText(selected_attrib.value)
		self.Layout.addWidget(self.label, 0)
		self.Layout.addWidget(self.ui_element, 1)

avaliable_ui_elements: List[Ui_element] = [String_element, Bool_element, Int_element, Float_element, Selection_element]

def create_interface_element(parent: QWidget, attributeInstance: AttributeInstance) -> Union[None, Ui_element]:
	Attribute = attributeInstance.attributeDefinition
	if(not Attribute.is_placeholder and not Attribute.hidden):
		for ui_element in avaliable_ui_elements:
			if(ui_element.comparisonType == Attribute.type):
				return ui_element(parent, attributeInstance)
	return None
