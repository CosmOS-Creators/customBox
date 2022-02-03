import os
import json
import argparse
import re
import Parser.helpers as helpers
import Parser.constants as const
from pathlib import Path
from typing import List, Union


class Environment:
    environment = os.getcwd()

    def __init__(self, environment_file: str, environment_path: str = None):
        if environment_path is not None:
            self.environment = environment_path
        self.environmentFilePath = environment_file
        self.placeholders = [const.ENVIRONMENT_PLACEHOLDER]

        with open(environment_file, "r") as file:
            environmentFile = json.load(file)
        # first add all elements as they are
        for key in environmentFile:
            if key in self.__dict__ or key in self.placeholders:
                raise KeyError(
                    f'Environment file contained the key "{key}" which is reserved and not permitted to be used'
                )
            if type(environmentFile[key]) is list:
                resolvedPathsList = []
                for path in environmentFile[key]:
                    resolvedPathsList.append(path)
                setattr(self, key, resolvedPathsList)
            elif type(environmentFile[key]) is str:
                setattr(self, key, environmentFile[key])
            else:
                raise TypeError(
                    f'Format of the Environment file "{environment_file}" is invalid. The only supported items are list and str but found {type(environmentFile[key])}.'
                )
            self.placeholders.append(key)
        # then do placeholder replacement
        for key in environmentFile:
            property = getattr(self, key)
            if type(property) is list:
                for i, path in enumerate(property):
                    try:
                        property[i] = self.resolvePath(path)
                    except TypeError as e:
                        raise TypeError(
                            f'Error while replacing placeholders in "{key}" config: {str(e)}'
                        ) from e
            elif type(property) is str:
                try:
                    setattr(self, key, self.resolvePath(property))
                except TypeError as e:
                    raise TypeError(
                        f'Error while replacing placeholders in "{key}" config: {str(e)}'
                    ) from e
            else:
                raise TypeError(
                    f'Format of the Environment file "{environment_file}" is invalid. The only supported items are list and str but found {type(property)}.'
                )
            self.placeholders.append(key)

    def resolvePath(self, path: str):
        resolvedPath = path
        for placeholder in self.placeholders:
            placeholderStr = f"{{{placeholder}}}"
            if placeholderStr in path:
                replacementValue = getattr(self, placeholder)
                if type(replacementValue) is str:
                    resolvedPath = resolvedPath.replace(
                        placeholderStr, replacementValue
                    )
                else:
                    raise TypeError(
                        f'Placeholder "{placeholder}" was requested which is of type {type(replacementValue)} but only strings can be used as placeholders.'
                    )
        match = re.match(r"{\S+}", resolvedPath)
        if match:
            raise TypeError(
                f'Placeholder "{match.group(0)}" was requested but did not find a replacement value for it.'
            )

        return resolvedPath

    def requireFolder(
        self, requiredKeys: Union[List[str], str], createMissingDirs: bool = False
    ):
        """Check that a config path with a certain name exists
        @createMissingDirs 	If true will create missing dirs instead of throwing an exception.
                                                If false will check that the path exists and is an actual directory. If not an exception will be raised.
        """
        requiredKeys = helpers.forceStrList(requiredKeys)
        requiredFolders: List[Path] = list()
        for key in requiredKeys:
            try:
                folderPaths = getattr(self, key)
            except AttributeError:
                raise AttributeError(
                    f'Environment "{self.environmentFilePath}" has no attribute "{key}" but it was listed as required.'
                )
            if type(folderPaths) is str:
                folderPaths = [folderPaths]
            for path in folderPaths:
                path = Path(path)
                if path.exists():
                    if not path.is_dir():
                        raise IOError(
                            f'The path "{path}" for the config "{key}" does not point to a directory'
                        )
                    else:
                        requiredFolders.append(path)
                elif createMissingDirs:
                    path.mkdir(parents=True)
                    requiredFolders.append(path)
                else:
                    raise IOError(
                        f'The path "{path}" for the config "{key}" does not exist'
                    )
        return requiredFolders

    def requireFile(
        self, requiredKeys: Union[List[str], str], createMissingDirs: bool = False
    ):
        """Check that a config path with a certain name exists
        @createMissingDirs 	If true will create missing dirs instead of throwing an exception. This will not create a file, only the directory paths.
                                                If false will check that the path exists and is an actual existing file. If not an exception will be raised.
        """
        requiredKeys = helpers.forceStrList(requiredKeys)
        requiredFiles: List[Path] = list()
        for key in requiredKeys:
            try:
                filePaths = getattr(self, key)
            except AttributeError:
                raise AttributeError(
                    f'Environment "{self.environmentFilePath}" has no attribute "{key}" but it was listed as required.'
                )
            if type(filePaths) is str:
                filePaths = [filePaths]
            for path in filePaths:
                path = Path(path)
                if path.exists():
                    if not path.is_file():
                        raise IOError(
                            f'The path "{str(path)}" for the config "{key}" does not point to a file'
                        )
                    else:
                        requiredFiles.append(path)
                elif createMissingDirs:
                    path.parent.mkdir(parents=True)
                    requiredFiles.append(path)
                else:
                    raise IOError(
                        f'The path "{path}" for the config "{key}" does not exist'
                    )
        return requiredFiles

    def require(self, requiredKeys: Union[List[str], str]):
        """Check that a key exists in the environment file"""
        requiredKeys = helpers.forceStrList(requiredKeys)
        for key in requiredKeys:
            try:
                getattr(self, key)
            except AttributeError:
                raise AttributeError(
                    f'Environment "{self.environmentFilePath}" has no attribute "{key}" but it was listed as required.'
                )

    @staticmethod
    def getReqiredArgparse(Argparser: argparse.ArgumentParser = None):
        if Argparser is None:
            Argparser = argparse.ArgumentParser()
        Argparser.add_argument(
            "ENVIRONMENT_CONFIG",
            help="File path to the environment config JSON file",
            type=str,
        )
        Argparser.add_argument(
            "-w",
            "--environment-root",
            dest="environment_root",
            required=False,
            default=None,
            help="Directory to the environment root path, if not given cwd will be used for this",
            type=str,
        )
        return Argparser
