import pytest
from Parser import Workspace, ConfigParser

@pytest.fixture
def test_workspace():
	return Workspace("./Cosmos/customBox/python/Parser/tests/testConfigs/workspaces/BasicConfig.json")

@pytest.fixture
def parsed_config():
	parser = ConfigParser("./Cosmos/customBox/python/Parser/tests/testConfigs/configs/BasicConfig")
	return parser.parse()
