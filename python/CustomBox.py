from typing import List, Tuple
from PySide6.QtWidgets import QVBoxLayout, QWidget
from UI import Configurator
import sys
import Parser
from UI.InterfaceElements import create_interface_element
from UI.PageBuilder import buildPage

if __name__ == "__main__":
	args 		= Parser.Workspace.getReqiredArgparse().parse_args()
	workspace 	= Parser.Workspace(args.WORKSPACE)
	parser 		= Parser.ConfigParser(workspace)
	systemModel = parser.parse()
	Interface 	= Configurator()

	pages: List[Tuple[QWidget, str]] = list()
	for subconfig_name, subconfig in systemModel.configs.items():
		new_page = buildPage(subconfig, subconfig_name)
		pages.append((new_page, None))

	Interface.buildMainWindow(pages)
	sys.exit(Interface.run())
