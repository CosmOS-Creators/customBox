import re
from pathlib import Path

import Generator.GeneratorCorePlugins as GeneratorPlugins
from Parser.helpers 		import overrides
from Parser.ConfigTypes		import Configuration

user_group_regex = re.compile(r"\/\*\**\n.*USER SECTION \| Start.*\n.*start_name =(\S+).*\n.*\*\/\n([\n\s\S]*?)\/\*\**\n.*stop_name =(?=\1).*\n.*USER SECTION \| Stop.*\n.*\*\/")
ForbiddenSectionNames = ["getSection"]

class Sections():
	def getSection(self, sectionID):
		if(hasattr(self, sectionID)):
			return getattr(self, sectionID)
		else:
			return ""

	def __getitem__(self, key):
		return self.getSection(key)

class sectionParserPlugin(GeneratorPlugins.GeneratorPlugin):
	@overrides(GeneratorPlugins.GeneratorPlugin)
	def preFileGeneration(self, currentTemplateDict: dict, systemConfig: Configuration, file_path: Path):
		if(file_path.exists()):
			with open(file_path, "r") as file:
				fileContent = file.read()
			user_sections = user_group_regex.findall(fileContent)
			sections = Sections()
			for sectionID, userSection in user_sections:
				if(sectionID in ForbiddenSectionNames):
					raise AttributeError(f'A section id with the name "{sectionID}" was requested but this ID is a reserved keyword and thus cannot be used as a section name.')
				setattr(sections, sectionID, userSection.rstrip())
			currentTemplateDict["sections"] = sections
		if(not "sections" in currentTemplateDict):
			currentTemplateDict["sections"] = Sections()
		return currentTemplateDict
