from UI import Configurator
import sys
import Parser
import ConfigurationGenerator


if __name__ == "__main__":
	args 			= Parser.Workspace.getReqiredArgparse().parse_args()
	workspace 		= Parser.Workspace(args.WORKSPACE)
	parser 			= Parser.ConfigParser(workspace)
	systemModel 	= parser.parse()
	configGenerator = ConfigurationGenerator.configGenerator(workspace)
	Interface 		= Configurator()

	mainUI = Interface.buildMainWindow(systemModel, "CustomBox")
	mainUI.register_generate_callback(lambda: configGenerator.generate(systemModel))

	sys.exit(Interface.run())
