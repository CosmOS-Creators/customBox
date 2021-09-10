from __future__ import annotations
from pathlib import Path
from typing import List, Tuple
from PySide6.QtCore import QEasingCurve, QParallelAnimationGroup, QPoint, QPropertyAnimation, Qt
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QScrollArea, QSizeGrip, QSizePolicy, QStackedLayout, QVBoxLayout, QWidget, QHBoxLayout
from qt_material import apply_stylesheet
import sys
from Parser.ConfigTypes import Configuration
from UI.support import SeperatorLine, icons
from UI.StyleDimensions import styleExtensions
import UI.PageBuilder as pageBuilder


class sidebar(QWidget):
	def __init__(self, parent: QWidget, page_layout: QStackedLayout):
		super().__init__(parent)
		self.pageButtons: List[Tuple[QPushButton, str, bool]] = list()
		self.tabButtons: List[QPushButton] = list()
		self.numPages       = 0
		self.expandedWidth  = 0
		self.collapsedWidth = styleExtensions.SIDEBAR_ICON_SIZE.width() + styleExtensions.SIDEBAR_ICON_PADDING_LEFT + styleExtensions.SIDEBAR_ICON_PADDING_RIGHT

		self.setAttribute(Qt.WA_StyledBackground, True)
		self.setObjectName("sideMenu")
		self.page_layout = page_layout
		self.sidebar_layout = QVBoxLayout(self)
		self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
		self.sidebar_layout.setSpacing(0)
		menuButton = QPushButton("Hide", self, clicked=self.toggleSidebar)
		menuButton.setIcon(icons.Icon("menu"))
		menuButton.setIconSize(styleExtensions.SIDEBAR_ICON_SIZE)
		self.saveButton = QPushButton("Save", self)
		self.saveButton.setIcon(icons.Icon("save"))
		self.saveButton.setIconSize(styleExtensions.SIDEBAR_ICON_SIZE)
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
		self.configPagesLayout.setContentsMargins(0, 0, 0, 0)
		self.configPagesLayout.setSpacing(0)
		configPagesScrollArea.setWidget(configPages)
		configPagesScrollArea.setWidgetResizable(True)
		configPagesScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		configPagesScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

		self.getMaxButtonSize(menuButton)
		self.getMaxButtonSize(self.saveButton)
		self.getMaxButtonSize(newButton)
		self.getMaxButtonSize(settingsButton)
		self.pageButtons.append((menuButton, menuButton.text(), True))
		self.pageButtons.append((self.saveButton, self.saveButton.text(), True))
		self.pageButtons.append((newButton, newButton.text(), True))
		self.pageButtons.append((settingsButton, settingsButton.text(), True))
		self.sidebar_layout.addWidget(menuButton)
		self.sidebar_layout.addWidget(SeperatorLine(self))
		self.sidebar_layout.addWidget(configPagesScrollArea)
		self.sidebar_layout.addWidget(SeperatorLine(self))
		self.sidebar_layout.addWidget(newButton)
		self.sidebar_layout.addWidget(self.saveButton)
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
		button.setToolTip(buttonText)

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
		super().__init__(main_window)
		self.main_window = main_window
		self.setObjectName("TitleBar")
		self.setAttribute(Qt.WA_StyledBackground, True)
		self.title_area_layout = QVBoxLayout(self)
		self.title_area_layout.setContentsMargins(0, 0, 0, 0)
		self.title_area_layout.setSpacing(0)
		self.title_bar_layout = QHBoxLayout()
		self.title_bar_layout.setContentsMargins(0, 0, 0, 0)
		self.title_area_layout.addLayout(self.title_bar_layout)
		self.title_area_layout.addWidget(SeperatorLine(self))

		self.custom_window_title = QLabel(main_window.windowTitle())
		self.custom_window_title.setObjectName("windowTitle")


		self.title_bar_layout.setSpacing(0)
		self.title_bar_layout.addSpacing(50) # placeholder for a potention future icon
		self.title_bar_layout.addWidget(self.custom_window_title)
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

	def mouseDoubleClickEvent(self, event):
		self.main_window.toggleMaximized()

class MainWindow(QWidget):
	def __init__(self, SystemConfig: Configuration, windowTitle: str):
		super().__init__()
		self.maximized = False
		self.setWindowTitle(windowTitle)
		self.setWindowFlags(Qt.FramelessWindowHint)
		self.appLayout      = QVBoxLayout(self)
		self.appLayout.setSpacing(0)
		self.appLayout.setContentsMargins(0, 0, 0, 0)
		self.mainLayout     = QHBoxLayout()
		self.pagesWidget    = QWidget(self)
		self.pagesLayout    = QStackedLayout(self.pagesWidget)
		self.title_bar      = TitleBar(self)
		self.appLayout.addWidget(self.title_bar)
		self.appLayout.addLayout(self.mainLayout)
		self.appLayout.addWidget(QSizeGrip(self), 0, Qt.AlignBottom | Qt.AlignRight)
		self.systemConfig 	= SystemConfig

		self.sidebar = sidebar(self, self.pagesLayout)
		self.sidebar.saveButton.clicked.connect(self.save_config_to_file)

		self.mainLayout.addWidget(self.sidebar)
		self.mainLayout.addWidget(self.pagesWidget, 1)

	def addPages(self, pages: List[QWidget]):
		for i, page in enumerate(pages):
			self.pagesLayout.addWidget(page[0])
			self.sidebar.addPage(page[0], i, page[1])

	def toggleMaximized(self):
		if(self.maximized):
			self.showNormal()
		else:
			self.normalWidth = self.width()
			self.showMaximized()
		self.maximized = not self.maximized

	def isMaximized(self):
		return self.maximized

	def save_config_to_file(self):
		self.systemConfig.serialize()