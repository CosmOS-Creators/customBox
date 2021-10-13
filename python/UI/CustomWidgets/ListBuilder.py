from typing import List, Optional, Tuple
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLayout, QPushButton, QScrollArea, QSizePolicy, QVBoxLayout, QWidget
from UI import support
from UI.support import icons
from UI.CustomWidgets import CardWidget
from UI.CustomWidgets.IconButton import iconButton


class ListBuilderSignals(QObject):
	listChanged = Signal()

class ListBuilderWidget(QWidget):
	def __init__(self, parent: Optional[QWidget], selectable_elements: Optional[List[Tuple[str, object]]] = None, selected_elements: Optional[List[Tuple[str, object]]] = None):
		super().__init__(parent)
		self.__should_emit		= False
		self.__signals 			= ListBuilderSignals()
		self.listChanged		= self.__signals.listChanged
		self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
		self.selected_elements: List[Tuple[str, object]] 	= list()
		self.available_elements: List[Tuple[str, object]] 	= list()
		self.__layout_lookup: List[Tuple[object, QLayout]] 	= list()
		self.widget_layout 	= QVBoxLayout(self)
		self.add_row_layout	= QHBoxLayout()
		self.widget_layout.addLayout(self.add_row_layout)
		self.list_scroll_area = QScrollArea(self)
		self.widget_layout.addWidget(self.list_scroll_area)
		# self.widget_layout.addWidget(QSizeGrip(self), 0 , Qt.AlignBottom | Qt.AlignRight)
		self.list_scroll_area.setWidgetResizable(True)
		self.list_widget	= QWidget(self.list_scroll_area)
		self.list_layout 	= QVBoxLayout(self.list_widget)
		self.list_scroll_area.setWidget(self.list_widget)
		self.avaliable_elements_combobox = QComboBox(self)

		self.add_row_layout.addWidget(self.avaliable_elements_combobox, 1)
		self.add_button = QPushButton("Add to list", self, clicked=self.__addButtonClicked)
		self.add_row_layout.addWidget(self.add_button, 0)

		if(selectable_elements):
			self.setAvaliableElements(selectable_elements)

		if(selected_elements):
			self.setSelectedElements(selected_elements)

		self.__should_emit = True

	def __addButtonClicked(self):
		index = self.avaliable_elements_combobox.currentIndex()
		data = self.avaliable_elements_combobox.itemData(index)
		label = self.avaliable_elements_combobox.itemText(index)
		self.addSelection(label, data)

	def setAvaliableElements(self, selectable_elements: List[Tuple[str, object]]):
		self.__should_emit = False # keep the changed signal from being emitted while going through the loop
		self.available_elements: List[Tuple[str, object]] = selectable_elements
		# delete all current list elements:
		for _, selected_item in self.selected_elements:
			self.removeSelection(selected_item)

		#remove all selections from the combobox:
		self.avaliable_elements_combobox.clear()
		for avaliable_element_label, avaliable_element in self.available_elements:
			already_selected = False
			for selected_element_label, selected_element in self.selected_elements:
				if(selected_element == avaliable_element and selected_element_label == avaliable_element_label):
					already_selected = True
			if(not already_selected):
				self.avaliable_elements_combobox.addItem(avaliable_element_label, avaliable_element)
		self.setSelectedElements(self.selected_elements)
		self.__should_emit = True

	def setSelectedElements(self, selected_elements):
		emit_restore_value 		= self.__should_emit
		self.__should_emit 		= False # keep the changed signal from being emitted while going through the loop
		self.selected_elements 	= list()
		wasChaged 				= False
		for element_label, element in selected_elements:
			self.addSelection(element_label, element)
			wasChaged = True
		self.__should_emit = emit_restore_value # Restore emitting of signals
		if(wasChaged):
			self.__notify_list_changed()

	def removeSelection(self, label: str, element: object):
		matchedLayout = [(layout, i) for i, (object, layout) in enumerate(self.__layout_lookup) if object == element]
		if(len(matchedLayout) == 1):
			layout, lookup_index = matchedLayout[0]
			found = False
			num_layouts = self.list_layout.count()
			for index in range(num_layouts):
				l = self.list_layout.itemAt(index)
				if(l == layout):
					self.list_layout.takeAt(index)
					found = True
					break
			support.clear_layout(layout)
			if(found):
				layout.deleteLater()
				del self.__layout_lookup[lookup_index]
			self.avaliable_elements_combobox.addItem(label, element)
			self.__notify_list_changed()

	def addSelection(self, label: str, element: object):
		index = self.avaliable_elements_combobox.findData(element)
		if(index != -1):
			line_layout = QHBoxLayout()
			line_label = QLabel(label)
			line_label.setObjectName("ListBuilder_LineLabel")
			line_layout.addWidget(line_label, 1)
			line_remove_button = iconButton(self.list_scroll_area, "close", clicked=lambda: self.removeSelection(label, element))
			line_layout.addWidget(line_remove_button, 0)
			self.list_layout.addLayout(line_layout)
			self.selected_elements.append((label, element))
			self.avaliable_elements_combobox.removeItem(index)
			self.__layout_lookup.append((element, line_layout))
			self.list_widget.updateGeometry()
			self.__notify_list_changed()

	def selectedItems(self):
		return [element for _, element in self.selected_elements]

	def __notify_list_changed(self):
		if(self.__should_emit):
				self.listChanged.emit()
