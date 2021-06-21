from typing import List

def getGlobalLink(location: str, target: str):
	return location + "/" + target

def isGlobalLink(link: str):
	return "/" in link

def getConfigNameFromLink(globalLink: str):
	return globalLink.split("/")[0]

def splitGlobalLink(globalLink: str) -> List[str]:
	return globalLink.split("/")
