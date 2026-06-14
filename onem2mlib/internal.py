#
#	internal.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
"""	This module defines various internal utility functions for the library.
"""

from __future__ import annotations
from typing import Any, Optional, Union, TYPE_CHECKING

from requests import Response

from . import constants as CON
from . import mcarequests as MCA
from . import utilities as UT
from .resources.ResourceBase import ResourceBase
from .resources.AE import AE
from .resources.Container import Container
from .resources.ContentInstance import ContentInstance
from .resources.Group import Group
from .resources.RemoteCSE import RemoteCSE
from .resources.FlexContainer import FlexContainer
from .resources.AccessControlPolicy import AccessControlPolicy
from .resources.Subscription import Subscription


if TYPE_CHECKING:
	import requests


###############################################################################

#
#	JSON Utilities
#

def getElementJSON(jsn: dict, elemName: str, default: Any = None) -> Any:
	"""	Find a tag value from the JSON dictionaty or, if not found, return the default.

		Args:
			jsn: The JSON dictionary to search in.
			elemName: The name of the element to find.
			default: The default value to return if the element is not found.

		Returns:
			The value of the element if found, otherwise the default value.
		"""
	if elemName in jsn:
		elem = jsn[elemName]
		return elem
	return default


def addToElementJSON(jsn: dict, name: str, content: Any, mandatory: bool = False) -> None:
	"""	Add an element to the JSON content.

		Args:
			jsn: The JSON dictionary to add the element to.
			name: The name of the element to add.
			content: The content of the element to add.
			mandatory: If True, the element is added even if the content is empty or None. Default is False.
	"""
	if isinstance(content, int) or (content and len(content) > 0) or mandatory:
		jsn[name] = content

# Find all the sub-structures of a specific name inside a JSON document
# TODO: Replace this with some xpath-like query package
def getALLSubElementsJSON(jsn: dict, name: str) -> list:
	result = []
	for elemName in jsn:
		elem = jsn[elemName]
		if elemName == name:
			result.append(elem)
		elif isinstance(elem, dict):
			result.extend(getALLSubElementsJSON(elem, name))
		elif isinstance(elem, list):
			for e in elem:
				if isinstance(e, dict):
					result.extend(getALLSubElementsJSON(e, name))
	return result


def wrapJSON(obj: ResourceBase, jsn: dict) -> dict:
	return {f'{obj.namespace}:{obj.typeShortName}': jsn}


###############################################################################
#
#	Utilities
#

# Get the type from a response, for JSON
def getTypeFromResponse(response: requests.Response) -> int:
	jsn = response.json()
	# This is a bit complicated. We need to get to the type, which is hidden under an
	# unknown object definition key. So, we asume that the JSON we get has the object
	# definition in the first element (as it should be).
	inner = list(jsn.values())[0]
	return getElementJSON(inner, 'ty')

###############################################################################
#
#	Formatting
#

_width = 45

def strResource(name: str, 
				shortName: str, 
				value: ResourceBase|str|int|bool|list[str]|list[int], 
				minusIndent: int = 0) -> str:
	if value is None:
		return ''
	if isinstance(value, list) and len(value) == 0:
		return '' 
	if not isinstance(value, str):
		value = str(value)
	if value and len(value) > 0:
		if shortName:
			return f'\t{name}({shortName}):'.ljust(_width-minusIndent) + str(value) + '\n'
		else:
			return f'\t{name}:'.ljust(_width-minusIndent) + str(value) + '\n'
	return ''


# Convert to an integer, except when it is None, then return None.
def toInt(value: Any) -> Optional[int]:
	"""	Convert a value to an integer, except when it is None, then return None.
		Args:
			value: The value to convert to an integer.

		Returns:
			The integer value if conversion is possible, otherwise None.
	"""
	if value is None:
		return None
	return int(value)


# Return the formatted resource name, id and type
def nameAndType(resource: ResourceBase) -> str:
	"""	Return a string with the resource name, id and type of the given resource.

		Args:
			resource: The resource to get the name and type from.

		Returns:
			A string with the resource name, id and type of the given resource.
	"""
	if resource is None or resource.type is None:
		return "NONE"
	rn = resource.resourceName if resource.resourceName is not None else 'unknown'
	ri = resource.resourceID if resource.resourceID is not None else "unknown"
	return rn + '(' +  ri + ') [' +  typeToString(resource.type) + ']'


# Return the resource type as a string
def typeToString(ty: int) -> str:
	res = [		"mixed", "accessControlPolicy", "AE", "container", "contentInstance", "CSEBase", "delivery", "eventConfig", "execInstance",
				"group", "locationPolicy", "m2mServiceSubscriptionProfile", "mgmtCmd", "mgmtObj", "node", "pollingChannel",
				"remoteCSE", "request", "schedule", "serviceSubscribedAppRule", "serviceSubscribedNode", "statsCollect",
				"statsConfig", "subscription", "semanticDescriptor", "notificationTargetMgmtPolicyRef", "notificationTargetPolicy",
				"policyDeletionRules", "flexContainer", "timeSeries", "timeSeriesInstance", "role", "token", "void",
				"dynamicAuthorizationConsultation", "authorizationDecision", "authorizationPolicy", "authorizationInformation",
				"ontologyRepository", "ontology", "semanticMashupJobProfile", "semanticMashupInstance", "semanticMashupResult",
				"AEContactList", "AEContactListPerCSE", "localMulticastGroup", "multimediaSession", "triggerRequest",
				"crossResourceSubscription"]
	resAnnc = [	"", "accessControlPolicyAnnc", "AEAnnc", "containerAnnc", "contentInstanceAnnc", "", "", "", "", "groupAnnc",
				"locationPolicyAnnc", "", "", "mgmtObjAnnc", "nodeAnnc", "", "remoteCSEAnnc", "", "scheduleAnnc", "", "",
				"", "", "", "semanticDescriptorAnnc", "", "", "", "flexContainerAnnc", "timeSeriesAnnc", "timeSeriesInstanceAnnc",
				"void", "dynamicAuthorizationConsultationAnnc", "", "", "", "ontologyRepositoryAnnc", "ontologyAnnc", 
				"semanticMashupJobProfileAnnc", "semanticMashupInstanceAnnc", "semanticMashupResultAnnc", "", "", "",
				"multimediaSessionAnnc"]

	if ty < 10000:
		if ty >= 0 and ty <= len(res)+1:
			return res[ty]
	else:
		if ty > 10000 and ty <= len(resAnnc)+1:
			return resAnnc[ty - 10000];
	return "unknown"



	


###############################################################################
#
#	Search
#

# Find a child-resource
def _findSubResource(resource: ResourceBase, 
					 type: int, 
					 filter: Optional[list[tuple[str, str|int|bool]]] = None, 
					 originator: str = None) -> Optional[list[ResourceBase]]:

	if not resource or not resource.session or not resource.resourceID: 
		return None
	result = []
 
	combined_filter: list[tuple[str, str|int|bool]] = [UT.newTypeFilterCriteria(int(type))]
	
	if filter:
		if isinstance(filter, list):
			combined_filter.extend(filter)
		else:
			# Handle case where only a single tuple was passed instead of a list
			combined_filter.append(filter)

 
 
	ris = MCA.discoverInCSE(resource, filter=combined_filter, structuredResult=True, originator=originator)
	if ris:
		#	The following is a hack to restrict the search result to the direct child
		#	level. Yes, the oneM2M "level" attribute could be used for that, but it
		#	doesn't seem to be supported that much (at least not in om2m).
		#	Anyway, the hack works like that: count the forward slashes, ie. the 
		#	number of path elements, and only add those from the response to the result
		#	which have count+1 path elements.

		sid = resource._structuredResourceID()
		count = sid.count('/') + 1

		for ri in ris:
			if ri.count('/') == count:	# <- hack s.o.
				subResource = _newResourceFromRID(type, ri, resource)
				subResource.retrieveFromCSE()
				result.append(subResource)
			elif ri[0] != '/':	# Hack for Mobius. where they just return an unstructured RI, no matter what
				subResource = _newResourceFromRID(type, ri, resource)
				subResource.retrieveFromCSE()
				result.append(subResource)
		# Still a hack: sort the list by the ct attribute
		result.sort(key=lambda x: x.creationTime)

	return result


# Find a resource from a list by its resource name
def _findResourceInList(resources: list[ResourceBase], resourceName: str) -> Optional[ResourceBase]:
	for res in resources:
		if res.resourceName == resourceName:
			return res
	return None


# Create a new resource object with a given type, RI and parent
def _newResourceFromRID(type: int, 
						ri: str, 
						parent: Optional[ResourceBase] = None, 
						originator: Optional[str] = None) -> Optional[ResourceBase]:
	res = _newResourceFromType(type, parent, originator=originator)
	if res:
		res.resourceID = ri
	return res


def _newResourceFromType(type: int, parent: Optional[ResourceBase] = None, originator: Optional[str] = None) -> Optional[ResourceBase]:
	if type == CON.Type_ContentInstance:	return ContentInstance(parent=parent, originator=originator, instantly=False)
	elif type == CON.Type_Container:		return Container(parent=parent, originator=originator, instantly=False)
	elif type == CON.Type_AE:				return AE(parent=parent, originator=originator, instantly=False)
	elif type == CON.Type_Group:			return Group(parent=parent, originator=originator, instantly=False)
	elif type == CON.Type_ACP:				return AccessControlPolicy(parent=parent, originator=originator, instantly=False)
	elif type == CON.Type_Subscription:		return Subscription(parent=parent, originator=originator, instantly=False)
	elif type == CON.Type_RemoteCSE:		return RemoteCSE(parent=parent, originator=originator, instantly=False)
	elif type == CON.Type_FlexContainer:	return FlexContainer(parent=parent, originator=originator, instantly=False)
	return None


def _newResourceFromTypeString(typeString: str,
							   parent: Optional[ResourceBase] = None,
							   namespace: str = 'm2m', 
							   originator: Optional[str] = None) -> Optional[ResourceBase]:
	if namespace == 'm2m':
		if typeString == 'cin':		return _newResourceFromType(CON.Type_ContentInstance, parent, originator=originator)
		elif typeString == 'cnt':	return _newResourceFromType(CON.Type_Container, parent, originator=originator)
		elif typeString == 'ae':	return _newResourceFromType(CON.Type_AE, parent, originator=originator)
		elif typeString == 'grp':	return _newResourceFromType(CON.Type_Group, parent, originator=originator)
		elif typeString == 'acp':	return _newResourceFromType(CON.Type_ACP, parent, originator=originator)
		elif typeString == 'sub':	return _newResourceFromType(CON.Type_Subscription, parent, originator=originator)
		elif typeString == 'csr':	return _newResourceFromType(CON.Type_RemoteCSE, parent, originator=originator)
	return None


# Get a resource from the CSE by its resourceName
def _getResourceFromCSEByResourceName(type: int, 
									  rn: str, 
									  parent: Optional[ResourceBase] = None, 
									  originator: Optional[str]=None) -> Optional[ResourceBase]:
	res: Optional[ResourceBase] = None
	if rn.startswith('/'):	# Remove leading '/' in case we do a deep search
		rn = rn[1:]
	if type == CON.Type_ContentInstance:		res = ContentInstance(parent=parent, resourceName=rn, originator=originator, instantly=False)
	elif type == CON.Type_Container:			res = Container(parent=parent, resourceName=rn, originator=originator, instantly=False)
	elif type == CON.Type_AE:					res = AE(parent=parent, resourceName=rn, originator=originator, instantly=False)
	elif type == CON.Type_Group:				res = Group(parent=parent, resourceName=rn, originator=originator, instantly=False)
	elif type == CON.Type_ACP:					res = AccessControlPolicy(parent=parent, resourceName=rn, originator=originator, instantly=False)
	elif type == CON.Type_Subscription:			res = Subscription(parent=parent, resourceName=rn, originator=originator, instantly=False)
	elif type == CON.Type_RemoteCSE:			res = RemoteCSE(parent=parent, resourceName=rn, originator=originator, instantly=False)
	elif type == CON.Type_FlexContainer: 		res = FlexContainer(parent=parent, resourceName=rn, originator=originator, instantly=False)
	if res is not None and res.retrieveFromCSE():
		return res
	return None



