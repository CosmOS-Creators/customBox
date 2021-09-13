from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet
from pathlib import Path
from UI.support import icons
from UI.StyleDimensions import styleExtensions
from UI.UI import MainWindow
import UI.PageBuilder as pageBuilder


class Configurator():
	def __init__(self):
		self.app = QApplication([])
		apply_stylesheet(self.app, theme='dark_blue.xml')
		stylesheet = self.app.styleSheet()
		scriptPath = Path(__file__)
		icons.set_icon_folder(scriptPath.with_name("icons"))

		with scriptPath.with_name('styles.qss').open("r") as file:
			style = stylesheet + file.read().format(**styleExtensions.get_Parameters())
		self.app.setStyleSheet(style)

	def buildMainWindow(self, SystemConfig, windowTitle: str = "Configurator"):
		w = MainWindow(SystemConfig, windowTitle)
		w.resize(800, 600)
		w.show()
		pages = pageBuilder.buildAllPages(w, SystemConfig)
		w.addPages(pages)
		return w

	def run(self):
		return self.app.exec()
