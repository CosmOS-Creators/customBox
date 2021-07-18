import pytest
from Parser import Link, ConfigTypes, AttributeTypes
from unittest.mock import patch

class TestClassLinkFunctions:

	@pytest.fixture
	def mocked_basic_cores_config_structure(self):
		attribLookup = {
				"cores/:bootOs": 	AttributeTypes.BoolType({"label": "Bool type", "type": "bool"}, "cores/:bootOs"),
				"cores/:coreName":	AttributeTypes.StringType({"label": "Core Name", "type": "string"}, "cores/:coreName")
		}
		configuration = ConfigTypes.Configuration()
		subconfig = configuration.createSubconfig("cores")
		configElement = subconfig.createElement("core_0")
		configElement.createAttributeInstance({"target": "bootOs", "value": True}, attribLookup)
		configElement.createAttributeInstance({"target": "coreName", "value": "CM4"}, attribLookup)
		return configuration

	@pytest.fixture
	def mocked_cores_program_config_structure(self, mocked_basic_cores_config_structure: ConfigTypes.Configuration):
		attribLookup = {
				"programs/:core": AttributeTypes.ParentReferenceType({"type": "parentReference"}, "programs/:core"),
				"programs/:name":	AttributeTypes.StringType({"label": "Program Name", "type": "string"}, "programs/:name")
		}
		subconfig = mocked_basic_cores_config_structure.createSubconfig("programs")
		configElement = subconfig.createElement("program_0")
		configElement.createAttributeInstance({"target": "name", "value": "default_CM4"},attribLookup)
		configElement.createAttributeInstance({"target": "core", "value": "cores/core_0"},attribLookup)
		return mocked_basic_cores_config_structure

	def test_parentReferenceLink_method(self, mocked_cores_program_config_structure: ConfigTypes.Configuration):
		cores = mocked_cores_program_config_structure.getSubconfig("cores")
		programs = mocked_cores_program_config_structure.getSubconfig("programs")
		core_0 = cores.getElement("core_0")
		coreName = core_0.getAttributeInstance("coreName")
		bootOs = core_0.getAttributeInstance("bootOs")
		program_0 = programs.getElement("program_0")
		core = program_0.getAttributeInstance("core")
		name = program_0.getAttributeInstance("name")
		assert core_0.attributes == {"coreName": coreName, "bootOs": bootOs}
		assert program_0.attributes == {"name": name, "core": core}
		assert core.value == "cores/core_0"
		core.ResolveValueLink()
		assert core.value == core_0
		assert program_0.attributes == {"name": name, "core": core}
		core_0_attributes = core_0.attributes

		assert core_0_attributes["coreName"] == coreName
		assert core_0_attributes["bootOs"] == bootOs
		core_0_attributes_list = list(core_0_attributes.keys())
		expected_items = ["coreName", "bootOs", "programs"]
		for item in expected_items:
			assert item in core_0_attributes_list
		assert len(expected_items) == len(core_0_attributes_list)
		parent_linked_programs = core_0.getReferenceObject("programs")
		assert parent_linked_programs.references == {"program_0": program_0}
