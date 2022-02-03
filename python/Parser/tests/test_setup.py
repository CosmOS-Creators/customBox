import pytest
from Parser import Environment, ConfigParser


@pytest.fixture
def test_environment():
    return Environment(
        "./Cosmos/customBox/python/Parser/tests/testConfigs/environments/BasicConfig.json"
    )


@pytest.fixture
def parsed_config():
    parser = ConfigParser(
        "./Cosmos/customBox/python/Parser/tests/testConfigs/configs/BasicConfig"
    )
    return parser.parse()


@pytest.fixture
def element_creation_config():
    parser = ConfigParser(
        "./Cosmos/customBox/python/Parser/tests/testConfigs/configs/elementCreationConfig"
    )
    return parser.parse()
