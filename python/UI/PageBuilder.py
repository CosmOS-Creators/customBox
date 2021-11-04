from typing import Dict, List, Tuple
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QInputDialog,
    QLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QWidget,
)
from Parser.ConfigTypes import (
    Configuration,
    Subconfig,
    ConfigElement,
    UiPage,
    UiViewType,
    UiViewTypes,
)
from UI.CustomWidgets import CardWidget
from UI.CustomWidgets import iconButton
from UI.FlowLayout import FlowLayout
from UI.InterfaceElements import create_interface_element
from UI.support import icons


class ContainerPage:
    viewType: UiViewType = None
    deletable = False
    allowCreation = False

    def delete_element(self, element: ConfigElement):
        dlg = QMessageBox(self)
        dlg.setWindowTitle(f'Delete "{str(element.link)}" element')
        dlg.setText(
            f'Are you sure that you want to remove the "{str(element.link.element)}" element from the config?'
        )
        dlg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        dlg.setIcon(QMessageBox.Icon.Question)
        result = dlg.exec()
        if result == QMessageBox.Yes:
            element.delete()
            return True
        return False


class cardPage(CardWidget):
    def __init__(
        self,
        parent: QWidget,
        page: QWidget,
        name: str,
        mapped_element: ConfigElement,
        uiPage: UiPage,
    ):
        super().__init__(parent, page, name)
        self.mapped_element = mapped_element
        self.uiPage = uiPage
        self.header.addStretch()

    def addHandlers(self, createHandler, deleteHandler):
        if self.uiPage.allowElementCreation:
            add_button = iconButton(
                self,
                "add",
                "Add a new element of the same type",
                clicked=lambda: createHandler(),
            )
            self.header.addWidget(add_button)
        if self.uiPage.allowElementDeletion:
            delete_button = iconButton(
                self,
                "close",
                "Delete this element",
                clicked=lambda: deleteHandler(self),
            )
            self.header.addWidget(delete_button)


class cardedPage(QScrollArea, ContainerPage):
    viewType = UiViewTypes.carded

    def delete_handler(self, pageWidget: cardPage):
        if self.delete_element(pageWidget.mapped_element):
            self.grid_layout.removeWidget(pageWidget)
            pageWidget.deleteLater()

    def create_element_handler(self, subconfig: Subconfig, uiPage: UiPage):
        element_name, result = QInputDialog.getText(
            self,
            "Element creation",
            "What name should the new element have?",
            QLineEdit.Normal,
        )
        if result:
            try:
                new_element = subconfig.createElement(element_name)
            except Exception as e:
                error_msg = QMessageBox(self)
                error_msg.critical(self, "Error creating element", str(e))
                return
            _, card, _ = buildElement(self, element_name, new_element)
            new_page = cardPage(
                self.page_widget, card, element_name, new_element, uiPage
            )
            new_page.addHandlers(
                lambda: self.create_element_handler(subconfig, uiPage),
                self.delete_handler,
            )
            self.grid_layout.addWidget(new_page)

    def __init__(self, parent: QWidget, uiPage: UiPage):
        super().__init__(parent)
        subconfigs: Dict[str, Subconfig] = uiPage.assignedSubconfigs
        page_label: str = uiPage.label
        self.setObjectName(page_label)
        self.page_widget = QWidget(self)
        self.setProperty("class", "cardContainer")
        self.grid_layout = FlowLayout(self.page_widget)
        self.grid_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.page_widget)

        for subconfig in subconfigs.values():
            cards = buildElements(self, subconfig)
            for card_name, card, element in cards:
                new_page = cardPage(self.page_widget, card, card_name, element, uiPage)
                new_page.addHandlers(
                    lambda: self.create_element_handler(subconfig, uiPage),
                    self.delete_handler,
                )
                self.grid_layout.addWidget(new_page)


class ScrollingPage(QScrollArea):
    def __init__(
        self, parent: QWidget, pageWidget: QWidget, mapped_element: ConfigElement
    ):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setWidget(pageWidget)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.mapped_element = mapped_element


class tabbedPage(QTabWidget, ContainerPage):
    viewType = UiViewTypes.tabbed

    def close_handler(self, index):
        page: ScrollingPage = self.widget(index)
        if self.delete_element(page.mapped_element):
            self.removeTab(index)

    def add_handler(self, subconfigs: Dict[str, Subconfig]):
        if len(subconfigs) == 1:
            subconfig = list(subconfigs.values())[0]
        else:
            subconfig_keys = list(subconfigs.keys())
            subconfig_key, result = QInputDialog.getItem(
                self,
                "Element creation",
                "Choose the subconfig for which to create an element for:",
                subconfig_keys,
                0,
            )
            if result:
                subconfig = subconfigs[subconfig_key]
            else:
                return
        element_name, result = QInputDialog.getText(
            self,
            "Element creation",
            "What name should the new element have?",
            QLineEdit.Normal,
        )
        if result:
            try:
                new_element = subconfig.createElement(element_name)
            except Exception as e:
                error_msg = QMessageBox(self)
                error_msg.critical(self, "Error creating element", str(e))
                return
            _, tab, _ = buildElement(self, element_name, new_element)
            new_page = ScrollingPage(self, tab, new_element)
            self.addTab(new_page, element_name)

    def __init__(self, parent: QWidget, uiPage: UiPage):
        super().__init__(parent)
        subconfigs: Dict[str, Subconfig] = uiPage.assignedSubconfigs
        page_label: str = uiPage.label
        self.setObjectName(page_label)
        if uiPage.allowElementDeletion:
            self.setTabsClosable(True)
        if uiPage.allowElementCreation:
            add_button = iconButton(
                self,
                "add",
                "Add a new element",
                clicked=lambda: self.add_handler(subconfigs),
            )
            self.setCornerWidget(add_button)
        self.tabCloseRequested.connect(self.close_handler)
        for subconfig in subconfigs.values():
            tabs = buildElements(self, subconfig)
            for tab_name, tab, element in tabs:
                new_tab = ScrollingPage(self, tab, element)
                self.addTab(new_tab, tab_name)


def buildElement(parent: QWidget, element_name: str, element: ConfigElement):
    page = QWidget(parent)
    layout = QFormLayout(page)
    for attributeInstance in element.attributeInstances.values():
        new_widget = create_interface_element(page, attributeInstance)
        if new_widget:
            layout.addRow(*new_widget.get_Row())
    return (element_name, page, element)


def buildElements(parent: QWidget, subconfig: Subconfig):
    pages: List[Tuple[str, QWidget, ConfigElement]] = list()
    for element_name, element in subconfig.elements.items():
        new_page = buildElement(parent, element_name, element)
        pages.append(new_page)
    return pages


all_page_types = [tabbedPage, cardedPage]


def buildAllPages(parent, config: Configuration):
    pages: List[Tuple[QWidget, str]] = list()
    for page_id, page in config.UiConfig.pages.items():
        for pageType in all_page_types:
            if pageType.viewType == page.viewType:
                new_page = pageType(parent, page)
                pages.append((new_page, page.icon))
    return pages
