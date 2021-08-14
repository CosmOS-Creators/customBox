from PySide6.QtWidgets import QVBoxLayout, QWidget
from UI import Configurator
import sys
import Parser
from UI.InterfaceElements import create_interface_element

if __name__ == "__main__":
	args 		= Parser.Workspace.getReqiredArgparse().parse_args()
	workspace 	= Parser.Workspace(args.WORKSPACE)
	parser 		= Parser.ConfigParser(workspace)
	systemModel = parser.parse()
	Interface 	= Configurator()

	cores 		= systemModel.getSubconfig("cores")
	core_0 		= cores.getElement("core_0")

	page1 		= QWidget()
	page1.setObjectName("Cores")
	page1Layout = QVBoxLayout()

	for element in core_0.attributeInstances.values():
		new_widget = create_interface_element(page1, element)
		if(new_widget):
			page1Layout.addWidget(new_widget)
		# addElementToPage(page1, page1Layout, element)
	page1Layout.addStretch()
	page1.setLayout(page1Layout)

	cores 		= systemModel.getSubconfig("schedulers")
	scheduler_0 = cores.getElement("scheduler_0")

	page2 		= QWidget()
	page2.setObjectName("Schedulers")
	page2Layout = QVBoxLayout()

	for element in scheduler_0.attributeInstances.values():
		new_widget = create_interface_element(page2, element)
		if(new_widget):
			page2Layout.addWidget(new_widget)
	page2Layout.addStretch()
	page2.setLayout(page2Layout)

	Pages = [(page1, "memory"), (page2, "calendar_today")]

	Interface.buildMainWindow(Pages)
	sys.exit(Interface.run())
