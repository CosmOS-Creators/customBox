import pytest
import os
from Parser import Workspace, ConfigParser, ConfigTypes

class TestClassBasicFunctions:
	@pytest.fixture
	def parsed_config(self):
		workspace = Workspace("./Cosmos/customBox/python/Parser/tests/testConfigs/workspaces/BasicConfig.json")
		parser = ConfigParser(workspace)
		return parser.parse()

	def test_return_type(self, parsed_config):
		assert type(parsed_config) is ConfigTypes.Configuration

	def test_element_1_values(self, parsed_config: ConfigTypes.Configuration):
		subconfig = parsed_config.getSubconfig("basicTypes")
		configElement = subconfig.getElement("element_1")
		element_1_attribute_values = {
			"stringType": "testString",
			"boolType": True,
			"intType": 5,
			"floatType": 1.2,
			"stringListType": ["value_1", "value_2", "value_3"],
			"hexType": 15,
			"sliderType": 6,
			"selectionType": "selection_1"
			}
		for name, attribute in configElement.attributes.items():
			assert element_1_attribute_values[name] == attribute.value
