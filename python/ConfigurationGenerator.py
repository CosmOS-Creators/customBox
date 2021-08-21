import Parser
from Generator 							import FileGenerator
import Generator.GeneratorCorePlugins 	as GeneratorPlugins


if __name__ == "__main__":
	from Model import InitializerLogic, MemoryMapperLogic, PermissionerLogic, SchedulerLogic
	args 				= Parser.Workspace.getReqiredArgparse().parse_args()
	workspace 			= Parser.Workspace(args.WORKSPACE)
	loggerPlugin 		= GeneratorPlugins.loggerPlugin()
	sectionPlugin 		= GeneratorPlugins.sectionParserPlugin()
	logicRunnerPlugin 	= GeneratorPlugins.logicRunnerPlugin()
	timestampPlugin 	= GeneratorPlugins.timeStampPlugin()
	FileCleaner 		= GeneratorPlugins.fileCleanerPlugin([workspace.ApplicationGeneratedDir, workspace.CoreGeneratedDir])

	logicRunnerPlugin.registerLogic([InitializerLogic(), MemoryMapperLogic(), PermissionerLogic(), SchedulerLogic()])
	# try:
	myGenerator = FileGenerator.Generator(workspace)
	myGenerator.registerPlugin([loggerPlugin, sectionPlugin, logicRunnerPlugin, FileCleaner, timestampPlugin])
	myGenerator.generate()
	# except Exception as e:
	# 	print(f"[ERROR] Aborting execution of DefaultConfig.py: {str(e)}")
	# 	exit(1)
