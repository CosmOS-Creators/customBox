from typing import List
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QWidget
from Parser.LinkElement import Link


class RelinkDialog(QDialog):
    def __init__(self, parent: QWidget, options: List[Link], relink_callback):
        super().__init__(parent)
        self.relink_callback = relink_callback

        self.setWindowTitle("Select parent")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout1 = QVBoxLayout(self)
        self.listWidget = QListWidget(self)
        self.listWidget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        for option in options:
            newItem = QListWidgetItem()
            newItem.setData(Qt.UserRole, option)
            newItem.setText(str(option))
            self.listWidget.addItem(newItem)
        self.layout1.addWidget(QLabel("Select the new item you want to set as a Parent"))
        self.layout1.addWidget(self.listWidget)
        self.layout1.addWidget(self.buttonBox)

    def accept(self):
        self.relink_callback(self.listWidget.selectedItems()[0].data(Qt.UserRole))
        self.close()

    def reject(self):
        self.close()


class LinkerWidget(QWidget):
    def __init__(self, parent: QWidget, current_link: Link, link_options: List[Link], relink_callback) -> None:
        super().__init__(parent=parent)
        self.link_options = link_options
        self.relink_callback = relink_callback
        layout = QHBoxLayout(self)
        layout.addWidget(QLabel(str(current_link), self))
        layout.addWidget(QPushButton("Change Parent", self, clicked=self.open_relink_dialog))

    def open_relink_dialog(self):
        dialog = RelinkDialog(self, self.link_options, self.relink_callback)
        dialog.exec()
        dialog.deleteLater()
