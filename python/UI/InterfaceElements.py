from typing import Dict, List, Union
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator

from PySide6.QtWidgets import QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QWidget
from Parser.AttributeTypes import BoolType, FloatType, IntType, ReferenceListType, SelectionType, StringType
from Parser.ConfigTypes import AttributeInstance, ConfigElement
from Parser.LinkElement import Link
from UI.support import icons
from UI.CustomWidgets import ListBuilderWidget
from Parser import ValidationError
from UI.StyleDimensions import styleExtensions

SPIN_BOX_MAX_DEFAULT_VALUE = 2147483647

class Ui_element(QWidget):
	comparisonType = ""
	def __init__(self, parent: QWidget, attribute: AttributeInstance):
		super().__init__(parent)
		self.ui_element: QWidget	= None
		self.label: QLabel			= None
		self.tooltip: str			= None
		self.attributeDef 			= attribute.attributeDefinition
		self.attribute 				= attribute
		self.tooltip 				= self.attributeDef.tooltip
		self._get_current_value_func= None

	def set_ui_element(self, widget: QWidget):
		self.ui_element = widget
		valid, msg = self.attribute.isValid()
		self.setValidity(valid, msg)

	def get_Row(self):
		element_widget = QWidget(self)
		element_layout = QHBoxLayout(element_widget)
		element_layout.addWidget(self.ui_element, 1)
		if(self.tooltip):
			tooltip_icon = icons.Icon("help")
			if(tooltip_icon):
				tooltip_widget = QPushButton(element_widget)
				tooltip_widget.setObjectName("HelpButton")
				tooltip_widget.setToolTip(self.tooltip)
				tooltip_widget.setIcon(tooltip_icon)
				element_layout.addWidget(tooltip_widget, 0)
		return self.label, element_widget

	def setValidity(self, valid: bool, error_msg: str = None):
		if(valid):
			self.ui_element.setStyleSheet("")
			self.ui_element.setToolTip(None)
		else:
			self.ui_element.setStyleSheet(f"border-color: {styleExtensions.ERROR_COLOR}")
			self.ui_element.setToolTip(error_msg)

	def saveToConfigObject(self, value = None):
		try:
			if(self._get_current_value_func):
				self.attribute.populate(self._get_current_value_func(), False)
			elif(value is not None):
				self.attribute.populate(value, False)
			self.setValidity(True)
		except ValidationError as e:
			self.setValidity(False, str(e))

class String_element(Ui_element):
	comparisonType = StringType._comparison_type
	def __init__(self, parent: QWidget, attribute: AttributeInstance):
		super().__init__(parent, attribute)
		self.attributeDef: StringType
		self.label 		= QLabel(self.attributeDef.label, parent)
		self.set_ui_element(QLineEdit(parent))
		if(self.attributeDef.validation):
			self.ui_element.setValidator(QRegularExpressionValidator(QRegularExpression(self.attributeDef.validation)))
		self.ui_element.setText(attribute.value)


		self._get_current_value_func = self.ui_element.text
		self.ui_element.textChanged.connect(self.saveToConfigObject)


class Bool_element(Ui_element):
	comparisonType = BoolType._comparison_type
	def __init__(self, parent: QWidget, attribute: AttributeInstance):
		super().__init__(parent, attribute)
		self.attributeDef: BoolType
		self.label 		= QLabel(self.attributeDef.label, parent)
		self.set_ui_element(QCheckBox(parent))
		self.ui_element.setChecked(attribute.value)

		self._get_current_value_func = self.ui_element.isChecked
		self.ui_element.toggled.connect(self.saveToConfigObject)

class Int_element(Ui_element):
	comparisonType = IntType._comparison_type
	def __init__(self, parent: QWidget, attribute: AttributeInstance):
		super().__init__(parent, attribute)
		self.attributeDef: IntType
		self.label 		= QLabel(self.attributeDef.label, parent)
		self.set_ui_element(QSpinBox(parent))
		if(self.attributeDef.min is not None):
			self.ui_element.setMinimum(self.attributeDef.min)
		if(self.attributeDef.max is not None):
			self.ui_element.setMaximum(self.attributeDef.max)
		else:
			self.ui_element.setMaximum(SPIN_BOX_MAX_DEFAULT_VALUE)
		self.ui_element.setSingleStep(1)
		self.ui_element.setValue(attribute.value)

		self._get_current_value_func = self.ui_element.value
		self.ui_element.valueChanged.connect(self.saveToConfigObject)

class Float_element(Ui_element):
	comparisonType = FloatType._comparison_type
	def __init__(self, parent: QWidget, attribute: AttributeInstance):
		super().__init__(parent, attribute)
		self.attributeDef: FloatType
		self.label 		= QLabel(self.attributeDef.label, parent)
		self.set_ui_element(QSpinBox(parent))
		if(self.attributeDef.min):
			self.ui_element.setMinimum(self.attributeDef.min)
		if(self.attributeDef.max):
			self.ui_element.setMaximum(self.attributeDef.max)
		self.ui_element.setValue(attribute.value)
		self.ui_element.setSingleStep(0.1)

		self._get_current_value_func = self.ui_element.value
		self.ui_element.valueChanged.connect(self.saveToConfigObject)

class Selection_element(Ui_element):
	comparisonType = SelectionType._comparison_type
	def __init__(self, parent: QWidget, attribute: AttributeInstance):
		super().__init__(parent, attribute)
		self.attributeDef: SelectionType
		self.label 		= QLabel(self.attributeDef.label, parent)
		self.set_ui_element(QComboBox(parent))
		if(type(self.attributeDef.elements) is list):
			for selectionElement in self.attributeDef.elements:
				self.ui_element.addItem(selectionElement, selectionElement)
			self.ui_element.setCurrentText(attribute.value)
		else:
			for selectionElement in self.attributeDef.resolvedElements:
				self.ui_element.addItem(selectionElement.value, selectionElement)
			selected_element: ConfigElement = attribute.value
			if(selected_element is not None):
				selected_attrib = selected_element.getAttribute(self.attributeDef.targetedAttribute)
				self.ui_element.setCurrentText(selected_attrib.value)

		self._get_current_value_func = self.ui_element.currentData
		self.ui_element.currentIndexChanged.connect(self.saveToConfigObject)

class ReferenceList_element(Ui_element):
	comparisonType = ReferenceListType._comparison_type
	def __init__(self, parent: QWidget, attribute: AttributeInstance):
		super().__init__(parent, attribute)
		self.attributeDef: ReferenceListType
		self.configuration				= attribute.parent.parent.parent
		self.label 						= QLabel(self.attributeDef.label, parent)
		avaliableOptions 				= list()
		selectedOptions 				= list()
		attribute_targets: Dict[str, str]	= dict()
		if(self.attributeDef.elements):
			for referencedElement in self.attributeDef.elements:
				if(referencedElement.config not in attribute_targets):
					attribute_targets[referencedElement.config] = referencedElement.attribute
				avaliableChoices = referencedElement.resolveAttributeList(self.configuration)
				for attrib_inst, conf_element in avaliableChoices:
					avaliableOptions.append((attrib_inst.value, conf_element))
		else:
			for subconfig in self.configuration.configs.values():
				for element in subconfig.elements.values():
					avaliableOptions.append((str(element.link), element))
		for selection in attribute.value:
			if(len(attribute_targets) > 0):
				if(selection.link.config in attribute_targets):
					attribute_target_link = Link.construct(config = selection.link.config, element=selection.link.element, attribute=attribute_targets[selection.link.config])
					selectedAttribute_str = attribute_target_link.resolveAttribute(self.configuration)
					selectedOptions.append((selectedAttribute_str.value, selection))
			else:
				selectedOptions.append((str(selection.link), selection))
		self.set_ui_element(ListBuilderWidget(parent, avaliableOptions, selectedOptions))

		self._get_current_value_func = self.ui_element.selectedItems
		self.ui_element.listChanged.connect(self.saveToConfigObject)

avaliable_ui_elements: List[Ui_element] = [String_element, Bool_element, Int_element, Float_element, Selection_element, ReferenceList_element]

def create_interface_element(parent: QWidget, attributeInstance: AttributeInstance) -> Union[None, Ui_element]:
	Attribute = attributeInstance.attributeDefinition
	if(not Attribute.is_placeholder and not Attribute.hidden):
		for ui_element in avaliable_ui_elements:
			if(ui_element.comparisonType == Attribute.type):
				return ui_element(parent, attributeInstance)
	return None