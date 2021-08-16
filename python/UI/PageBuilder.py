from typing import Dict, List, Tuple
from PySide6.QtWidgets import QFormLayout, QTabWidget, QVBoxLayout, QWidget
from Parser.ConfigTypes import Configuration, Subconfig, UiViewTypes
from UI.InterfaceElements import Ui_element, create_interface_element

class card(QWidget):
	def __init__(self, parent: QWidget):
		super().__init__(parent)

def buildTabbedPage(subconfigs: dict[str, Subconfig], name: str):
	tabwidget 	= QTabWidget()
	tabwidget.setObjectName(name)
	for subconfig in subconfigs.values():
		pages 	= buildPage(subconfig)
		for page_name, page in pages:
			tabwidget.addTab(page, page_name)
	return tabwidget

def buildPage(subconfig: Subconfig):
	pages: List[Tuple[str, QWidget]] = list()
	for element_name, element in subconfig.elements.items():
		page 	= QWidget()
		layout 	= QFormLayout()
		page.setLayout(layout)
		pages.append((element_name, page))
		for attributeInstance in element.attributeInstances.values():
			new_widget = create_interface_element(page, attributeInstance)
			if(new_widget):
				layout.addRow(*new_widget.get_Row())
	return pages

def buildAllPages(config: Configuration):
	pages: List[Tuple[QWidget, str]] = list()
	for page_id, page in config.UiConfig.pages.items():
		if(page.viewType == UiViewTypes.tabbed):
			new_page = buildTabbedPage(page.assignedSubconfigs, page.label)
			pages.append((new_page, page.icon))
		elif(page.viewType == UiViewTypes.tabbed):
			pass
	return pages
