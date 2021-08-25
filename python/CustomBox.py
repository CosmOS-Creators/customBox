from UI import Configurator
import sys
import Parser


if __name__ == "__main__":
	args 		= Parser.Workspace.getReqiredArgparse().parse_args()
	workspace 	= Parser.Workspace(args.WORKSPACE)
	parser 		= Parser.ConfigParser(workspace)
	systemModel = parser.parse()
	Interface 	= Configurator()

	mainUI = Interface.buildMainWindow(systemModel, "CustomBox")

	sys.exit(Interface.run())
