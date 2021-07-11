import json
import os
import Parser
from pathlib import Path
from Parser.ConfigParser import discoverConfigFiles, ELEMENTS_KEY

if __name__ == "__main__":
	parser = Parser.Workspace.getReqiredArgparse()
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument("-g", "--generate", help="Generate the default config files from project config", action="store_true")
	group.add_argument("-c", "--check", help="Check if the default config matches with the config structure of the current project", action="store_true")
	args = parser.parse_args()

	workspace = Parser.Workspace(args.WORKSPACE)
	try:
		workspace.requireFolder(["config", "CoreConfig", "DefaultConfig"])
	except AttributeError as e:
		raise AttributeError(f"Aborting execution of DefaultConfig.py: {str(e)}")
	try:
		parser = Parser.ConfigParser(workspace)
		parser.parse() # ensure that there are no syntax errors in the current config by tyring to load it
	except Exception as e:
		raise Exception(f"The input config was not valid: \n{str(e)}")

	allConfigFiles = discoverConfigFiles(workspace.CoreConfig)
	relativeFilePaths = [None] * len(allConfigFiles)
	for i, config in enumerate(allConfigFiles):
		relativeFilePaths[i] = config.relative_to(workspace.CoreConfig)
	BasePath = Path(workspace.DefaultConfig)

	if(args.generate):
		if(os.path.exists(workspace.DefaultConfig)):
			if(not os.path.isdir(workspace.DefaultConfig)):
				raise FileNotFoundError(f"The output path \"{workspace.DefaultConfig}\" id not a directory")
		else:
			os.makedirs(workspace.DefaultConfig)

		for configPath in relativeFilePaths:
			newConfigPath = BasePath.joinpath(configPath.parent)
			if(not os.path.exists(newConfigPath)):
				os.makedirs(newConfigPath)
		for i, configFile in enumerate(allConfigFiles):
			with open(configFile, "r") as file:
				currentConfig = json.load(file)
			currentConfig[ELEMENTS_KEY] = {}
			outPath = BasePath.joinpath(relativeFilePaths[i])
			with open(outPath, "w") as outFile:
				json.dump(currentConfig, outFile, indent=4)
	elif(args.check):
		for i, configPath in enumerate(relativeFilePaths):
			DefaultConfigPath = BasePath.joinpath(configPath)
			try:
				with open(DefaultConfigPath, "r") as file:
					defaultConfig = json.load(file)
			except IOError as e:
				raise IOError(f"ERROR: Default config does not match with core config. Reason: {str(e)}")
			with open(allConfigFiles[i], "r") as file1:
				CoreConfig = json.load(file1)
			CoreConfig[ELEMENTS_KEY] = {}
			if(defaultConfig != CoreConfig):
				raise Exception(f"ERROR: Default config \"{DefaultConfigPath}\" does not match with Core config \"{allConfigFiles[i]}\". Check FAILED\nConsider running the Default config script with the generation option.")
		print("Default config is inline with Core config. Check was SUCCESSFUL")
	else:
		raise NotImplementedError("Either check or generate option must have to be selected.")
