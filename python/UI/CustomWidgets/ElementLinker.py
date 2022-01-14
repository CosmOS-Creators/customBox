from typing import List, Tuple
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMessageBox, QPushButton, QVBoxLayout, QWidget
from Parser.LinkElement import Link


class RelinkDialog(QDialog):
    def __init__(self, parent: QWidget, options: List[Tuple[str, Link]], link_callback, supported = False):
        super().__init__(parent)
        self.link_callback = link_callback
        self.__supported_operation = supported

        self.setWindowTitle("Select parent")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.confirm)
        self.buttonBox.rejected.connect(self.abort)

        self.layout1 = QVBoxLayout(self)
        self.listWidget = QListWidget(self)
        self.listWidget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        for option_str, option in options:
            newItem = QListWidgetItem()
            newItem.setData(Qt.UserRole, option)
            newItem.setText(option_str)
            self.listWidget.addItem(newItem)
        self.layout1.addWidget(QLabel("Select the new item you want to set as a Parent"))
        self.layout1.addWidget(self.listWidget)
        self.layout1.addWidget(self.buttonBox)

    def confirm(self):
        if(self.__supported_operation):
            self.link_callback(self.listWidget.selectedItems()[0].data(Qt.UserRole))
        else:
            QMessageBox.information(self, "Not yet implemented", "Relinking items is not yet implemented")
        self.accept()

    def abort(self):
        self.reject()


class LinkerWidget(QWidget):
    def __init__(self, parent: QWidget, current_link: Link, get_link_options_callback, relink_callback, link_callback) -> None:
        super().__init__(parent=parent)
        self.get_link_options = get_link_options_callback
        self.relink_callback = relink_callback
        self.link_callback = link_callback
        self.setContentsMargins(0,0,0,0)
        self.setStyleSheet("background-color: 3px solid red;")

        self.__link_label = None
        self.__widget_layout = QHBoxLayout(self)
        self.__widget_layout.setContentsMargins(0, 0, 0, 0)
        if(current_link is not None):
            self.__link_label = QLabel(str(current_link), self)
            self.__widget_layout.addWidget(self.__link_label, 0)
            button_text = "Change Parent"
            self.__clicked_callback = self.open_relink_dialog
        else:
            button_text = "Set Parent"
            self.__clicked_callback = self.open_link_dialog
        self.set_parent_button = QPushButton(button_text, self, clicked=self.__clicked_callback)
        self.__widget_layout.addWidget(self.set_parent_button, 1)

    def open_relink_dialog(self):
        link_options = self.get_link_options()
        dialog = RelinkDialog(self, link_options, self.relink_callback, False)
        dialog.exec()
        dialog.deleteLater()

    def open_link_dialog(self):
        link_options = self.get_link_options()
        dialog = RelinkDialog(self, link_options, self.link_callback, True)
        dialog.exec()
        dialog.deleteLater()

    def set_linked_state(self, is_already_linked: bool, current_link: Link = None):
        if(is_already_linked and self.__link_label is None):
            self.__link_label = QLabel(current_link.getLink(), self)
            self.__widget_layout.insertWidget(0, self.__link_label, 0)
            button_text = "Change Parent"
            clicked_callback = self.open_relink_dialog
        else:
            button_text = "Set Parent"
            clicked_callback = self.open_link_dialog
        self.set_parent_button.setText(button_text)
        self.set_parent_button.clicked.disconnect(self.__clicked_callback)
        self.set_parent_button.clicked.connect(clicked_callback)
        self.__clicked_callback = clicked_callback
