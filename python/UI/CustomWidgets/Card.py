from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class CardWidget(QFrame):
    def __init__(self, parent: QWidget, widget: QWidget, name: str = None):
        super().__init__(parent)
        self.__layout = QVBoxLayout(self)
        self.__header_widget = QWidget(self)
        self.__header_widget.setObjectName("CardWidgetHeader")
        self.__header_layout = QHBoxLayout(self.__header_widget)
        self.__layout.addWidget(self.__header_widget)
        if name is not None:
            heading = QLabel(name, self)
            heading.setObjectName("CardWidgetHeaderHeading")
            self.__header_layout.addWidget(heading)

        widget.setStyleSheet("background-color: transparent")
        self.__layout.addWidget(widget)

    @property
    def header(self):
        return self.__header_layout
