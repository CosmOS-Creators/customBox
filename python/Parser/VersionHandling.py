from __future__ import annotations
from typing import Dict, List, Union
import re
import Parser
import Parser.constants as const
import Parser.upgradeHandlers as upgradeHandlers

class Version:
	__versionParseRegex = re.compile(r"([0-9]+)\.([0-9]+)\.([0-9]+)")
	def __init__(self, version: Union[str, Version]) -> None:
		self.__major = None
		self.__minor = None
		self.__patch = None
		if(isinstance(version, Version)):
			self.__major = version.major
			self.__minor = version.minor
			self.__patch = version.patch
		elif(type(version) is str):
			result = self.__versionParseRegex.match(version)
			if(result):
				self.__major = result.group(1)
				self.__minor = result.group(2)
				self.__patch = result.group(3)

	@property
	def major(self):
		return self.__major

	@property
	def minor(self):
		return self.__minor

	@property
	def patch(self):
		return self.__patch

	def __force_version(self, version: Union[str, Version]) -> Version:
		if(isinstance(version, Version)):
			return version
		else:
			return Version(version)

	def matches(self, version: Union[str, Version]):
		compare_version = self.__force_version(version)
		if(compare_version.major == self.major and
			compare_version.minor == self.minor and
			compare_version.patch == self.patch):
			return True
		else:
			return False

	def __eq__(self, o: Version) -> bool:
		return self.matches(o)

	def __str__(self) -> str:
		return f'{self.major}.{self.minor}.{self.patch}'

	def __lt__(self, o: Version) -> bool:
		if(self.major < o.major):
			return True
		elif(self.major > o.major):
			return False
		elif(self.major == o.major):
			if(self.minor < o.minor):
				return True
			elif(self.minor > o.minor):
				return False
			elif(self.minor == o.minor):
				if(self.patch < o.patch):
					return True
				elif(self.patch > o.patch):
					return False
				elif(self.patch == o.patch):
					return False

	def __le__(self, o: Version) -> bool:
		if(self == o):
			return True
		else:
			return self < o

	def __gt__(self, o: Version) -> bool:
		if(self.major > o.major):
			return True
		elif(self.major < o.major):
			return False
		elif(self.major == o.major):
			if(self.minor > o.minor):
				return True
			elif(self.minor < o.minor):
				return False
			elif(self.minor == o.minor):
				if(self.patch > o.patch):
					return True
				elif(self.patch < o.patch):
					return False
				elif(self.patch == o.patch):
					return False

	def __ge__(self, o: Version) -> bool:
		if(self == o):
			return True
		else:
			return self > o

	def __hash__(self) -> int:
		return hash((self.major, self.minor, self.patch))


class CompatabilityManager:
	UPGRADE_LOOKUP = {
		# from version: to (version, with handler)
		Version("1.0.0"): (Version("1.1.0"), upgradeHandlers.upgrade_1_0_0_to_1_1_0)
	}

	@staticmethod
	def is_compatible(file_version: Version):
		return file_version == CompatabilityManager.get_current_version()

	@staticmethod
	def get_current_version():
		return Parser.FILE_FORMAT_VERSION

	# TODO: maybe write an algorithm that can find the shortest upgrade path if it ever becomes necessary
	@staticmethod
	def _find_upgrade_path(from_version: Version, to_version: Version, upgrade_path:List = []) -> List[upgradeHandlers.baseUpgradeHandler]:
		if(from_version in CompatabilityManager.UPGRADE_LOOKUP):
			upgraded_version, handler = CompatabilityManager.UPGRADE_LOOKUP[from_version]
			upgrade_path.append(handler(upgraded_version))
			if(upgraded_version == to_version):
				return upgrade_path
			else:
				CompatabilityManager._find_upgrade_path(upgraded_version, to_version, upgrade_path)
				return upgrade_path
		else:
			raise Exception(f'Could not find a upgrade path from version {from_version} to version {to_version}')

	@staticmethod
	def upgrade(input: Dict):
		current_file_version 	= Version(input[const.VERSION_KEY])
		if(current_file_version > CompatabilityManager.get_current_version()):
			raise Exception(f'The file format is from a newer parser version. Downgrading is not possible, please update your parser to at least version {str(current_file_version)} to open this file.')
		elif(current_file_version == CompatabilityManager.get_current_version()):
			return input
		upgrade_path 			= CompatabilityManager._find_upgrade_path(current_file_version, CompatabilityManager.get_current_version())
		upgraded_data 			= input
		for upgrade_handler in upgrade_path:
			upgraded_data = upgrade_handler.do_upgrade(upgraded_data)
		return upgraded_data
