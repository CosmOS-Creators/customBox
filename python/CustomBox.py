from UI import Configurator, MainWindow, UILoggerPlugin
import sys
import Parser
import ConfigurationGenerator


def wrap_generator(call, mainWindow: MainWindow):
    try:
        call()
    except Exception as ex:
        mainWindow.criticalError("Error during generation", str(ex))


if __name__ == "__main__":
    args = Parser.Workspace.getReqiredArgparse().parse_args()
    workspace = Parser.Workspace(args.WORKSPACE, args.workspace_root)
    parser = Parser.ConfigParser(workspace)
    systemModel = parser.parse()
    Interface = Configurator(
        Configurator.THEME_STYLE_DARK, Configurator.THEME_COLOR_BLUE
    )

    mainUI = Interface.buildMainWindow(systemModel, "CustomBox", "custombox-icon")

    UILogger = UILoggerPlugin(mainUI)
    configGenerator = ConfigurationGenerator.configGenerator(workspace, UILogger)
    # UILogger.register_cancel_callback(configGenerator.cancel_generation)

    generator_call = lambda: configGenerator.generate(systemModel)
    mainUI.register_generate_callback(lambda: wrap_generator(generator_call, mainUI))

    sys.exit(Interface.run(mainUI))
