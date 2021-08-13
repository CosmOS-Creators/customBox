from PySide6.QtWidgets import QCheckBox, QComboBox, QFormLayout, QLineEdit, QWidget
from UI import Configurator
import sys

if __name__ == "__main__":
	Interface = Configurator()

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

	Interface.buildMainWindow(Pages)
	sys.exit(Interface.run())
