import re
from pathlib import Path

import GeneratorCorePlugins as GeneratorPlugins
from Parser.helpers 		import overrides
from Parser.ConfigTypes		import Configuration

user_group_regex = re.compile(r"\/\*\**\n.*USER SECTION \| Start.*\n.*start_name =(\S+).*\n.*\*\/\n([.\n]*)\/\*\**\n.*stop_name =(\S+).*\n.*USER SECTION \| Stop.*\n.*\*\/")

class sectionParserPlugin(GeneratorPlugins.GeneratorPlugin):
	@overrides(GeneratorPlugins.GeneratorPlugin)
	def preFileGeneration(self, currentTemplateDict: dict, systemConfig: Configuration, file_path: Path):
		if(file_path.exists()):
			with open(file_path, "r") as file:
				fileContent = file.read()
			user_sections = user_group_regex.findall(fileContent)
			print(fileContent)
			for start, userSection, end in user_sections:
				if(start != end):
					raise Exception(f'The user section "{start}" or "{end}" inside the file"{file_path}" was illformed. Please make sure that the user sections are properly closed and opened and not nested.')
				print(userSection)
		return currentTemplateDict
