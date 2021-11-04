from PySide6.QtWidgets import QApplication, QSplashScreen
from qt_material import apply_stylesheet
from pathlib import Path
from UI.support import icons
from UI.StyleDimensions import styleExtensions
from UI.UI import MainWindow
import UI.PageBuilder as pageBuilder
import os

os.environ["QT_FONT_DPI"] = "96"  # FIX Problem for High DPI and Scale above 100%


class Configurator:
    THEME_STYLE_DARK = "dark"
    THEME_STYLE_LIGHT = "light"

    THEME_COLOR_BLUE = "blue"
    THEME_COLOR_RED = "red"
    THEME_COLOR_GREEN = "green"
    THEME_COLOR_YELLOW = "yellow"

    def __init__(self, theme_style: str = THEME_STYLE_DARK, theme_color: str = "blue"):
        scriptPath = Path(__file__)
        icons.set_resources_folder(scriptPath.with_name("resources"))
        if theme_style == self.THEME_STYLE_DARK:
            icons.set_default_color("white")
        elif theme_style == self.THEME_STYLE_LIGHT:
            icons.set_default_color("black")
        else:
            print(
                f'WARNING: "{theme_style}" is an unsupported theme style for icons, defaulting to white icons'
            )
            icons.set_default_color("white")
        self.app = QApplication([])
        self.splash = QSplashScreen(
            icons.Amimation("custombox-logo-animation").pixmap(200)
        )
        self.splash.show()
        stylesheet_name = f"{theme_style}_{theme_color}.xml"
        apply_stylesheet(self.app, theme=stylesheet_name)
        stylesheet = self.app.styleSheet()

        with scriptPath.with_name("styles.qss").open("r") as file:
            style = stylesheet + file.read().format(**styleExtensions.get_Parameters())
        self.app.setStyleSheet(style)

    def buildMainWindow(
        self, SystemConfig, windowTitle: str = "Configurator", window_icon: str = None
    ):
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
