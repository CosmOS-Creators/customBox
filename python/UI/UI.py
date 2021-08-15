from __future__ import annotations
from pathlib import Path
from typing import List, Tuple
from PySide6.QtCore import QEasingCurve, QParallelAnimationGroup, QPoint, QPropertyAnimation, Qt
from PySide6.QtWidgets import QApplication, QCheckBox, QComboBox, QFormLayout, QFrame, QGraphicsDropShadowEffect, QLineEdit, QPushButton, QScrollArea, QSizeGrip, QSizePolicy, QStackedLayout, QVBoxLayout, QWidget, QHBoxLayout
from qt_material import apply_stylesheet
import sys
from UI.support import Icons
from UI.StyleDimensions import styleExtensions

class SeperatorLine(QFrame):
	def __init__(self, parent):
		super().__init__(parent)
		self.setObjectName("seperatorLine")
		self.setFrameShape(QFrame.HLine)
		self.setFrameShadow(QFrame.Sunken)

class sidebar(QWidget):
	def __init__(self, page_layout: QStackedLayout):
		super().__init__()
		self.pageButtons: List[Tuple[QPushButton, str, bool]] = list()
		self.tabButtons: List[QPushButton] = list()
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
		menuButton.setIcon(icons.Icon("menu"))
		menuButton.setIconSize(styleExtensions.SIDEBAR_ICON_SIZE)
		saveButton = QPushButton("Save", self)
		saveButton.setIcon(icons.Icon("save"))
		saveButton.setIconSize(styleExtensions.SIDEBAR_ICON_SIZE)
		newButton = QPushButton("New", self)
		newButton.setIcon(icons.Icon("create"))
		newButton.setIconSize(styleExtensions.SIDEBAR_ICON_SIZE)
		settingsButton = QPushButton("Settings", self)
		settingsButton.setIcon(icons.Icon("settings"))
		settingsButton.setIconSize(styleExtensions.SIDEBAR_ICON_SIZE)

		configPagesScrollArea 	= QScrollArea()
		configPages 			= QWidget()
		configPages.setObjectName("sideMenuScrollArea")
		self.configPagesLayout 	= QVBoxLayout(configPages)
		self.configPagesLayout.setAlignment(Qt.AlignTop)
		configPages.setLayout(self.configPagesLayout)
		self.configPagesLayout.setContentsMargins(0, 0, 0, 0)
		self.configPagesLayout.setSpacing(0)
		configPagesScrollArea.setWidget(configPages)
		configPagesScrollArea.setWidgetResizable(True)
		configPagesScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		configPagesScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

		self.getMaxButtonSize(menuButton)
		self.getMaxButtonSize(saveButton)
		self.getMaxButtonSize(newButton)
		self.getMaxButtonSize(settingsButton)
		self.pageButtons.append((menuButton, menuButton.text(), True))
		self.pageButtons.append((saveButton, saveButton.text(), True))
		self.pageButtons.append((newButton, newButton.text(), True))
		self.pageButtons.append((settingsButton, settingsButton.text(), True))
		self.sidebar_layout.addWidget(menuButton)
		self.sidebar_layout.addWidget(SeperatorLine(self))
		self.sidebar_layout.addWidget(configPagesScrollArea)
		self.sidebar_layout.addWidget(SeperatorLine(self))
		self.sidebar_layout.addWidget(newButton)
		self.sidebar_layout.addWidget(saveButton)
		self.sidebar_layout.addWidget(settingsButton)

		self.numStaticButtons 	= self.sidebar_layout.count() - 1
		self.current_index      = 0
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
		old_button      = self.tabButtons[old_selection]
		new_button      = self.tabButtons[new_selection]
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
		buttonIcon = icons.Icon(icon)
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
		self.tabButtons.append(button)
		self.configPagesLayout.insertWidget(self.current_index, button)
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
			self.isCollapsed = False
			self.setSidebarButtonText()
			self.toggle_animation_1.setStartValue(self.width())
			self.toggle_animation_2.setStartValue(self.width())
			self.toggle_animation_1.setEndValue(self.expandedWidth)
			self.toggle_animation_2.setEndValue(self.expandedWidth)
			self.anim_group.start()
		else:
			self.isCollapsed = True
			self.toggle_animation_1.setStartValue(self.width())
			self.toggle_animation_2.setStartValue(self.width())
			self.toggle_animation_1.setEndValue(self.collapsedWidth)
			self.toggle_animation_2.setEndValue(self.collapsedWidth)
			self.anim_group.start()

	def setSidebarButtonText(self):
		if(self.isCollapsed):
			for button, buttonText, hasIcon in self.pageButtons:
				if(hasIcon):
					button.setText("")
				else:
					button.setText(buttonText[:styleExtensions.SIDEBAR_SHORT_TEXT_LENGTH])
		else:
			for button, buttonText, _ in self.pageButtons:
				button.setText(buttonText)

class TitleBar(QWidget):
	def __init__(self, main_window: MainWindow):
		super().__init__()
		self.main_window = main_window
		self.setObjectName("TitleBar")
		self.setAttribute(Qt.WA_StyledBackground, True)
		self.title_area_layout = QVBoxLayout()
		self.title_area_layout.setContentsMargins(0, 0, 0, 0)
		self.title_area_layout.setSpacing(0)
		self.title_bar_layout = QHBoxLayout()
		self.title_bar_layout.setContentsMargins(0, 0, 0, 0)
		self.title_area_layout.addLayout(self.title_bar_layout)
		self.title_area_layout.addWidget(SeperatorLine(self))
		self.setLayout(self.title_area_layout)

		self.title_bar_layout.setSpacing(0)
		self.title_bar_layout.addStretch()
		self.MinimizeButton = QPushButton(icons.Icon("minimize"), "", clicked=main_window.showMinimized)
		self.MinimizeButton.setIconSize(styleExtensions.TITLEBAR_ICON_SIZE)
		self.MinimizeButton.setObjectName("MinimizeButton")
		self.MaximizeButton = QPushButton(icons.Icon("crop_square"), "", clicked=main_window.toggleMaximized)
		self.MaximizeButton.setIconSize(styleExtensions.TITLEBAR_ICON_SIZE)
		self.MaximizeButton.setObjectName("MaximizeButton")
		self.CloseButton = QPushButton(icons.Icon("close"), "", clicked=main_window.close)
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
				pass
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


class Configurator():
	def __init__(self):
		global icons
		self.app = QApplication([])
		apply_stylesheet(self.app, theme='dark_blue.xml')
		stylesheet = self.app.styleSheet()
		scriptPath = Path(__file__)
		icons = Icons(scriptPath.with_name("icons"))

		with scriptPath.with_name('styles.qss').open("r") as file:
			style = stylesheet + file.read().format(**styleExtensions.get_Parameters())
		self.app.setStyleSheet(style)

	def buildMainWindow(self, Pages):
		w = MainWindow(Pages)
		w.resize(800, 600)
		w.show()

	def run(self):
		return self.app.exec()

if __name__ == "__main__":
	Interface = Configurator()
	Interface.buildMainWindow([])
	sys.exit(Interface.run())
