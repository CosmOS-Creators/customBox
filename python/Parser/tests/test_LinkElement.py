import pytest
from Parser import Link, ConfigTypes, AttributeTypes
from unittest.mock import patch


class TestClassLinkFunctions:

	@pytest.fixture
	def mocked_basic_config_structure(self):
		from pathlib import Path
		boolType = AttributeTypes.BoolType({"label": "Bool type", "type": "bool"}, "config/:attribute")
		attribLookup = dict()
		attribLookup["config/:attribute"] = boolType
		configuration = ConfigTypes.Configuration()
		subconfig = configuration.createSubconfig("config", Path("test.json"))
		configElement = subconfig.createElement("element")
		configElement.createAttributeInstance({"target": "attribute", "value": True}, attribLookup)
		return configuration

	def test_constructor(self):
		link = Link()
		with pytest.raises(ValueError):
			link.element
		with pytest.raises(ValueError):
			link.config
		with pytest.raises(ValueError):
			link.attribute
		with patch.object(Link, 'split', return_value=("mockedConfig","MockedElement","MockedAttribute")) as mocked_split_method:
			mockedLink = Link("config/element:attribute")
			assert mockedLink.config == "mockedConfig"
			assert mockedLink.element == "MockedElement"
			assert mockedLink.attribute == "MockedAttribute"
		mocked_split_method.assert_called_once_with("config/element:attribute", Link.EMPHASIZE_ELEMENT)
		with patch.object(Link, 'split', return_value=("mockedConfig",None,None)) as mocked_split_method:
			mockedLink = Link("config", Link.EMPHASIZE_CONFIG)
			assert mockedLink.config == "mockedConfig"
			with pytest.raises(ValueError):
				mockedLink.element
			with pytest.raises(ValueError):
				mockedLink.attribute
		mocked_split_method.assert_called_once_with("config", Link.EMPHASIZE_CONFIG)
		link.attribute = "test"
		link.element = "testElement"
		link1 = Link(link)
		link.attribute = "test1"
		link.element = "testElement1"
		assert link1.attribute == "test"
		assert link1.element == "testElement"
		assert link1.hasConfig() == False
		with pytest.raises(TypeError):
			test = Link(1)

	def test_split_method(self):
		config, element, attribute = Link.split(None)
		assert config is None
		assert element is None
		assert attribute is None
		config, element, attribute = Link.split("")
		assert config is None
		assert element is None
		assert attribute is None
		config, element, attribute = Link.split("element")
		assert config is None
		assert element == "element"
		assert attribute is None
		config, element, attribute = Link.split("/element")
		assert config is None
		assert element == "element"
		assert attribute is None
		config, element, attribute = Link.split("/element", Link.EMPHASIZE_CONFIG)
		assert config is None
		assert element == "element"
		assert attribute is None
		config, element, attribute = Link.split("config/")
		assert config == "config"
		assert element is None
		assert attribute is None
		config, element, attribute = Link.split("config/element")
		assert config == "config"
		assert element == "element"
		assert attribute is None
		config, element, attribute = Link.split("config/element:attribute")
		assert config == "config"
		assert element == "element"
		assert attribute == "attribute"
		config, element, attribute = Link.split("config/:attribute")
		assert config == "config"
		assert element is None
		assert attribute == "attribute"
		config, element, attribute = Link.split("element:attribute")
		assert config is None
		assert element == "element"
		assert attribute == "attribute"
		config, element, attribute = Link.split("element", Link.EMPHASIZE_ELEMENT)
		assert config is None
		assert element == "element"
		assert attribute is None
		config, element, attribute = Link.split("config", Link.EMPHASIZE_CONFIG)
		assert config == "config"
		assert element is None
		assert attribute is None
		config, element, attribute = Link.split("attribute", Link.EMPHASIZE_ATTRIBUTE)
		assert config is None
		assert element is None
		assert attribute == "attribute"
		with pytest.raises(ValueError):
			config, element, attribute = Link.split("attribute", 5)
		with pytest.raises(ValueError):
			config, element, attribute = Link.split("config/element/attribute")
		with pytest.raises(ValueError):
			config, element, attribute = Link.split("config:element:attribute")
		with pytest.raises(TypeError):
			config, element, attribute = Link.split(100)

	def test_operators(self):
		link1 = Link("config/element:attribute")
		link2 = Link("config/element1:attribute")
		link3 = Link()
		link3.attribute = "attribute"
		link3.element	= "element1"
		link3.config	= "config"
		link4 = Link("config/element")
		assert repr(link1) == "Link(config/element:attribute)"
		assert str(link2) == "config/element1:attribute"
		assert link1 == "config/element:attribute"
		assert link1 != link2
		assert link1 != link3
		assert link2 == link3
		assert link4 != link1
		link1.attribute = None
		assert link4 == link1
		test = dict()
		test[link1] = "value"
		test[link2] = "value1"
		assert test[link1] == "value"
		assert test[link2] == "value1"
		assert test[link4] == "value"
		assert test[link3] == "value1"

	def test_link_hasAnyParts_method(self):
		def runTests(input, expections):
			tests = [
				input.hasAnyParts(),
				input.hasAnyParts(config=True),
				input.hasAnyParts(element=True),
				input.hasAnyParts(attribute=True),
				input.hasAnyParts(config=True, element=True),
				input.hasAnyParts(config=True, attribute=True),
				input.hasAnyParts(config=True, element=True, attribute=True)
			]
			for i, test in enumerate(tests):
				assert test == expections[i]
		link = Link()
		expectations = [
			True,
			False,
			False,
			False,
			False,
			False,
			False
		]
		runTests(link, expectations)
		link.config = "config"
		expectations[1] = True
		runTests(link, expectations)
		link.element = "element"
		expectations[2] = True
		expectations[4] = True
		runTests(link, expectations)
		link.attribute = "attribute"
		expectations[3] = True
		expectations[5] = True
		expectations[6] = True
		runTests(link, expectations)

	def test_link_has_methods(self):
		link = Link()
		assert link.hasConfig() == False
		assert link.hasElement() == False
		assert link.hasAttribute() == False
		link.config = "config"
		assert link.hasConfig() == True
		assert link.hasElement() == False
		assert link.hasAttribute() == False
		link.element = "element"
		assert link.hasConfig() == True
		assert link.hasElement() == True
		assert link.hasAttribute() == False
		link.attribute = "attribute"
		assert link.hasConfig() == True
		assert link.hasElement() == True
		assert link.hasAttribute() == True

	def test_construct_method(self):
		link = Link.construct()
		assert link.hasAttribute() == False
		assert link.hasElement() == False
		assert link.hasConfig() == False
		link = Link.construct(config="config")
		assert link.hasAttribute() == False
		assert link.hasElement() == False
		assert link.config == "config"
		link = Link.construct(element="element")
		assert link.hasAttribute() == False
		assert link.element == "element"
		assert link.hasConfig() == False
		link = Link.construct(attribute="attribute")
		assert link.attribute == "attribute"
		assert link.hasElement() == False
		assert link.hasConfig() == False
		link = Link.construct(config="config", attribute="attribute")
		assert link.attribute == "attribute"
		assert link.hasElement() == False
		assert link.config == "config"
		link = Link.construct(config="config", element="element", attribute="attribute")
		assert link.attribute == "attribute"
		assert link.element == "element"
		assert link.config == "config"

	def test_setters(self):
		link = Link()
		link.config = "config"
		with pytest.raises(ValueError):
			link.config = "config/"
		with pytest.raises(ValueError):
			link.config = "config:"
		assert link.config == "config"
		link.element = "element"
		with pytest.raises(ValueError):
			link.element = "element/"
		with pytest.raises(ValueError):
			link.element = "element:"
		assert link.element == "element"
		link.attribute = "attribute"
		with pytest.raises(ValueError):
			link.attribute = "attribute/"
		with pytest.raises(ValueError):
			link.attribute = "attribute:"
		assert link.attribute == "attribute"
		link.config = None
		with pytest.raises(ValueError):
			link.config
		link.element = None
		with pytest.raises(ValueError):
			link.element
		link.attribute = None
		with pytest.raises(ValueError):
			link.attribute

	def test_copy(self):
		link = Link("config/element:attribute")
		link1 = link.copy()
		assert link1.config == "config"
		assert link1.element == "element"
		assert link1.attribute == "attribute"
		link1.config = "1"
		link1.element = "2"
		link1.attribute = "3"
		assert link1.config == "1"
		assert link1.element == "2"
		assert link1.attribute == "3"
		assert link.config == "config"
		assert link.element == "element"
		assert link.attribute == "attribute"

	def test_isGlobal_methods(self):
		link = Link("config/element:attribute")
		assert link.isGlobal() == True
		link = Link("config/element")
		assert link.isGlobal() == True
		link = Link("config")
		assert link.isGlobal() == False
		link = Link("element:attribute")
		assert link.isGlobal() == False
		link = Link("config/:attribute")
		assert link.isGlobal() == True

		assert Link.isGlobal("config/element:attribute") == True
		assert Link.isGlobal("config/element") == True
		assert Link.isGlobal("config") == False
		assert Link.isGlobal("element:attribute") == False
		assert Link.isGlobal("config/:attribute") == True

	def test_force_method(self, mocked_basic_config_structure: ConfigTypes.Configuration):
		link = Link.force(None)
		config, element, attribute = link.parts
		assert type(link) is Link
		assert config is None
		assert element is None
		assert attribute is None
		link = Link.force("")
		config, element, attribute = link.parts
		assert type(link) is Link
		assert config is None
		assert element is None
		assert attribute is None
		link = Link.force("config/element")
		config, element, attribute = link.parts
		assert type(link) is Link
		assert config == "config"
		assert element == "element"
		assert attribute is None
		link1 = Link.force(link)
		assert link1 == link
		with pytest.raises(TypeError):
			Link.force(100)
		elementLink = Link("config/element")
		attributeLink = Link("config/element:attribute")
		configElement = elementLink.resolve(mocked_basic_config_structure)
		attributeInstance = attributeLink.resolve(mocked_basic_config_structure)
		assert Link.force(configElement) == elementLink
		assert Link.force(attributeInstance) == attributeLink

	def test_isValidElementLink_method(self):
		assert Link("config/element").isValidElementLink() == True
		assert Link("config/element:attribute").isValidElementLink() == True
		assert Link("element:attribute").isValidElementLink() == False
		assert Link("element", Link.EMPHASIZE_ELEMENT).isValidElementLink() == False
		assert Link("config", Link.EMPHASIZE_CONFIG).isValidElementLink() == False

	def test_getLink_method(self):
		link = Link("config/element:attribute")
		assert link.getLink() == "config/element:attribute"
		assert link.getLink(Config=False) == "element:attribute"
		assert link.getLink(Element=False) == "config/:attribute"
		assert link.getLink(Attribute=False) == "config/element"
		assert link.getLink(Config=False, Attribute=False) == "/element"
		assert link.getLink(Config=False, Element=False) == ":attribute"
		assert link.getLink(Config=False, Element=False, Attribute=False) == ""
		link = Link("config/")
		assert link.getLink() == "config/"
		assert link.getLink(Config=False) == ""
		assert link.getLink(Element=False) == "config/"
		assert link.getLink(Attribute=False) == "config/"
		assert link.getLink(Config=False, Attribute=False) == ""
		assert link.getLink(Config=False, Element=False) == ""
		assert link.getLink(Config=False, Element=False, Attribute=False) == ""
		link = Link("/element")
		assert link.getLink() == "/element"
		assert link.getLink(Config=False) == "/element"
		assert link.getLink(Element=False) == ""
		assert link.getLink(Attribute=False) == "/element"
		assert link.getLink(Config=False, Attribute=False) == "/element"
		assert link.getLink(Config=False, Element=False) == ""
		assert link.getLink(Config=False, Element=False, Attribute=False) == ""

	def test_merge_method(self):
		link1 = Link("config/element1")
		link2 = Link("element2:attribute")
		link3 = link1.merge(link2)
		assert link1.config == "config"
		assert link1.element == "element1"
		assert link1.hasAttribute() == False
		assert link2.hasConfig() == False
		assert link2.element == "element2"
		assert link2.attribute == "attribute"
		assert link3.config == "config"
		assert link3.element == "element2"
		assert link3.attribute == "attribute"
		link4 = link1.merge("config1/:attribute1")
		assert link4.config == "config1"
		assert link4.element == "element1"
		assert link4.attribute == "attribute1"
		link4 = link2.merge("config2/")
		assert link4.config == "config2"
		assert link4.element == "element2"
		assert link4.attribute == "attribute"

	def test_resolve_methods(self, mocked_basic_config_structure: ConfigTypes.Configuration):
		configLink = Link("config/")
		elementLink = Link("config/element")
		attributeLink = Link("config/element:attribute")
		noConfigLink = Link("element:attribute")
		noElementLink = Link("config/:attribute")
		justAttributeLink = Link(":attribute")
		subconfig = mocked_basic_config_structure.getSubconfig("config")
		element = subconfig.getElement("element")
		attribute = element.getAttributeInstance("attribute")
		assert configLink.resolve(mocked_basic_config_structure) == subconfig
		assert elementLink.resolve(mocked_basic_config_structure) == element
		assert attributeLink.resolve(mocked_basic_config_structure) == attribute
		with pytest.raises(AttributeError):
			noConfigLink.resolve(mocked_basic_config_structure)
		with pytest.raises(AttributeError):
			justAttributeLink.resolve(mocked_basic_config_structure)
		assert noElementLink.resolve(mocked_basic_config_structure) == [(attribute, element)]
		with pytest.raises(ValueError):
			noConfigLink.resolveElement(mocked_basic_config_structure)
		with pytest.raises(ValueError):
			elementLink.resolveAttribute(mocked_basic_config_structure)
		with pytest.raises(ValueError):
			noConfigLink.resolveSubconfig(mocked_basic_config_structure)
		with pytest.raises(ValueError):
			noConfigLink.resolveAttributeList(mocked_basic_config_structure)
