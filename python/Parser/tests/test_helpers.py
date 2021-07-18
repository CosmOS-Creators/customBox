import pytest
from Parser.helpers import overrides, toHex, toInt, forceStrList

class TestHelperFunctions:

	def test_overrides_decorator(self):
		class baseClass:
			def test(self):
				return 0

		class inheritedClass(baseClass):
			@overrides(baseClass)
			def test(self):
				return 1

		instance = inheritedClass()
		assert instance.test() == 1

		with pytest.raises(AssertionError):
			class inheritedClass1(baseClass):
				@overrides(baseClass)
				def test1(self):
					return 2

	def test_converterFunctions(self):
		assert toHex(15) == "0xF"
		assert toHex(0) == "0x0"
		assert toHex(256) == "0x100"
		with pytest.raises(TypeError):
			toHex(None)
		with pytest.raises(TypeError):
			toHex(1.5)
		assert toInt("0x10") == 16
		assert toInt("0xFF") == 255
		assert toInt("0x00F") == 15
		assert toInt("0F") == 15

	def test_forceStrList_function(self):
		assert forceStrList("test") == ["test"]
		assert forceStrList(["test"]) == ["test"]
		assert forceStrList(["test", "test1"]) == ["test", "test1"]
		with pytest.raises(TypeError):
			forceStrList(0)
		with pytest.raises(TypeError):
			forceStrList([0])
		with pytest.raises(TypeError):
			forceStrList(["test", 0])
