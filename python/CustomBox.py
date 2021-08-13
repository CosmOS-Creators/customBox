from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QDoubleValidator, QIntValidator, QRegularExpressionValidator
from PySide6.QtWidgets import QCheckBox, QComboBox, QFormLayout, QLineEdit, QSpinBox, QWidget
from Parser.ConfigTypes import AttributeInstance
from UI import Configurator
import sys
import Parser

def addElementToPage(parent: QWidget, page: QFormLayout, element: AttributeInstance):
	Attribute = element.attributeDefinition
	if(not Attribute.is_placeholder):
		if(Attribute.type == "string"):
			newStringEdit = QLineEdit(parent)
			if(Attribute.validation):
				newStringEdit.setValidator(QRegularExpressionValidator(QRegularExpression(Attribute.validation)))
			newStringEdit.setText(element.value)
			page.addRow(Attribute.label, newStringEdit)
		elif(Attribute.type == "bool"):
			newBoolEdit = QCheckBox(parent)
			newBoolEdit.setChecked(element.value)
			page.addRow(Attribute.label, newBoolEdit)
		elif(Attribute.type == "int"):
			newIntEdit = QSpinBox(parent)
			if(Attribute.min):
				newIntEdit.setMinimum(Attribute.min)
			if(Attribute.max):
				newIntEdit.setMaximum(Attribute.max)
			newIntEdit.setSingleStep(1)
			newIntEdit.setValue(element.value)
			page.addRow(Attribute.label, newIntEdit)
		elif(Attribute.type == "float"):
			newFloatEdit = QSpinBox(parent)
			if(Attribute.min):
				newFloatEdit.setMinimum(Attribute.min)
			if(Attribute.max):
				newFloatEdit.setMaximum(Attribute.max)
			newFloatEdit.setSingleStep(0.1)
			newFloatEdit.setValue(element.value)
			page.addRow(Attribute.label, newFloatEdit)
		elif(Attribute.type == "selection"):
			if(type(Attribute.elements) is list):
				newSelectionEdit = QComboBox(parent)
				for selectionElement in Attribute.elements:
					newSelectionEdit.addItem(selectionElement)
				newSelectionEdit.setCurrentText(element.value)
				page.addRow(Attribute.label, newSelectionEdit)


if __name__ == "__main__":
	args 		= Parser.Workspace.getReqiredArgparse().parse_args()
	workspace 	= Parser.Workspace(args.WORKSPACE)
	parser 		= Parser.ConfigParser(workspace)
	systemModel = parser.parse()
	Interface 	= Configurator()

	cores 		= systemModel.getSubconfig("cores")
	core_0 		= cores.getElement("core_0")

	page1 		= QWidget()
	page1.setObjectName("Cores")
	page1Layout = QFormLayout()

	for element in core_0.attributeInstances.values():
		addElementToPage(page1, page1Layout, element)
	page1.setLayout(page1Layout)

	cores 		= systemModel.getSubconfig("schedulers")
	scheduler_0 = cores.getElement("scheduler_0")

	page2 		= QWidget()
	page2.setObjectName("Schedulers")
	page2Layout = QFormLayout()

	for element in scheduler_0.attributeInstances.values():
		addElementToPage(page2, page2Layout, element)
	page2.setLayout(page2Layout)

	Pages = [(page1, "memory"), (page2, "calendar_today")]

	Interface.buildMainWindow(Pages)
	sys.exit(Interface.run())
