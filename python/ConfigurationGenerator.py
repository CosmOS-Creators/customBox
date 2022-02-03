import Parser
from Generator import FileGenerator
import Generator.GeneratorCorePlugins as GeneratorPlugins
from Model import InitializerLogic, MemoryMapperLogic, PermissionerLogic, SchedulerLogic


class configGenerator:
    def __init__(
        self,
        environment: Parser.Environment,
        customLogger: GeneratorPlugins.loggerPlugin = None,
    ):
        if customLogger is None:
            self.loggerPlugin = GeneratorPlugins.loggerPlugin()
        else:
            self.loggerPlugin = customLogger
        self.sectionPlugin = GeneratorPlugins.sectionParserPlugin()
        self.logicRunnerPlugin = GeneratorPlugins.logicRunnerPlugin()
        self.timestampPlugin = GeneratorPlugins.timeStampPlugin()
        self.FileCleaner = GeneratorPlugins.fileCleanerPlugin(
            [environment.ApplicationGeneratedDir, environment.CoreGeneratedDir]
        )

        self.logicRunnerPlugin.registerLogic(
            [
                SchedulerLogic(),
                InitializerLogic(),
                MemoryMapperLogic(),
                PermissionerLogic(),
            ]
        )
        self.__generator = FileGenerator.Generator(environment)
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
    args = Parser.Environment.getReqiredArgparse().parse_args()
    environment = Parser.Environment(args.ENVIRONMENT_CONFIG)
    myGenerator = configGenerator(environment)
    myGenerator.generate_from_files()
