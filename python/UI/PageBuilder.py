from PySide6.QtWidgets import QGridLayout, QLabel, QTabWidget, QVBoxLayout, QWidget
from Parser.ConfigTypes import Subconfig
from UI.InterfaceElements import create_interface_element

def buildPage(config: Subconfig, name: str):
	tabwidget 	= QTabWidget()
	tabwidget.setObjectName(name)

	for element_name, element in config.elements.items():
		page 		= QWidget()
		layout 		= QVBoxLayout()
		page.setLayout(layout)
		tabwidget.addTab(page, element_name)
		for attributeInstance in element.attributeInstances.values():
			new_widget = create_interface_element(page, attributeInstance)
			if(new_widget):
				layout.addWidget(new_widget)
		layout.addStretch()

	return tabwidget
