from typing import Dict
import pytest
import Parser.upgradeHandlers as upgradeHandlers
from Parser.VersionHandling import CompatabilityManager, Version
import Parser.constants as const

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
		CompatabilityManager.UPGRADE_LOOKUP = {
			Version("1.0.0"): (Version("1.1.0"), upgradeH1),
			Version("1.1.0"): (Version("2.0.0"), upgradeH2)
		}
		return CompatabilityManager

	def test_direct_upgrade_path(self, upgrade_lookup_test: CompatabilityManager):
		def version_1_1_0():
			return Version("1.1.0")
		upgrade_lookup_test.get_current_version = version_1_1_0
		test_data = {const.VERSION_KEY: "1.0.0"}
		upgraded_data = upgrade_lookup_test.upgrade(test_data)
		assert "H1" in upgraded_data and "H2" not in upgraded_data

	def test_indirect_upgrade_path(self, upgrade_lookup_test: CompatabilityManager):
		def version_2_0_0():
			return Version("2.0.0")
		upgrade_lookup_test.get_current_version = version_2_0_0
		test_data = {const.VERSION_KEY: "1.0.0"}
		upgraded_data = upgrade_lookup_test.upgrade(test_data)
		assert "H1" in upgraded_data and "H2" in upgraded_data
