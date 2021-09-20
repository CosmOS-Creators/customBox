from pathlib import Path
import pytest
from Parser import Workspace, ConfigParser, ConfigTypes, constants
from Parser.tests.test_setup import test_workspace, parsed_config
import json
import hashlib

class TestClassBasicFunctions:

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

class TestCreatingElementCreationAndDeletion:

	def test_new_element_creation(self, parsed_config: ConfigTypes.Configuration):
		subconfig = parsed_config.getSubconfig("basicTypes")
		assert len(subconfig.elements) == 2
		assert "element_1" in subconfig.elements and "element_2" in subconfig.elements
		newElement = subconfig.createElement("element_3")
		assert len(newElement.attributes) == 0
		assert len(subconfig.elements) == 3
		assert "element_1" in subconfig.elements and "element_2" in subconfig.elements and "element_3" in subconfig.elements
		newAttribInst = newElement.createAttributeInstance("stringType", "test")
		assert len(newElement.attributes) == 1
		with pytest.raises(AttributeError):
			newElement.createAttributeInstance("stringType", "test")
		with pytest.raises(ValueError):
			newElement.createAttributeInstance("stringType", attributeName="test1")

	def test_element_deletion(self, parsed_config: ConfigTypes.Configuration):
		referenceTypes = parsed_config.getSubconfig("referenceTypes")
		basicTypes = parsed_config.getSubconfig("basicTypes")
		ref_test_0 = referenceTypes.getElement("reference_test_0")
		element_1 = basicTypes.getElement("element_1")
		assert element_1 in ref_test_0.getAttribute("referenceListType").value
		assert element_1 == ref_test_0.getAttribute("parentReferenceType").value
		element_1.delete()
		assert element_1 not in ref_test_0.getAttribute("referenceListType").value
		assert ref_test_0.getAttribute("parentReferenceType").value is None


class TestChecksumFunctionality:
	@pytest.fixture
	def config_file(self, test_workspace):
		workspace = Workspace("./Cosmos/customBox/python/Parser/tests/testConfigs/workspaces/BasicConfig.json")
		configFolders = workspace.requireFolder("config")
		for configFolder in configFolders:
			basicTypesConfig = configFolder.joinpath("basicTypes.json")
			if(basicTypesConfig.exists()):
				return basicTypesConfig
		return None

	def test_checksum(self, parsed_config: ConfigTypes.Configuration, config_file: Path):
		subconfig = parsed_config.getSubconfig("basicTypes")
		assert subconfig.needs_serialization() == False
		newElement = subconfig.createElement("element_3")
		assert subconfig.needs_serialization() == True
