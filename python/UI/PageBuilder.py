from typing import List, Tuple
from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget
from Parser.ConfigTypes import Configuration, Subconfig
from UI.InterfaceElements import create_interface_element

def buildPage(subconfigs: dict[str, Subconfig], name: str):
	tabwidget 	= QTabWidget()
	tabwidget.setObjectName(name)
	for subconfig in subconfigs.values():
		for element_name, element in subconfig.elements.items():
			page 	= QWidget()
			layout 	= QVBoxLayout()
			page.setLayout(layout)
			tabwidget.addTab(page, element_name)
			for attributeInstance in element.attributeInstances.values():
				new_widget = create_interface_element(page, attributeInstance)
				if(new_widget):
					layout.addWidget(new_widget)
			layout.addStretch()

	return tabwidget

def buildAllPages(config: Configuration):
	pages: List[Tuple[QWidget, str]] = list()
	for page_id, page in config.UiConfig.pages.items():
		# page.viewType
		new_page = buildPage(page.assignedSubconfigs, page.label)
		pages.append((new_page, page.icon))
	return pages
