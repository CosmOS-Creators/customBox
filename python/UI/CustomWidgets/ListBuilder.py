from typing import List, Optional, Tuple
from PySide6.QtCore import QObject, Signal, QSize
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from UI import support
from UI.CustomWidgets.IconButton import iconButton

NUM_OF_SHOWN_LIST_ELEMENTS = 5


class ListBuilderSignals(QObject):
    listChanged = Signal()


class ListBuilderWidget(QFrame):
    MODE_PREDEFINED_OPTIONS = 0
    MODE_CUSTOMIZABLE_OPTIONS = 1

    def __init__(
        self,
        parent: Optional[QWidget],
        selectable_elements: Optional[List[Tuple[str, object]]] = None,
        selected_elements: Optional[List[Tuple[str, object]]] = None,
        mode=MODE_PREDEFINED_OPTIONS,
    ):
        super().__init__(parent)
        self.__should_emit = False
        self.__mode = mode
        self.__signals = ListBuilderSignals()
        self.listChanged = self.__signals.listChanged
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.selected_elements: List[Tuple[str, object]] = list()
        self.available_elements: List[Tuple[str, object]] = list()
        self.__layout_lookup: List[Tuple[object, QWidget]] = list()
        self.widget_layout = QVBoxLayout(self)
        self.add_row_layout = QHBoxLayout()
        self.add_row_layout.setContentsMargins(0, 0, 0, 0)
        self.widget_layout.addLayout(self.add_row_layout)
        self.list_scroll_area = QScrollArea(self)
        self.widget_layout.addWidget(self.list_scroll_area)
        self.list_scroll_area.setWidgetResizable(True)
        self.list_widget = QWidget(self.list_scroll_area)
        self.list_layout = QVBoxLayout(self.list_widget)
        cm = self.list_layout.contentsMargins()
        self.list_layout.setContentsMargins(cm.left(), 0, cm.right(), 0)
        self.list_scroll_area.setWidget(self.list_widget)
        if self.__mode == self.MODE_PREDEFINED_OPTIONS:
            self.avaliable_elements_combobox = QComboBox(self)
            self.add_row_layout.addWidget(self.avaliable_elements_combobox, 1)
        elif self.__mode == self.MODE_CUSTOMIZABLE_OPTIONS:
            self.new_item_textbox = QLineEdit(self)
            self.add_row_layout.addWidget(self.new_item_textbox, 1)
            self.new_item_textbox.returnPressed.connect(self.__addButtonClicked)
        self.add_button = QPushButton(
            "Add to list", self, clicked=self.__addButtonClicked
        )
        self.add_row_layout.addWidget(self.add_button, 0)

        if selectable_elements:
            self.setAvaliableElements(selectable_elements)

        if selected_elements:
            self.setSelectedElements(selected_elements)

        self.__should_emit = True

    def __addButtonClicked(self):
        if self.__mode == self.MODE_PREDEFINED_OPTIONS:
            index = self.avaliable_elements_combobox.currentIndex()
            data = self.avaliable_elements_combobox.itemData(index)
            label = self.avaliable_elements_combobox.itemText(index)
        elif self.__mode == self.MODE_CUSTOMIZABLE_OPTIONS:
            new_item = self.new_item_textbox.text()
            if new_item:
                sameItems = [
                    obj for _, obj in self.selected_elements if obj == new_item
                ]
                if len(sameItems) == 0:
                    label = data = new_item
                    self.new_item_textbox.clear()
                else:
                    QMessageBox.critical(
                        self,
                        "Error adding item",
                        "This exact item already exists in the list",
                    )
                    return
            else:
                QMessageBox.critical(
                    self, "Error adding item", "Adding an empty item is not allowed"
                )
                return
        self.addSelection(label, data)

    def sizeHint(self) -> QSize:
        frame_border = 2
        own_width = self.width()
        own_cm = self.widget_layout.contentsMargins()
        add_row_geometry = self.add_row_layout.geometry()
        height_offset = (
            frame_border
            + own_cm.top()
            + add_row_geometry.height()
            + self.widget_layout.spacing()
            + own_cm.bottom()
        )
        list_height = 0
        for i, (_, list_layout) in enumerate(self.__layout_lookup):
            if i >= NUM_OF_SHOWN_LIST_ELEMENTS:
                break
            list_entry_geometry = list_layout.geometry()
            list_height += list_entry_geometry.height() + self.list_layout.spacing()
        return QSize(own_width, height_offset + list_height)

    def setAvaliableElements(self, selectable_elements: List[Tuple[str, object]]):
        self.__should_emit = False  # keep the changed signal from being emitted while going through the loop
        self.available_elements: List[Tuple[str, object]] = selectable_elements
        # delete all current list elements:
        for _, selected_item in self.selected_elements:
            self.removeSelection(selected_item)

        if self.__mode == self.MODE_PREDEFINED_OPTIONS:
            # remove all selections from the combobox:
            self.avaliable_elements_combobox.clear()
            for avaliable_element_label, avaliable_element in self.available_elements:
                already_selected = False
                for selected_element_label, selected_element in self.selected_elements:
                    if (
                        selected_element == avaliable_element
                        and selected_element_label == avaliable_element_label
                    ):
                        already_selected = True
                if not already_selected:
                    self.avaliable_elements_combobox.addItem(
                        avaliable_element_label, avaliable_element
                    )
        self.setSelectedElements(self.selected_elements)
        self.__should_emit = True

    def setSelectedElements(self, selected_elements):
        emit_restore_value = self.__should_emit
        self.__should_emit = False  # keep the changed signal from being emitted while going through the loop
        self.selected_elements = list()
        wasChaged = False
        for element_label, element in selected_elements:
            self.addSelection(element_label, element)
            wasChaged = True
        self.__should_emit = emit_restore_value  # Restore emitting of signals
        if wasChaged:
            self.__notify_list_changed()

    def removeSelection(self, label: str, element: object):
        matchedLayout = [
            (layout, i)
            for i, (object, layout) in enumerate(self.__layout_lookup)
            if object == element
        ]
        self.selected_elements.remove((label, element))
        if len(matchedLayout) == 1:
            layout, lookup_index = matchedLayout[0]
            found = False
            num_layouts = self.list_layout.count()
            for index in range(num_layouts):
                layout_item = self.list_layout.itemAt(index)
                layout_to_remove = layout_item.layout()
                if layout_to_remove == layout:
                    self.list_layout.takeAt(index)
                    found = True
                    break
            support.clear_layout(layout)
            if found:
                layout.deleteLater()
                del self.__layout_lookup[lookup_index]
            if self.__mode == self.MODE_PREDEFINED_OPTIONS:
                self.avaliable_elements_combobox.addItem(label, element)
            self.__notify_list_changed()
        self.list_scroll_area.updateGeometry()

    def addSelection(self, label: str, element: object):
        if self.__mode == self.MODE_PREDEFINED_OPTIONS:
            index = self.avaliable_elements_combobox.findData(element)
        elif self.__mode == self.MODE_CUSTOMIZABLE_OPTIONS:
            index = 0
        if index != -1:
            line_layout = QHBoxLayout()
            line_label = QLabel(label)
            line_layout.addWidget(line_label, 1)
            line_remove_button = iconButton(
                self.list_scroll_area,
                "close",
                clicked=lambda: self.removeSelection(label, element),
            )
            line_layout.addWidget(line_remove_button, 0)
            self.list_layout.addLayout(line_layout)
            self.selected_elements.append((label, element))
            if self.__mode == self.MODE_PREDEFINED_OPTIONS:
                self.avaliable_elements_combobox.removeItem(index)
            self.__layout_lookup.append((element, line_layout))
            self.__notify_list_changed()
        self.list_scroll_area.updateGeometry()

    def selectedItems(self):
        return [element for _, element in self.selected_elements]

    def __notify_list_changed(self):
        if self.__should_emit:
            self.listChanged.emit()
