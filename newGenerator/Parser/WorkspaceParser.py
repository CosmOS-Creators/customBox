import os
import json
from typing import List, Union
from pathlib import Path
import argparse
import re

import Parser.helpers as helpers

WORKSPACE_PLACEHOLDER 	= "workspace"

reservedKeys = [WORKSPACE_PLACEHOLDER, "workspaceFilePath", "placeholders", "workspace", "resolvePath", "requireFolder", "requireFile", "getReqiredArgparse"]

class Workspace():
	workspace = os.getcwd()
	def __init__(self, WorkspaceFile: str):
		self.workspaceFilePath = WorkspaceFile
		self.placeholders = [WORKSPACE_PLACEHOLDER]

		with open(WorkspaceFile, "r") as file:
			workspaceFile = json.load(file)
		# first add all elements as they are
		for key in workspaceFile:
			if(key in reservedKeys):
				raise KeyError(f"Workspace file contained the key \"{key}\" which is reserved and not permitted to be used")
			if(type(workspaceFile[key]) is list):
				resolvedPathsList = []
				for path in workspaceFile[key]:
					resolvedPathsList.append(path)
				setattr(self, key, resolvedPathsList)
			elif(type(workspaceFile[key]) is str):
				setattr(self, key, workspaceFile[key])
			else:
				raise TypeError(f"Format of the workspace file \"{WorkspaceFile}\" is invalid. The only supported items are list and str but found {type(workspaceFile[key])}.")
			self.placeholders.append(key)
		# then do placeholder replacement
		for key in workspaceFile:
			property = getattr(self, key)
			if(type(property) is list):
				for i, path in enumerate(property):
					try:
						property[i] = self.resolvePath(path)
					except TypeError as e:
						raise TypeError(f"Error while replacing placeholders in \"{key}\" config: {str(e)}")
			elif(type(property) is str):
				try:
					setattr(self, key, self.resolvePath(property))
				except TypeError as e:
					raise TypeError(f"Error while replacing placeholders in \"{key}\" config: {str(e)}")
			else:
				raise TypeError(f"Format of the workspace file \"{WorkspaceFile}\" is invalid. The only supported items are list and str but found {type(property)}.")
			self.placeholders.append(key)

	def resolvePath(self, path: str):
		resolvedPath = path
		for placeholder in self.placeholders:
			placeholderStr = f"{{{placeholder}}}"
			if(placeholderStr in path):
				replacementValue = getattr(self, placeholder)
				if(type(replacementValue) is str):
					resolvedPath = resolvedPath.replace(placeholderStr, replacementValue)
				else:
					raise TypeError(f"Placeholder \"{placeholder}\" was requested which is of type {type(replacementValue)} but only strings can be used as placeholders.")
		match = re.match(r"{\S+}", resolvedPath)
		if(match):
			raise TypeError(f"Placeholder \"{match.group(0)}\" was requested but did not find a replacement value for it.")

		return resolvedPath

	def requireFolder(self, requiredKeys: Union[List[str], str], createMissingDirs: bool = False):
		""" Check that a config path with a certain name exists
			@createMissingDirs 	If true will create missing dirs instead of throwing an exception.
								If false will check that the path exists and is an actual directory. If not an exception will be raised.
		"""
		requiredKeys = helpers.forceStrList(requiredKeys)
		for key in requiredKeys:
			try:
				folderPaths = getattr(self, key)
			except AttributeError:
				raise AttributeError(f"Workspace \"{self.workspaceFilePath}\" has no attribute \"{key}\" but it was listed as required.")
			if(type(folderPaths) is str):
				folderPaths = [folderPaths]
			for path in folderPaths:
				if(os.path.exists(path)):
					if(not os.path.isdir(path)):
						raise IOError(f"The path \"{path}\" for the config \"{key}\" does not point to a directory")
				elif(createMissingDirs):
					os.makedirs(path)
				else:
					raise IOError(f"The path \"{path}\" for the config \"{key}\" does not exist")

	def requireFile(self, requiredKeys: Union[List[str], str], createMissingDirs: bool = False):
		""" Check that a config path with a certain name exists
			@createMissingDirs 	If true will create missing dirs instead of throwing an exception. This will not create a file, only the directory paths.
								If false will check that the path exists and is an actual existing file. If not an exception will be raised.
		"""
		requiredKeys = helpers.forceStrList(requiredKeys)
		for key in requiredKeys:
			try:
				filePaths = getattr(self, key)
			except AttributeError:
				raise AttributeError(f"Workspace \"{self.workspaceFilePath}\" has no attribute \"{key}\" but it was listed as required.")
			if(type(filePaths) is str):
				filePaths = [filePaths]
			for path in filePaths:
				if(os.path.exists(path)):
					if(not os.path.isfile(path)):
						raise IOError(f"The path \"{path}\" for the config \"{key}\" does not point to a file")
				elif(createMissingDirs):
					os.makedirs(Path(path).parent)
				else:
					raise IOError(f"The path \"{path}\" for the config \"{key}\" does not exist")

	def require(self, requiredKeys: Union[List[str], str]):
		""" Check that a key exists in the workspace file
		"""
		requiredKeys = helpers.forceStrList(requiredKeys)
		for key in requiredKeys:
			try:
				getattr(self, key)
			except AttributeError:
				raise AttributeError(f"Workspace \"{self.workspaceFilePath}\" has no attribute \"{key}\" but it was listed as required.")

	@staticmethod
	def getReqiredArgparse(Argparser: argparse.ArgumentParser = None):
		if(Argparser is None):
			Argparser = argparse.ArgumentParser()
		Argparser.add_argument("WORKSPACE", help="Input workspace file path", type=str)
		return Argparser
