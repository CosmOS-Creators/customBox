from typing import Dict, List, Tuple
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFormLayout, QLayout, QScrollArea, QTabWidget, QWidget
from Parser.ConfigTypes import Configuration, Subconfig, UiViewType, UiViewTypes
from UI.CustomWidgets import CardWidget
from UI.FlowLayout import FlowLayout
from UI.InterfaceElements import create_interface_element

class Page():
	viewType: UiViewType = None

class cardedPage(QScrollArea, Page):
	viewType = UiViewTypes.carded

	def __init__(self, parent: QWidget, subconfigs: Dict[str, Subconfig], page_label: str):
		super().__init__(parent)
		self.setObjectName(page_label)
		self.page_widget = QWidget(self)
		self.setProperty("class", "cardContainer")
		self.grid_layout = FlowLayout(self.page_widget)
		self.grid_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
		self.setWidgetResizable(True)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setWidget(self.page_widget)

		for subconfig in subconfigs.values():
			cards = buildPage(self, subconfig)
			for card_name, card in cards:
				self.grid_layout.addWidget(CardWidget(self.page_widget, card, card_name))

class tabbedPage(QTabWidget, Page):
	viewType = UiViewTypes.tabbed

	def __init__(self, parent: QWidget, subconfigs: Dict[str, Subconfig], page_label: str):
		super().__init__(parent)
		self.setObjectName(page_label)

		for subconfig in subconfigs.values():
			pages 	= buildPage(self, subconfig)
			for page_name, page in pages:
				scroll_area = QScrollArea(self)
				scroll_area.setWidgetResizable(True)
				scroll_area.setWidget(page)
				scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
				self.addTab(scroll_area, page_name)

def buildPage(parent: QWidget ,subconfig: Subconfig):
	pages: List[Tuple[str, QWidget]] = list()
	for element_name, element in subconfig.elements.items():
		page 	= QWidget(parent)
		layout 	= QFormLayout(page)
		pages.append((element_name, page))
		for attributeInstance in element.attributeInstances.values():
			new_widget = create_interface_element(page, attributeInstance)
			if(new_widget):
				layout.addRow(*new_widget.get_Row())
	return pages

all_page_types = [tabbedPage, cardedPage]

def buildAllPages(parent, config: Configuration):
	pages: List[Tuple[QWidget, str]] = list()
	for page_id, page in config.UiConfig.pages.items():
		for pageType in all_page_types:
			if(pageType.viewType == page.viewType):
				new_page = pageType(parent, page.assignedSubconfigs, page.label)
				pages.append((new_page, page.icon))
	return pages
