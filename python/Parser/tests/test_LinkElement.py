import pytest
from Parser import Link

class TestClassLinkFunctions:

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
