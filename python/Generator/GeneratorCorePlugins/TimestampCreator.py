import re
from pathlib import Path
from typing import List
from datetime 	import datetime

import Generator.GeneratorPluginSkeleton as PluginSkeleton
from Parser.helpers 		import overrides

defaultTimestampFormat = "%Y-%m-%d"
defaultTimestampRegex  = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
MultiLineCommentRegex  = re.compile(r"(\/\*(?:\*(?!\/)|[^*])*\*\/)")
SingleLineCommentRegex = re.compile(r"(^.*\/\/.*$)")

templateDateVariableName = "date"

class timeStampPlugin(PluginSkeleton.GeneratorPlugin):
	def __init__(self, disableTimestamps: bool = False, timestampFormat: str = None, timestampIgnoreRegex: str = None):
		self.__disable_timestamps = disableTimestamps
		if(timestampFormat):
			self.__time_format = timestampFormat
			if(not timestampIgnoreRegex):
				raise AttributeError(f'Error for timestamp plugin init. Parameter "timestampFormat" is given but parameter "timestampIgnoreRegex" is not. but it is mandatory.')
			else:
				self.__timestampRegex 	= re.compile(timestampIgnoreRegex)
		else:
			self.__time_format			= defaultTimestampFormat
			self.__timestampRegex 		= defaultTimestampRegex

	def __eraseTimestamp(self, file_content: str):
		def replace(commentString, file_content):
			out_file = file_content
			for comment in commentString:
				newComment = comment
				matches = self.__timestampRegex.findall(comment)
				for match in matches:
					newComment = newComment.replace(match, "")
				out_file = out_file.replace(comment, newComment)
			return out_file
		multilineComments 	= MultiLineCommentRegex.findall(file_content)
		singlelineComments 	= SingleLineCommentRegex.findall(file_content)
		file_content = replace(multilineComments, file_content)
		file_content = replace(singlelineComments, file_content)
		return file_content

	@overrides(PluginSkeleton.GeneratorPlugin)
	def preFileGeneration(self, currentTemplateDict: dict, systemConfig, file_path: Path):
		if(self.__disable_timestamps):
			currentTemplateDict[templateDateVariableName] = ""
		else:
			currentTemplateDict[templateDateVariableName] = datetime.now().strftime(self.__time_format)
		return currentTemplateDict

	@overrides(PluginSkeleton.GeneratorPlugin)
	def postFileGeneration(self, file_path: Path, file_content: str):
		if(file_path.exists()):
			with open(file_path, "r") as oldFile:
				old_file_content = oldFile.read()
			new = self.__eraseTimestamp(file_content)
			old = self.__eraseTimestamp(old_file_content)
			return new != old
		else:
			return True
