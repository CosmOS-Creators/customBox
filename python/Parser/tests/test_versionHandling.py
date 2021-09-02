from typing import Dict
import pytest
import Parser.upgradeHandlers as upgradeHandlers
from Parser.VersionHandling import CompatabilityManager, Version
import Parser.constants as const
import unittest.mock as mock

class TestCompatabilityManager:

	@pytest.fixture
	def upgrade_lookup_test(self):
		class upgradeH1(upgradeHandlers.baseUpgradeHandler):
			def do_upgrade(self, data) -> Dict:
				new_data = super().do_upgrade(data)
				new_data["H1"] = True
				return new_data
		class upgradeH2(upgradeHandlers.baseUpgradeHandler):
			def do_upgrade(self, data) -> Dict:
				new_data = super().do_upgrade(data)
				new_data["H2"] = True
				return new_data
		return {
			Version("1.0.0"): (Version("1.1.0"), upgradeH1),
			Version("1.1.0"): (Version("2.0.0"), upgradeH2)
		}

	@mock.patch.object(CompatabilityManager, 'get_current_version', return_value = Version("1.1.0"))
	def test_direct_upgrade_path(self, get_current_version, upgrade_lookup_test: Dict):
		CompatabilityManager.UPGRADE_LOOKUP = upgrade_lookup_test
		test_data = {const.VERSION_KEY: "1.0.0"}
		upgraded_data = CompatabilityManager.upgrade(test_data)
		assert "H1" in upgraded_data and "H2" not in upgraded_data

	@mock.patch.object(CompatabilityManager, 'get_current_version', return_value = Version("2.0.0"))
	def test_indirect_upgrade_path(self, get_current_version, upgrade_lookup_test: Dict):
		CompatabilityManager.UPGRADE_LOOKUP = upgrade_lookup_test
		test_data = {const.VERSION_KEY: "1.0.0"}
		upgraded_data = CompatabilityManager.upgrade(test_data)
		assert "H1" in upgraded_data and "H2" in upgraded_data
