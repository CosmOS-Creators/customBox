from __future__ import annotations
from pathlib import Path
from typing import List, Tuple
from PySide6.QtCore import QEasingCurve, QParallelAnimationGroup, QPoint, QPropertyAnimation, Qt
from PySide6.QtWidgets import QApplication, QCheckBox, QComboBox, QFormLayout, QGraphicsDropShadowEffect, QLineEdit, QPushButton, QSizeGrip, QSizePolicy, QStackedLayout, QVBoxLayout, QWidget, QHBoxLayout
from qt_material import apply_stylesheet
import sys
from support import Icon
from StyleDimensions import styleExtensions

class sidebar(QWidget):
    def __init__(self, page_layout: QStackedLayout):
        super().__init__()
        self.pageButtons: List[Tuple[QPushButton, str, bool]] = list()
        self.numPages       = 0
        self.expandedWidth  = 0
        self.collapsedWidth = styleExtensions.SIDEBAR_ICON_SIZE.width() + styleExtensions.SIDEBAR_ICON_PADDING_LEFT + styleExtensions.SIDEBAR_ICON_PADDING_RIGHT

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("sideMenu")
        self.page_layout = page_layout
        self.sidebar_layout = QVBoxLayout()
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(0)
        self.setLayout(self.sidebar_layout)
        menuButton = QPushButton("Hide", self, clicked=self.toggleSidebar)
        menuButton.setIcon(Icon("menu"))
        menuButton.setIconSize(styleExtensions.SIDEBAR_ICON_SIZE)
        settingsButton = QPushButton("Settings", self)
        settingsButton.setIcon(Icon("settings"))
        settingsButton.setIconSize(styleExtensions.SIDEBAR_ICON_SIZE)
        self.getMaxButtonSize(menuButton)
        self.getMaxButtonSize(settingsButton)
        self.pageButtons.append((menuButton, menuButton.text(), True))
        self.pageButtons.append((settingsButton, settingsButton.text(), True))
        self.sidebar_layout.addWidget(menuButton)
        self.sidebar_layout.addStretch()
        self.sidebar_layout.addWidget(settingsButton)
        self.current_index      = self.sidebar_layout.count() - 2
        self.isCollapsed        = True

        self.toggle_animation_1 = QPropertyAnimation(self, b"minimumWidth")
        self.toggle_animation_1.setEasingCurve(QEasingCurve.InOutQuart)
        self.toggle_animation_1.setDuration(250)
        self.toggle_animation_2 = QPropertyAnimation(self, b"maximumWidth")
        self.toggle_animation_2.setEasingCurve(QEasingCurve.InOutQuart)
        self.toggle_animation_2.setDuration(250)
        self.anim_group = QParallelAnimationGroup()
        self.anim_group.addAnimation(self.toggle_animation_1)
        self.anim_group.addAnimation(self.toggle_animation_2)
        self.anim_group.finished.connect(self.setSidebarButtonText)

        self.setMaximumWidth(self.collapsedWidth)
        self.setMinimumWidth(self.collapsedWidth)

    def switchSelection(self, new_selection):
        old_selection   = self.page_layout.currentIndex()
        old_button      = self.pageButtons[2:][old_selection][0]
        new_button      = self.pageButtons[2:][new_selection][0]
        old_button.setProperty("Selected", "false")
        new_button.setProperty("Selected", "true")
        self.refreshStyle(old_button)
        self.refreshStyle(new_button)
        old_button.setStyleSheet("text-align: left") # This is needed for some reason to have the button update when it is switched
        new_button.setStyleSheet("text-align: left")
        self.page_layout.setCurrentIndex(new_selection)

    def refreshStyle(self, widget: QWidget):
        widget.setStyleSheet(widget.styleSheet())

    def addPage(self, widget: QWidget, layout_index, icon = None):
        buttonIcon = Icon(icon)
        buttonText = widget.objectName()
        if(buttonIcon):
            button = QPushButton(buttonIcon, buttonText, self)
            button.setIconSize(styleExtensions.SIDEBAR_ICON_SIZE)
            hasIcon = True
        else:
            button = QPushButton(buttonText, self)
            hasIcon = False
        button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        button.clicked.connect(lambda: self.switchSelection(layout_index))
        button.setAttribute(Qt.WA_StyledBackground, True)

        if(self.numPages == 0):
            button.setProperty("Selected", "true")
        self.pageButtons.append((button, buttonText, hasIcon))
        self.sidebar_layout.insertWidget(self.current_index, button)
        self.current_index += 1
        self.numPages += 1
        self.getMaxButtonSize(button)
        self.setSidebarButtonText()

    def getMaxButtonSize(self, button):
        button.adjustSize()
        if(self.expandedWidth < button.width()):
            self.expandedWidth = button.width()

    def toggleSidebar(self):
        if(self.isCollapsed):
            for button, buttonText, _ in self.pageButtons:
                button.setText(buttonText)
            self.toggle_animation_1.setStartValue(self.width())
            self.toggle_animation_2.setStartValue(self.width())
            self.toggle_animation_1.setEndValue(self.expandedWidth)
            self.toggle_animation_2.setEndValue(self.expandedWidth)
            self.anim_group.start()
            self.isCollapsed = False
        else:
            self.toggle_animation_1.setStartValue(self.width())
            self.toggle_animation_2.setStartValue(self.width())
            self.toggle_animation_1.setEndValue(self.collapsedWidth)
            self.toggle_animation_2.setEndValue(self.collapsedWidth)
            self.anim_group.start()
            self.isCollapsed = True

    def setSidebarButtonText(self):
        if(self.isCollapsed):
            for button, buttonText, hasIcon in self.pageButtons:
                if(hasIcon):
                    button.setText("")
                else:
                    button.setText(buttonText[0:2])

class TitleBar(QWidget):
    def __init__(self, main_window: MainWindow):
        super().__init__()
        self.main_window = main_window
        self.setObjectName("TitleBar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.title_bar_layout = QHBoxLayout()
        self.title_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.title_bar_layout)

        self.title_bar_layout.setSpacing(0)
        self.title_bar_layout.addStretch()
        self.MinimizeButton = QPushButton(Icon("minimize"), "", clicked=main_window.showMinimized)
        self.MinimizeButton.setIconSize(styleExtensions.TITLEBAR_ICON_SIZE)
        self.MinimizeButton.setObjectName("MinimizeButton")
        self.MaximizeButton = QPushButton(Icon("crop_square"), "", clicked=main_window.toggleMaximized)
        self.MaximizeButton.setIconSize(styleExtensions.TITLEBAR_ICON_SIZE)
        self.MaximizeButton.setObjectName("MaximizeButton")
        self.CloseButton = QPushButton(Icon("close"), "", clicked=main_window.close)
        self.CloseButton.setIconSize(styleExtensions.TITLEBAR_ICON_SIZE)
        self.CloseButton.setObjectName("CloseButton")
        self.title_bar_layout.addWidget(self.MinimizeButton)
        self.title_bar_layout.addWidget(self.MaximizeButton)
        self.title_bar_layout.addWidget(self.CloseButton)

        # shadow = QGraphicsDropShadowEffect()
        # shadow.setBlurRadius(15)
        # self.setGraphicsEffect(shadow)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.window_offset: QPoint = event.position().toPoint()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.window_offset is not None and event.buttons() == Qt.LeftButton:
            if(self.main_window.isMaximized()):
                pass
                # TODO: Fix this later, when dragging the title bar on a maximized window it should be returned to the previous size but stay perfectly at the users mouse cursor
                # width_before = self.main_window.size().width()
                # self.main_window.toggleMaximized()
                # correction = width_before - self.main_window.normalWidth
                # self.window_offset.setX(self.window_offset.x() - correction)
            else:
                self.main_window.move(self.main_window.pos() + event.position().toPoint() - self.window_offset)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.window_offset = None
        super().mouseReleaseEvent(event)

class MainWindow(QWidget):
    def __init__(self, pages: List[QWidget]):
        super().__init__()
        self.maximized = False
        self.setWindowTitle("Configurator")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.appLayout      = QVBoxLayout()
        self.appLayout.setSpacing(0)
        self.appLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout     = QHBoxLayout()
        self.pagesWidget    = QWidget()
        self.pagesLayout    = QStackedLayout()
        self.title_bar      = TitleBar(self)
        self.appLayout.addWidget(self.title_bar)
        self.appLayout.addLayout(self.mainLayout)
        self.appLayout.addWidget(QSizeGrip(self), 0, Qt.AlignBottom | Qt.AlignRight)
        self.setLayout(self.appLayout)

        self.sidebar = sidebar(self.pagesLayout)

        for i, page in enumerate(pages):
            self.pagesLayout.addWidget(page[0])
            self.sidebar.addPage(page[0], i, page[1])

        self.pagesWidget.setLayout(self.pagesLayout)
        self.mainLayout.addWidget(self.sidebar)
        self.mainLayout.addWidget(self.pagesWidget, 1)

    def toggleMaximized(self):
        if(self.maximized):
            self.showNormal()
        else:
            self.normalWidth = self.width()
            self.showMaximized()
        self.maximized = not self.maximized

    def isMaximized(self):
        return self.maximized


if __name__ == "__main__":
    app = QApplication([])
    apply_stylesheet(app, theme='dark_blue.xml')
    stylesheet = app.styleSheet()
    scriptPath = Path(__file__)

    with scriptPath.with_name('styles.qss').open("r") as file:
        style = stylesheet + file.read().format(**styleExtensions.get_Parameters())
    app.setStyleSheet(style)

    page1 = QWidget()
    page1.setObjectName("Cores")
    page1Layout = QFormLayout()
    page1Layout.addRow("Core Name:", QLineEdit(page1))
    page1Layout.addRow("Boot OS:", QCheckBox(page1))
    page1Layout.addRow("Is ComOS core:", QCheckBox(page1))
    page1Layout.addRow("Memory location:", QComboBox(page1))
    page1.setLayout(page1Layout)

    page2 = QWidget()
    page2.setObjectName("Scheduler")
    page2Layout = QFormLayout()
    page2Layout.addRow("Hyper tick of this scheduler:", QLineEdit())
    page2Layout.addRow("Synchronization period:", QLineEdit())
    page2Layout.addRow("Synchronization:", QCheckBox())
    page2.setLayout(page2Layout)

    Pages = [(page1, "memory"), (page2, "calendar_today")]

    w = MainWindow(Pages)
    w.resize(800, 600)
    w.show()

    sys.exit(app.exec())
