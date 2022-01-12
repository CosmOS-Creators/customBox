import pytest
from Parser import Link, ConfigTypes, AttributeTypes
from unittest.mock import patch

from Parser.ParserExceptions import ValidationError


class TestClassLinkFunctions:
    @pytest.fixture
    def mocked_basic_cores_config_structure(self):
        from pathlib import Path

        attribLookup = {
            "cores/:bootOs": AttributeTypes.BoolType(
                {"label": "Bool type", "type": "bool"}, "cores/:bootOs"
            ),
            "cores/:coreName": AttributeTypes.StringType(
                {"label": "Core Name", "type": "string"}, "cores/:coreName"
            ),
            "programs/:core": AttributeTypes.ParentReferenceType(
                {"type": "parentReference"}, "programs/:core"
            ),
            "programs/:name": AttributeTypes.StringType(
                {"label": "Program Name", "type": "string"}, "programs/:name"
            ),
        }
        configuration = ConfigTypes.Configuration(attribLookup)
        subconfig = configuration.createSubconfig("cores", Path("test.json"))
        configElement = subconfig.createElement("core_0")
        configElement.createAttributeInstanceFromDefinition(
            {"target": "bootOs", "value": True}
        )
        configElement.createAttributeInstanceFromDefinition(
            {"target": "coreName", "value": "CM4"}
        )
        return configuration

    @pytest.fixture
    def mocked_cores_program_config_structure(
        self, mocked_basic_cores_config_structure: ConfigTypes.Configuration
    ):
        from pathlib import Path

        subconfig = mocked_basic_cores_config_structure.createSubconfig(
            "programs", Path("test.json")
        )
        configElement = subconfig.createElement("program_0")
        configElement.createAttributeInstanceFromDefinition(
            {"target": "name", "value": "default_CM4"}
        )
        configElement.createAttributeInstanceFromDefinition(
            {"target": "core", "value": "cores/core_0"}
        )
        configElement = subconfig.createElement("program_1")
        configElement.createAttributeInstanceFromDefinition(
            {"target": "name", "value": "blinking_led_CM4"}
        )
        configElement.createAttributeInstanceFromDefinition(
            {"target": "core", "value": "cores/core_0"}
        )
        return mocked_basic_cores_config_structure

    def test_defaultValue_methods(self):
        defaults = [
            (
                "",
                AttributeTypes.StringType(
                    {"type": "string", "label": "test"}, "cores/:name1"
                ),
            ),
            (
                False,
                AttributeTypes.BoolType(
                    {"type": "bool", "label": "test"}, "cores/:name2"
                ),
            ),
            (
                0,
                AttributeTypes.IntType(
                    {"type": "int", "label": "test"}, "cores/:name3"
                ),
            ),
            (
                0,
                AttributeTypes.FloatType(
                    {"type": "float", "label": "test"}, "cores/:name4"
                ),
            ),
            (
                [],
                AttributeTypes.ReferenceListType(
                    {"type": "referenceList", "label": "test"}, "cores/:name5"
                ),
            ),
            (
                [],
                AttributeTypes.StringListType(
                    {"type": "stringList", "label": "test"}, "cores/:name6"
                ),
            ),
            (
                None,
                AttributeTypes.SelectionType(
                    {"type": "selection", "label": "test", "elements": []},
                    "cores/:name10",
                ),
            ),
            (
                0,
                AttributeTypes.HexType(
                    {"type": "hex", "label": "test"}, "cores/:name7"
                ),
            ),
            (
                0,
                AttributeTypes.SliderType(
                    {"type": "slider", "label": "test"}, "cores/:name8"
                ),
            ),
            (
                None,
                AttributeTypes.ParentReferenceType(
                    {"type": "parentReference", "label": "test"}, "cores/:name9"
                ),
            ),
        ]
        for value, attribType in defaults:
            assert attribType.getDefault() == value

    def test_parseAttribute_function(self):
        with pytest.raises(KeyError):  # no type key
            AttributeTypes.parseAttribute({}, "")
        with pytest.raises(ValueError):  # invalid link
            AttributeTypes.parseAttribute({"type": "parentReference"}, "")
        with pytest.raises(ValueError):  # invalid link
            AttributeTypes.parseAttribute({"type": "parentReference"}, "cores")
        with pytest.raises(ValueError):  # invalid link
            AttributeTypes.parseAttribute({"type": "parentReference"}, "cores/core_0")
        with pytest.raises(ValueError):  # invalid link
            AttributeTypes.parseAttribute({"type": "parentReference"}, "/:name")
        with pytest.raises(KeyError):  # invalid type
            AttributeTypes.parseAttribute({"type": "invalidType"}, "cores/:name")
        resultingTypes = {
            "string": AttributeTypes.StringType,
            "bool": AttributeTypes.BoolType,
            "int": AttributeTypes.IntType,
            "float": AttributeTypes.FloatType,
            "referenceList": AttributeTypes.ReferenceListType,
            "stringList": AttributeTypes.StringListType,
            "hex": AttributeTypes.HexType,
            "slider": AttributeTypes.SliderType,
            "parentReference": AttributeTypes.ParentReferenceType,
        }
        for typeStr, classType in resultingTypes.items():
            assert (
                type(
                    AttributeTypes.parseAttribute(
                        {"type": typeStr, "label": "test"}, "cores/:name"
                    )
                )
                is classType
            )
        # selection needs some special keys
        assert (
            type(
                AttributeTypes.parseAttribute(
                    {"type": "selection", "label": "test", "elements": []},
                    "cores/:name",
                )
            )
            is AttributeTypes.SelectionType
        )

    def test_attributeTypes_baseClass(
        self, mocked_basic_cores_config_structure: ConfigTypes.Configuration
    ):
        with pytest.raises(TypeError):  # base class should not be instantiated
            AttributeTypes.AttributeType({}, "")

        class test(AttributeTypes.AttributeType):
            pass

        with pytest.raises(AttributeError):
            test({}, "cores/:name")
        missconfiguredType = test({"type": "test", "label": "test"}, "cores/:name")
        with pytest.raises(NotImplementedError):
            missconfiguredType.getDefault()
        assert missconfiguredType.checkValue(0) == 0
        subc = mocked_basic_cores_config_structure.getSubconfig("cores")
        element = subc.getElement("core_0")
        attribInst = element.getAttributeInstance("coreName")
        with pytest.raises(NotImplementedError):  # link method from the base class should not be called as it is not implemented
            missconfiguredType.link(
                mocked_basic_cores_config_structure, attribInst
            )

    def test_parentReference_Link_method(
        self, mocked_cores_program_config_structure: ConfigTypes.Configuration
    ):
        cores = mocked_cores_program_config_structure.getSubconfig("cores")
        programs = mocked_cores_program_config_structure.getSubconfig("programs")
        core_0 = cores.getElement("core_0")
        coreName = core_0.getAttributeInstance("coreName")
        bootOs = core_0.getAttributeInstance("bootOs")
        program_0 = programs.getElement("program_0")
        program_0_core = program_0.getAttributeInstance("core")
        program_0_name = program_0.getAttributeInstance("name")
        program_1 = programs.getElement("program_1")
        program_1_core = program_1.getAttributeInstance("core")
        program_1_name = program_1.getAttributeInstance("name")
        assert core_0.attributes == {"coreName": coreName, "bootOs": bootOs}
        assert program_0.attributes == {"name": program_0_name, "core": program_0_core}
        assert program_0_core.value == "cores/core_0"
        program_0_core.ResolveValueLink()
        assert program_0_core.value == core_0
        assert program_0.attributes == {"name": program_0_name, "core": program_0_core}
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

        assert program_1.attributes == {"name": program_1_name, "core": program_1_core}
        assert program_1_core.value == "cores/core_0"
        program_1_core.ResolveValueLink()
        assert program_1_core.value == core_0
        assert program_1.attributes == {"name": program_1_name, "core": program_1_core}
        core_0_attributes = core_0.attributes
        assert core_0_attributes["coreName"] == coreName
        assert core_0_attributes["bootOs"] == bootOs
        core_0_attributes_list = list(core_0_attributes.keys())
        expected_items = ["coreName", "bootOs", "programs"]
        for item in expected_items:
            assert item in core_0_attributes_list
        assert len(expected_items) == len(core_0_attributes_list)
        parent_linked_programs = core_0.getReferenceObject("programs")
        assert parent_linked_programs.references == {
            "program_0": program_0,
            "program_1": program_1,
        }

    def test_parentReference_init_method(self):
        parentReference = AttributeTypes.ParentReferenceType(
            {"type": "parentReference", "label": "test", "tooltip": "test info"},
            "programs/:core",
        )
        assert parentReference.globalID == "programs/:core"
        assert parentReference.needsLinking == True
        with pytest.raises(KeyError):
            AttributeTypes.ParentReferenceType(
                {"type": "parentReference", "hidden": True}, "programs/:core"
            )
        with pytest.raises(KeyError):
            AttributeTypes.ParentReferenceType(
                {"type": "parentReference", "placeholder": True}, "programs/:core"
            )
        with pytest.raises(KeyError):
            AttributeTypes.ParentReferenceType(
                {"type": "parentReference", "min": 0}, "programs/:core"
            )
        with pytest.raises(KeyError):
            AttributeTypes.ParentReferenceType(
                {"type": "parentReference", "max": 0}, "programs/:core"
            )
        with pytest.raises(KeyError):
            AttributeTypes.ParentReferenceType(
                {"type": "parentReference", "step": 5}, "programs/:core"
            )

    def test_parentReference_checkValue_method(self):
        parentReference = AttributeTypes.ParentReferenceType(
            {"type": "parentReference"}, "programs/:core"
        )
        with pytest.raises(ValidationError):
            parentReference.checkValue("programs")
        with pytest.raises(ValidationError):
            parentReference.checkValue("programs/:name")
        with pytest.raises(ValidationError):
            parentReference.checkValue("")
        assert parentReference.checkValue("programs/program_0") == "programs/program_0"
        link = Link("programs/program_0")
        assert parentReference.checkValue(link) == link
        with pytest.raises(ValidationError):
            parentReference.checkValue(Link("programs"))
        with pytest.raises(ValidationError):
            parentReference.checkValue(0)
