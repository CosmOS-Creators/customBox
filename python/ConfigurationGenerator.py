import Parser
from Generator import FileGenerator
import Generator.GeneratorCorePlugins as GeneratorPlugins
from Model import InitializerLogic, MemoryMapperLogic, PermissionerLogic, SchedulerLogic


class configGenerator:
    def __init__(self, workspace: Parser.Workspace, customLogger: GeneratorPlugins.loggerPlugin = None):
        if(customLogger is None):
            self.loggerPlugin = GeneratorPlugins.loggerPlugin()
        else:
            self.loggerPlugin = customLogger
        self.sectionPlugin = GeneratorPlugins.sectionParserPlugin()
        self.logicRunnerPlugin = GeneratorPlugins.logicRunnerPlugin()
        self.timestampPlugin = GeneratorPlugins.timeStampPlugin()
        self.FileCleaner = GeneratorPlugins.fileCleanerPlugin(
            [workspace.ApplicationGeneratedDir, workspace.CoreGeneratedDir]
        )

        self.logicRunnerPlugin.registerLogic(
            [
                SchedulerLogic(),
                InitializerLogic(),
                MemoryMapperLogic(),
                PermissionerLogic(),
            ]
        )
        self.__generator = FileGenerator.Generator(workspace)
        self.__generator.registerPlugin(
            [
                self.loggerPlugin,
                self.sectionPlugin,
                self.logicRunnerPlugin,
                self.FileCleaner,
                self.timestampPlugin,
            ]
        )

    def generate(self, config: Parser.ConfigTypes.Configuration):
        config.clear_placeholders()
        self.__generator.generate(config)

    def generate_from_files(self):
        self.__generator.generate()

    def cancel_generation(self):
        self.__generator.cancel_generation()


if __name__ == "__main__":
    args = Parser.Workspace.getReqiredArgparse().parse_args()
    workspace = Parser.Workspace(args.WORKSPACE)
    myGenerator = configGenerator(workspace)
    myGenerator.generate_from_files()
