from __future__ import annotations
from typing import Dict
import Parser.constants as const
import Parser.VersionHandling as vh
import Parser.helpers as helpers

class baseUpgradeHandler:
	def __init__(self, new_version: vh.Version) -> None:
		self.new_version = new_version

	def do_upgrade(self, data: Dict) -> Dict:
		data[const.VERSION_KEY] = str(self.new_version)
		return data

class upgrade_1_0_0_to_1_1_0(baseUpgradeHandler):
	pass
