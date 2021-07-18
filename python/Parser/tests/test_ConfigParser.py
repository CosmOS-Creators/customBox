import pytest
from Parser import Workspace, ConfigParser, ConfigTypes

class TestClassBasicFunctions:
	@pytest.fixture
	def parsed_config(self):
		workspace = Workspace("./Cosmos/customBox/python/Parser/tests/testConfigs/workspaces/BasicConfig.json")
		parser = ConfigParser(workspace)
		return parser.parse()

	def test_return_type(self, parsed_config):
		assert type(parsed_config) is ConfigTypes.Configuration

	def test_basicTypes_element_1_values(self, parsed_config: ConfigTypes.Configuration):
		referenceTypes_subconfig		= parsed_config.getSubconfig("referenceTypes")
		basicTypes_subconfig			= parsed_config.getSubconfig("basicTypes")
		configElement 					= basicTypes_subconfig.getElement("element_1")
		reference_test_0_configElement	= referenceTypes_subconfig.getElement("reference_test_0")
		element_1_attribute_values = {
			"stringType": "testString",
			"boolType": True,
			"intType": 5,
			"floatType": 1.2,
			"stringListType": ["value_1", "value_2", "value_3"],
			"hexType": 15,
			"sliderType": 6,
			"selectionType": "selection_1",
			"referenceTypes": [reference_test_0_configElement]
			}
		for name, attribute in configElement.attributes.items():
			if(type(attribute) is ConfigTypes.AttributeInstance):
				assert element_1_attribute_values[name] == attribute.value
			elif(type(attribute) is ConfigTypes.ReferenceCollection):
				assert element_1_attribute_values[name] == list(attribute.references.values())

	def test_basicTypes_element_2_values(self, parsed_config: ConfigTypes.Configuration):
		subconfig = parsed_config.getSubconfig("basicTypes")
		configElement = subconfig.getElement("element_2")
		element_1_attribute_values = {
			"stringType": "StringTest",
			"boolType": False,
			"intType": 200,
			"floatType": 5.5,
			"stringListType": ["value_0"],
			"hexType": 240,
			"sliderType": 10,
			"selectionType": "selection_2"
			}
		for name, attribute in configElement.attributes.items():
			assert element_1_attribute_values[name] == attribute.value

	def test_referenceTypes_test_0_values(self, parsed_config: ConfigTypes.Configuration):
		referenceTypes_subconfig		= parsed_config.getSubconfig("referenceTypes")
		basicTypes_subconfig			= parsed_config.getSubconfig("basicTypes")
		reference_test_0_configElement	= referenceTypes_subconfig.getElement("reference_test_0")
		element_1_configElement 		= basicTypes_subconfig.getElement("element_1")
		element_2_configElement 		= basicTypes_subconfig.getElement("element_2")

		element_1_attribute_values = {
			"referenceListType": [element_1_configElement, element_2_configElement],
			"parentReferenceType": element_1_configElement,
			"selectionLinkType": element_2_configElement,
			"InheritedSelectionType": "selection_1"
			}
		for name, attribute in reference_test_0_configElement.attributes.items():
			assert element_1_attribute_values[name] == attribute.value
