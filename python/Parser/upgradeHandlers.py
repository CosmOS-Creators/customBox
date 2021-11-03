from __future__ import annotations
import hashlib
from typing import Dict
import Parser.constants as const
import Parser.VersionHandling as vh
import json


class baseUpgradeHandler:
    def __init__(self, new_version: vh.Version) -> None:
        self.new_version = new_version

    def do_upgrade(self, data: Dict) -> Dict:
        data[const.VERSION_KEY] = str(self.new_version)
        return data


class upgrade_1_0_0_to_1_1_0(baseUpgradeHandler):
    def do_upgrade(self, data: Dict) -> Dict:
        super().do_upgrade(data)
        elements_str = json.dumps(data[const.ELEMENTS_KEY]).encode("utf-8")
        elements_hash = str(hashlib.md5(elements_str).hexdigest())
        data[const.CHECKSUM_KEY] = elements_hash
        return data
