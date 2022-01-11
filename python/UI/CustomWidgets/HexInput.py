from PySide6.QtWidgets import QSpinBox
from Parser.helpers import toHex, toInt
import math

SPIN_BOX_MAX_DEFAULT_VALUE = 2147483647


class hexInput(QSpinBox):
    def __init__(self, parent) -> None:
        super().__init__(parent=parent)
        self.setMaximum(SPIN_BOX_MAX_DEFAULT_VALUE)
        self.setPrefix("0x")
        self.setDisplayIntegerBase(16)
        self.__alignment = 0

    def valueFromText(self, text):
        return toInt(text)

    def textFromValue(self, value):
        return toHex(value, False)

    def wheelEvent(self, event):
        pass

    def setAlignment(self, align: int):
        self.__alignment = align

    def stepBy(self, steps: int):
        if self.__alignment == 0:
            return super().stepBy(steps)
        else:
            value = self.value()
            if value == 0:
                next_exponent = 1
            else:
                current_exponent = int(round(math.log(value, self.__alignment)))
                if value != self.__alignment ** current_exponent:
                    next_exponent = current_exponent
                else:
                    next_exponent = current_exponent + steps
            if next_exponent == 0:
                new_value = 0
            else:
                new_value = self.__alignment ** next_exponent
        if new_value <= self.maximum() and new_value >= self.minimum():
            self.setValue(new_value)
