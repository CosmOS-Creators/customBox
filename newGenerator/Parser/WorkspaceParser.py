import os
import json
from typing import List
import argparse
import re

WORKSPACE_PLACEHOLDER 	= "workspace"

class Workspace():
	workspace = os.getcwd()
	def __init__(self, WorkspaceFile: str):
		self.workspaceFilePth = WorkspaceFile
		self.placeholders = [WORKSPACE_PLACEHOLDER]
		#TODO: build list of configs that need replacing

		with open(WorkspaceFile, "r") as file:
			workspaceFile = json.load(file)
		# first add all elements as they are
		for key in workspaceFile:
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
					raise TypeError(f"Placeholder \"{placeholder}\" was requested which is a list but lists cannot be used as placeholders.")
		match = re.match(r"{\S+}", resolvedPath)
		if(match):
			raise TypeError(f"Placeholder \"{match.group(0)}\" was requested but did not find a replacement value for it.")

		return resolvedPath

	def require(self, requiredKeys: List[str]):
		for key in requiredKeys:
			try:
				getattr(self, key)
			except AttributeError:
				raise AttributeError(f"Workspace \"{self.workspaceFilePth}\" has no attribute \"{key}\" but it was listed as required.")

	@staticmethod
	def getReqiredArgparse(Argparser: argparse.ArgumentParser = None):
		if(Argparser is None):
			Argparser = argparse.ArgumentParser()
		Argparser.add_argument("WORKSPACE", help="Input workspace file path", type=str)
		return Argparser
