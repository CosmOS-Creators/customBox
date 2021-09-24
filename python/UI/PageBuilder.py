from typing import Dict, List, Tuple
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFormLayout, QLayout, QMessageBox, QScrollArea, QTabWidget, QWidget
from Parser.ConfigTypes import Configuration, Subconfig, ConfigElement, UiPage, UiViewType, UiViewTypes
from UI.CustomWidgets import CardWidget
from UI.FlowLayout import FlowLayout
from UI.InterfaceElements import create_interface_element

class Page():
	viewType: UiViewType = None

	def delete_element(self, element: ConfigElement):
		dlg = QMessageBox(self)
		dlg.setWindowTitle(f'Delete "{str(element.link)}" element')
		dlg.setText(f'Are you sure that you want to remove the "{str(element.link.element)}" element from the config?')
		dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
		dlg.setIcon(QMessageBox.Icon.Question)
		result = dlg.exec()
		if(result == QMessageBox.Yes):
			element.delete()
			return True
		return False

class cardedPage(QScrollArea, Page):
	viewType = UiViewTypes.carded

	def __init__(self, parent: QWidget, page: UiPage):
		super().__init__(parent)
		subconfigs: Dict[str, Subconfig] 	= page.assignedSubconfigs
		page_label: str 					= page.label
		self.setObjectName(page_label)
		self.page_widget = QWidget(self)
		self.setProperty("class", "cardContainer")
		self.grid_layout = FlowLayout(self.page_widget)
		self.grid_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
		self.setWidgetResizable(True)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setWidget(self.page_widget)

		for subconfig in subconfigs.values():
			cards, elements = buildPages(self, subconfig)
			for card_name, card in cards:
				self.grid_layout.addWidget(CardWidget(self.page_widget, card, card_name))

class ScrollingPage(QScrollArea):
	def __init__(self, parent: QWidget, pageWidget: QWidget, mapped_element: ConfigElement):
		super().__init__(parent)
		self.setWidgetResizable(True)
		self.setWidget(pageWidget)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.mapped_element = mapped_element

class tabbedPage(QTabWidget, Page):
	viewType = UiViewTypes.tabbed

	def close_handler(self, index):
		page: ScrollingPage = self.widget(index)
		if(self.delete_element(page.mapped_element)):
			self.removeTab(index)

	def __init__(self, parent: QWidget, page: UiPage):
		super().__init__(parent)
		subconfigs: Dict[str, Subconfig] 	= page.assignedSubconfigs
		page_label: str 					= page.label
		self.setObjectName(page_label)
		if(page.allowElementDeletion):
			self.setTabsClosable(True)
		self.tabCloseRequested.connect(self.close_handler)
		for subconfig in subconfigs.values():
			pages, elements 	= buildPages(self, subconfig)
			for i, (page_name, page) in enumerate(pages):
				new_tab = ScrollingPage(self, page, elements[i])
				self.addTab(new_tab, page_name)

def buildPages(parent: QWidget ,subconfig: Subconfig):
	pages: List[Tuple[str, QWidget]] 	= list()
	elements: List[ConfigElement] 		= list()
	for element_name, element in subconfig.elements.items():
		page 	= QWidget(parent)
		layout 	= QFormLayout(page)
		pages.append((element_name, page))
		elements.append(element)
		for attributeInstance in element.attributeInstances.values():
			new_widget = create_interface_element(page, attributeInstance)
			if(new_widget):
				layout.addRow(*new_widget.get_Row())
	return pages, elements

all_page_types = [tabbedPage, cardedPage]

def buildAllPages(parent, config: Configuration):
	pages: List[Tuple[QWidget, str]] = list()
	for page_id, page in config.UiConfig.pages.items():
		for pageType in all_page_types:
			if(pageType.viewType == page.viewType):
				new_page = pageType(parent, page)
				pages.append((new_page, page.icon))
	return pages
