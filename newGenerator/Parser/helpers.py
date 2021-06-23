from typing import List

# helper decorator to ensure proper naming of functions
def overrides(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider

def getGlobalLink(location: str, target: str):
	return location + "/" + target

def isGlobalLink(link: str):
	if(link.count("/") <= 1):
		return "/" in link
	else:
		raise ValueError("Links are only allowed to have at most one nesting level ('/' character)")

def getConfigNameFromLink(globalLink: str):
	return globalLink.split("/")[0]

def splitGlobalLink(globalLink: str) -> List[str]:
	return globalLink.split("/")

def resolveConfigLink(config, configName: str, elementName: str):
	globalLink = getGlobalLink(configName, elementName)
	resolveConfigLink(config, globalLink)

def resolveConfigLink(config, link: str):
	isGlobal = isGlobalLink(link)
	if(isGlobal):
		configName, targetName = splitGlobalLink(link)
	else:
		configName = link
	try:
		subconfig = getattr(config, configName)
	except AttributeError:
		raise AttributeError(f"A config named \"{configName}\" was requested but a config with that name does not exist.")
	if(isGlobal):
		try:
			targetElement = getattr(subconfig, targetName)
		except AttributeError:
			raise AttributeError(f"An element called \"{targetName}\" was requested from config \"{configName}\" but an element with that name does not exist in that configuration.")
		return targetElement
	else:
		return subconfig

def toInt(hexValue: str):
	return int(hexValue, 16)

def toHex(intValue: int):
	return hex(intValue)
