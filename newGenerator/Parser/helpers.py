from typing import List

def getGlobalLink(location: str, target: str):
	return location + "/" + target

def isGlobalLink(link: str):
	return "/" in link

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
