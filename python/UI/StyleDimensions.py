import os
from typing import Any

from PySide6.QtCore import QMargins, QSize

class MetaStyleExtensionClass(type):
	def __getitem__(cls, key):
		custom_values = object.__getattribute__(cls, "custom_values")
		return custom_values[key][0]

	def __getattribute__(cls, name: str) -> Any:
		try:
			retunObj = object.__getattribute__(cls, name)
			return retunObj
		except AttributeError as e:
			custom_values = object.__getattribute__(cls, "custom_values")
			if(name in custom_values):
				return custom_values[name]
			else:
				raise e

class styleExtensions(object, metaclass=MetaStyleExtensionClass):
	custom_values = {
			"SIDEBAR_ICON_PADDING_LEFT": 12,
			"SIDEBAR_ICON_PADDING_RIGHT": 15,
			"CLOSE_BUTTON_HOVER_COLOR": "#c62828",
			"SIDEBAR_ICON_SIZE" : QSize(24, 24),
			"TITLEBAR_ICON_SIZE" : QSize(25, 25),
			"SIDEBAR_SHORT_TEXT_LENGTH" : 2,
			"TITLEBAR_WINDOW_ICON_SIZE" : 35,
			"TITLEBAR_WINDOW_ICON_MARGINS" : QMargins(10,2,2,2),
			"ERROR_COLOR": "#c62828",
			"ICON_BUTTON_SIZE" : QSize(24, 24),
			"ICON_BUTTON_COMPACT_SIZE" : QSize(18, 18),
		}

	def get_Parameters():
		base = os.environ
		extension = dict()
		for key, item in styleExtensions.custom_values.items():
			if(isinstance(item, QSize)):
				item: QSize
				extension[key + "_WIDTH"] = str(item.width())
				extension[key + "_HEIGHT"] = str(item.height())
			elif(isinstance(item, QMargins)):
				item: QMargins
				extension[key + "_LEFT"] = str(item.left())
				extension[key + "_RIGHT"] = str(item.right())
				extension[key + "_TOP"] = str(item.top())
				extension[key + "_BOTTOM"] = str(item.bottom())
			else:
				extension[key] = str(item)
		base.update(extension)
		return base
