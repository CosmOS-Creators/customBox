from PySide6.QtWidgets import QPushButton, QWidget
from UI.StyleDimensions import styleExtensions
from UI.support import icons


class iconButton(QPushButton):
    NORMAL = 0
    COMPACT = 1

    def __init__(
        self, parent: QWidget, icon: str, tooltip=None, clicked=None, variant=NORMAL
    ):
        super().__init__(icons.Icon(icon), "", parent, clicked=clicked)
        self.setToolTip(tooltip)
        self.setProperty("class", "iconButton")
        if variant == self.NORMAL:
            pass
        elif variant == self.COMPACT:
            self.setProperty("class", "iconButtonCompact")
        self.setIconSize(styleExtensions.ICON_BUTTON_SIZE)
