from typing import Dict, List, Tuple
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFormLayout, QInputDialog, QLayout, QLineEdit, QMessageBox, QPushButton, QScrollArea, QTabWidget, QWidget
from Parser.ConfigTypes import Configuration, Subconfig, ConfigElement, UiPage, UiViewType, UiViewTypes
from UI.CustomWidgets import CardWidget
from UI.FlowLayout import FlowLayout
from UI.InterfaceElements import create_interface_element
from UI.support import icons

class Page():
	viewType: UiViewType = None
	deletable 		= False
	allowCreation	= False

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

class cardPage(CardWidget):
	def __init__(self, parent: QWidget, page: QWidget, name: str, mapped_element: ConfigElement):
		super().__init__(parent, page, name)
		self.mapped_element = mapped_element

	def addDeleteButton(self, deleteCallback):
		self.header.addStretch()
		close_button = QPushButton(icons.Icon("close"), "", self, clicked=lambda: deleteCallback(self))
		close_button.setProperty("class", "iconButton")
		self.header.addWidget(close_button)

class cardedPage(QScrollArea, Page):
	viewType = UiViewTypes.carded

	def close_handler(self, pageWidget: cardPage):
		print(pageWidget.title())
		if(self.delete_element(pageWidget.mapped_element)):
			self.grid_layout.removeWidget(pageWidget)
			pageWidget.deleteLater()

	def handleElementAdd(self, subconfigs: Dict[str, Subconfig]):
		if(len(subconfigs) == 1):
			text, result = QInputDialog.getText(self, "Element creation", "What name should the new element have?", QLineEdit.Normal)
			if(result):
				for subconfig in subconfigs.values():
					new_element = subconfig.createElement(text)
				return True
			return False

	def __init__(self, parent: QWidget, uiPage: UiPage):
		super().__init__(parent)
		subconfigs: Dict[str, Subconfig] 	= uiPage.assignedSubconfigs
		page_label: str 					= uiPage.label
		self.setObjectName(page_label)
		self.page_widget = QWidget(self)
		self.setProperty("class", "cardContainer")
		self.grid_layout = FlowLayout(self.page_widget)
		self.grid_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
		self.setWidgetResizable(True)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setWidget(self.page_widget)
		if(uiPage.allowElementCreation):
			add_button = QPushButton(icons.Icon("add"), "", self, clicked=lambda: self.handleElementAdd(subconfigs))
			add_button.setProperty("class", "iconButton")
			self.grid_layout.addWidget(add_button)

		for subconfig in subconfigs.values():
			cards, elements = buildPages(self, subconfig)
			for i, (card_name, card) in enumerate(cards):
				new_page = cardPage(self.page_widget, card, card_name, elements[i])
				self.grid_layout.addWidget(new_page)
				if(uiPage.allowElementDeletion):
					new_page.addDeleteButton(self.close_handler)

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

	def __init__(self, parent: QWidget, uiPage: UiPage):
		super().__init__(parent)
		subconfigs: Dict[str, Subconfig] 	= uiPage.assignedSubconfigs
		page_label: str 					= uiPage.label
		self.setObjectName(page_label)
		if(uiPage.allowElementDeletion):
			self.setTabsClosable(True)
		self.tabCloseRequested.connect(self.close_handler)
		for subconfig in subconfigs.values():
			pages, elements = buildPages(self, subconfig)
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
