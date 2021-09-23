from PySide6.QtWidgets import QApplication, QSplashScreen
from qt_material import apply_stylesheet
from pathlib import Path
from UI.support import icons
from UI.StyleDimensions import styleExtensions
from UI.UI import MainWindow
import UI.PageBuilder as pageBuilder


class Configurator():
	def __init__(self):
		scriptPath = Path(__file__)
		icons.set_resources_folder(scriptPath.with_name("resources"))
		self.app = QApplication([])
		self.splash = QSplashScreen(icons.Amimation("custombox-logo-animation").pixmap(200))
		self.splash.show()
		apply_stylesheet(self.app, theme='dark_blue.xml')
		stylesheet = self.app.styleSheet()


		with scriptPath.with_name('styles.qss').open("r") as file:
			style = stylesheet + file.read().format(**styleExtensions.get_Parameters())
		self.app.setStyleSheet(style)

	def buildMainWindow(self, SystemConfig, windowTitle: str = "Configurator", window_icon: str = None):
		temp = icons.Icon(window_icon)
		self.app.setWindowIcon(temp)
		w = MainWindow(SystemConfig, windowTitle, window_icon)
		w.resize(800, 600)
		w.show()
		pages = pageBuilder.buildAllPages(w, SystemConfig)
		w.addPages(pages)
		return w

	def run(self, w):
		self.splash.finish(w)
		return self.app.exec()
