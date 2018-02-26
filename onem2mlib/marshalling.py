#
#	marshalling.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module defines various internal functions for marchalling and unmarshalling of objects.
#

import json
import onem2mlib
import onem2mlib.internal as INT
import onem2mlib.exceptions as EXC

###############################################################################
#
#	Resource Base
#

def _resourceBase_parseXML(obj, root):
	rootTag = INT.xmlQualifiedName(root)
	obj.resourceName = INT.getAttribute(root, 'm2m:'+rootTag.localname, 'rn', obj.resourceName)
	obj.type = INT.getElement(root, 'ty', obj.type)
	obj.stateTag = INT.toInt(INT.getElement(root, 'st', obj.stateTag))
	obj.labels = INT.getElement(root, 'lbl', obj.labels)
	obj.resourceID = INT.getElement(root, 'ri', obj.resourceID)
	obj.parentID = INT.getElement(root, 'pi', obj.parentID)
	obj.creationTime = INT.getElement(root, 'ct', obj.creationTime)
	obj.lastModifiedTime = INT.getElement(root, 'lt', obj.lastModifiedTime)
	obj.accessControlPolicyIDs = INT.getElement(root, 'acpi', obj.accessControlPolicyIDs)
	obj.expirationTime = INT.getElement(root, 'et', obj.expirationTime)
	obj.announceTo = INT.getElement(root, 'at', obj.announceTo)
	obj.announcedAttribute = INT.getElement(root, 'aa', obj.announcedAttribute)
	# todo: dynamicAuthorizationConsultationIDs


# Create the XML for only some of the writable attributes.
def _resourceBase_createXML(obj, root, isUpdate):
	if obj.resourceName and not isUpdate: 	# No RN when updating
		root.attrib['rn'] = obj.resourceName
	INT.addToElement(root, 'lbl', obj.labels)
	INT.addToElement(root, 'aa', obj.announcedAttribute)
	INT.addToElement(root, 'at', obj.announceTo)
	INT.addToElement(root, 'acpi', obj.accessControlPolicyIDs)


def _resourceBase_parseJSON(obj, jsn):
	obj.resourceName = INT.getElementJSON(jsn, 'rn', obj.resourceName)
	obj.type = INT.getElementJSON(jsn, 'ty', obj.type)
	obj.stateTag = INT.toInt(INT.getElementJSON(jsn, 'st', obj.stateTag))
	obj.labels = INT.getElementJSON(jsn, 'lbl', obj.labels)
	obj.resourceID = INT.getElementJSON(jsn, 'ri', obj.resourceID)
	obj.parentID = INT.getElementJSON(jsn, 'pi', obj.parentID)
	obj.creationTime = INT.getElementJSON(jsn, 'ct', obj.creationTime)
	obj.lastModifiedTime = INT.getElementJSON(jsn, 'lt', obj.lastModifiedTime)
	obj.accessControlPolicyIDs = INT.getElementJSON(jsn, 'acpi', obj.accessControlPolicyIDs)
	obj.expirationTime = INT.getElementJSON(jsn, 'et', obj.expirationTime)
	obj.announceTo = INT.getElementJSON(jsn, 'at', obj.announceTo)
	obj.announcedAttribute = INT.getElementJSON(jsn, 'aa', obj.announcedAttribute)



# Create the JSON for only some of the writable attributes.
def _resourceBase_createJSON(obj, jsn, isUpdate):
	if obj.resourceName and not isUpdate: 	# No RN when updating
		INT.addToElementJSON(jsn, 'rn', obj.resourceName)
	INT.addToElementJSON(jsn, 'lbl', obj.labels)
	INT.addToElementJSON(jsn, 'aa', obj.announcedAttribute)
	INT.addToElementJSON(jsn, 'at', obj.announceTo)
	INT.addToElementJSON(jsn, 'acpi', obj.accessControlPolicyIDs)


###############################################################################
#
#	CSEBase
#

def _CSEBase_parseXML(obj, root):
	_resourceBase_parseXML(obj, root)
	obj.cseType = INT.toInt(INT.getElement(root, 'cst', obj.cseType))
	obj.supportedResourceTypes = INT.getElement(root, 'srt', obj.supportedResourceTypes)
	obj.pointOfAccess = INT.getElement(root, 'poa', obj.pointOfAccess)


def _CSEBase_parseJSON(obj, jsn):
	if 'm2m:cb' not in jsn:
		raise EXC.EncodingError('Wrong encoding: ' + str(jsn))
	_jsn = jsn['m2m:cb']
	_resourceBase_parseJSON(obj, _jsn)
	obj.cseType = INT.toInt(INT.getElementJSON(_jsn, 'cst', obj.cseType))
	obj.supportedResourceTypes = INT.getElementJSON(_jsn, 'srt', obj.supportedResourceTypes)
	obj.pointOfAccess = INT.getElementJSON(_jsn, 'poa', obj.pointOfAccess)



###############################################################################
#
#	RemoteCSE
#

def _remoteCSE_parseXML(obj, root):
	_resourceBase_parseXML(obj, root)
	obj.requestReachability = INT.getElement(root, 'rr', obj.requestReachability)
	obj.pointOfAccess = INT.getElement(root, 'poa', obj.pointOfAccess)
	obj.cseBase = INT.getElement(root, 'cb', obj.cseBase)
	obj.cseID = INT.getElement(root, 'csi', obj.cseID)


def _remoteCSE_parseJSON(obj, jsn):
	if 'm2m:csr' not in jsn:
		raise EXC.EncodingError('Wrong encoding: ' + str(jsn))
	_jsn = jsn['m2m:csr']
	_resourceBase_parseJSON(obj, _jsn)
	obj.requestReachability = INT.getElementJSON(_jsn, 'rr', obj.requestReachability)
	obj.pointOfAccess = INT.getElementJSON(_jsn, 'poa', obj.pointOfAccess)
	obj.cseBase = INT.getElementJSON(_jsn, 'cb', obj.cseBase)
	obj.cseID = INT.getElementJSON(_jsn, 'csi', obj.cseID)


###############################################################################
#
#	AccessControlPolicy
#

def _accessControlPolicy_parseXML(obj, root):
	#print(INT.xmlToString(root))
	_resourceBase_parseXML(obj, root)
	obj.privileges = []
	pv = INT.getElementWithChildren(root, 'pv')
	if pv is not None and len(pv)>0:
		acrs = INT.getElements(pv[0], 'acr', relative=True) # only the first element[0]
		for a in acrs:
			acr = onem2mlib.AccessControlRule()
			acr._parseXML(a)
			obj.privileges.append(acr)
	obj.selfPrivileges = []
	pvs = INT.getElementWithChildren(root, 'pvs')
	if pvs is not None and len(pvs)>0:
		acrs = INT.getElements(pvs[0], 'acr', relative=True) # only the first element[0]
		for a in acrs:
			acr = onem2mlib.AccessControlRule()
			acr._parseXML(a)
			obj.selfPrivileges.append(acr)


def _accessControlPolicy_createXML(obj, isUpdate=False):
	root = INT.createElement('acp', namespace='m2m')
	# add resource attributes
	_resourceBase_createXML(obj, root, isUpdate)
	pv = INT.addElement(root, 'pv')
	for p in obj.privileges:
		p._createXML(pv)
	pvs = INT.addElement(root, 'pvs')
	for p in obj.selfPrivileges:
		p._createXML(pvs)
	return root


def _accessControlPolicy_parseJSON(obj, jsn):
	#print(json.dumps(jsn, sort_keys=True, indent=4))
	if 'm2m:acp' not in jsn:
		raise EXC.EncodingError('Wrong encoding: ' + str(jsn))
	_jsn = jsn['m2m:acp']
	if _jsn is None:
		raise EXC.EncodingError('Wrong encoding: ' + jsn)
	_resourceBase_parseJSON(obj, _jsn)
	obj.privileges = []
	pv = INT.getElementJSON(_jsn, 'pv')
	if pv:
		acrs = INT.getElementJSON(pv, 'acr')
		if acrs:
			for ajsn in acrs:
				acr = onem2mlib.AccessControlRule()
				acr._parseJSON(ajsn)	
				obj.privileges.append(acr)	
	obj.selfPrivileges = []
	pvs = INT.getElementJSON(_jsn, 'pvs')
	if pvs:
		acrs = INT.getElementJSON(pvs, 'acr')
		if acrs:
			for ajsn in acrs:
				acr = onem2mlib.AccessControlRule()
				acr._parseJSON(ajsn)
				obj.selfPrivileges.append(acr)	


def _accessControlPolicy_createJSON(obj, isUpdate=False):
	data = {}
	_resourceBase_createJSON(obj, data, isUpdate)
	if obj.privileges:
		pv = {}
		pv['acr'] = [ p._createJSON() for p in obj.privileges ]
		data['pv'] = pv
	if obj.selfPrivileges:
		pvs = {}
		pvs['acr'] = [ p._createJSON() for p in obj.selfPrivileges ]
		data['pvs'] = pvs
	return {'m2m:acp' : data}



###############################################################################
#
#	AccessControlRule
#

def _accessControlRule_parseXML(obj, root):
	obj.accessControlOriginators = []
	acors = INT.getElements(root, 'acor', relative=True)
	if acors:
		obj.accessControlOriginators = [ acor.text for acor in acors ]
	obj.accessControlOperations = INT.getElement(root, 'acop', 0, relative=True)


def _accessControlRule_createXML(obj, root):
	acr = INT.addElement(root, 'acr')
	for acor in obj.accessControlOriginators:
		INT.addToElement(acr, 'acor', acor)
	INT.addToElement(acr, 'acop', obj.accessControlOperations)


def _accessControlRule_parseJSON(obj, jsn):
	obj.accessControlOriginators = INT.getElementJSON(jsn, 'acor', [])
	obj.accessControlOperations = INT.getElementJSON(jsn, 'acop', 0)


def _accessControlRule_createJSON(obj):
	jsn = {}
	INT.addToElementJSON(jsn, 'acor', obj.accessControlOriginators)
	INT.addToElementJSON(jsn, 'acop', obj.accessControlOperations)
	return jsn


###############################################################################
#
#	AE
#

def _AE_parseXML(obj, root):
	_resourceBase_parseXML(obj, root)
	obj.appID = INT.getElement(root, 'api', obj.appID)
	obj.AEID = INT.getElement(root, 'aei', obj.AEID)
	obj.requestReachability = INT.getElement(root, 'rr', obj.requestReachability)
	obj.pointOfAccess = INT.getElement(root, 'poa', obj.pointOfAccess)


def _AE_createXML(obj, isUpdate=False):
	root = INT.createElement('ae', namespace='m2m')
	_resourceBase_createXML(obj, root, isUpdate)
	if obj.appID and not isUpdate: 		# No api when updating
		INT.addToElement(root, 'api', obj.appID)
	if obj.AEID and not isUpdate:	# No api when updating
		INT.addToElement(root, 'aei', obj.AEID)
	INT.addToElement(root, 'rr', obj.requestReachability)
	INT.addToElement(root, 'poa', obj.pointOfAccess)
	return root


def _AE_parseJSON(obj, jsn):
	if 'm2m:ae' not in jsn:
		raise EXC.EncodingError('Wrong encoding: ' + str(jsn))
	_jsn = jsn['m2m:ae']
	if _jsn is None:
		raise EXC.EncodingError('Wrong encoding: ' + jsn)
	_resourceBase_parseJSON(obj, _jsn)
	obj.appID = INT.getElementJSON(_jsn, 'api', obj.appID)
	obj.AEID = INT.getElementJSON(_jsn, 'aei', obj.AEID)
	obj.requestReachability = INT.getElementJSON(_jsn, 'rr', obj.requestReachability)
	obj.pointOfAccess = INT.getElementJSON(_jsn, 'poa', obj.pointOfAccess)


def _AE_createJSON(obj, isUpdate=False):
	data = {}
	_resourceBase_createJSON(obj, data, isUpdate)
	if obj.appID and not isUpdate: 		# No api when updating
		INT.addToElementJSON(data, 'api', obj.appID)
	if obj.AEID and not isUpdate:	# No api when updating
		INT.addToElementJSON(data, 'aei', obj.AEID)
	INT.addToElementJSON(data, 'rr', obj.requestReachability)
	INT.addToElementJSON(data, 'poa', obj.pointOfAccess)
	return {'m2m:ae' : data}


###############################################################################
#
#	Container
#

def _Container_parseXML(obj, root):
	_resourceBase_parseXML(obj, root)
	obj.maxNrOfInstances = INT.toInt(INT.getElement(root, 'mni', obj.maxNrOfInstances))
	obj.maxByteSize = INT.toInt(INT.getElement(root, 'mbs', obj.maxByteSize))
	obj.maxInstanceAge = INT.toInt(INT.getElement(root, 'mia', obj.maxInstanceAge))
	obj.currentNrOfInstances = INT.toInt(INT.getElement(root, 'cni', obj.currentNrOfInstances))
	obj.currentByteSize = INT.toInt(INT.getElement(root, 'cbs', obj.currentByteSize))
	obj.oldest = INT.getElement(root, 'ol', obj.oldest)
	obj.latest = INT.getElement(root, 'la', obj.latest)


def _Container_createXML(obj, isUpdate=False):
	root = INT.createElement('cnt', namespace='m2m')
	_resourceBase_createXML(obj, root, isUpdate)
	INT.addToElement(root, 'mni', obj.maxNrOfInstances)
	INT.addToElement(root, 'mbs', obj.maxByteSize)
	INT.addToElement(root, 'mia', obj.maxInstanceAge)
	return root


def _Container_parseJSON(obj, jsn):
	if 'm2m:cnt' not in jsn:
		raise EXC.EncodingError('Wrong encoding: ' + str(jsn))
	_jsn = jsn['m2m:cnt']
	_resourceBase_parseJSON(obj, _jsn)
	obj.maxNrOfInstances = INT.getElementJSON(_jsn, 'mni', obj.maxNrOfInstances)
	obj.maxByteSize = INT.getElementJSON(_jsn, 'mbs', obj.maxByteSize)
	obj.maxInstanceAge = INT.getElementJSON(_jsn, 'mia', obj.maxInstanceAge)
	obj.currentNrOfInstances = INT.getElementJSON(_jsn, 'cni', obj.currentNrOfInstances)
	obj.currentByteSize = INT.getElementJSON(_jsn, 'cbs', obj.currentByteSize)
	obj.oldest = INT.getElementJSON(_jsn, 'ol', obj.oldest)
	obj.latest = INT.getElementJSON(_jsn, 'la', obj.latest)


def _Container_createJSON(obj, isUpdate=False):
	data = {}
	_resourceBase_createJSON(obj, data, isUpdate)
	INT.addToElementJSON(data, 'mni', obj.maxNrOfInstances)
	INT.addToElementJSON(data, 'mbs', obj.maxByteSize)
	INT.addToElementJSON(data, 'mia', obj.maxInstanceAge)
	return {'m2m:cnt' : data}


###############################################################################
#
#	ContentInstance
#

def _ContentInstance_parseXML(obj, root):
	_resourceBase_parseXML(obj, root)
	obj.contentInfo = INT.getElement(root, 'cnf', obj.contentInfo)
	obj.contentSize = INT.toInt(INT.getElement(root, 'cs', obj.contentSize))
	obj.content = INT.getElement(root, 'con', obj.content)


def _ContentInstance_createXML(obj, isUpdate=False):
	root = INT.createElement('cin', namespace='m2m')
	_resourceBase_createXML(obj, root, isUpdate)
	INT.addToElement(root, 'cnf', obj.contentInfo)
	INT.addToElement(root, 'con', obj.content)
	return root


def _ContentInstance_parseJSON(obj, jsn):
	#print(json.dumps(jsn, sort_keys=True, indent=4))
	if 'm2m:cin' not in jsn:
		raise EXC.EncodingError('Wrong encoding: ' + str(jsn))
	_jsn = jsn['m2m:cin']
	if _jsn is None:
		raise EXC.EncodingError('Wrong encoding: ' + jsn)
	_resourceBase_parseJSON(obj, _jsn)
	obj.contentInfo = INT.getElementJSON(_jsn, 'cnf', obj.contentInfo)
	obj.contentSize = INT.getElementJSON(_jsn, 'cs', obj.contentSize)
	obj.content = INT.getElementJSON(_jsn, 'con', obj.content)


def _ContentInstance_createJSON(obj, isUpdate=False):
	data = {}
	_resourceBase_createJSON(obj, data, isUpdate)
	INT.addToElementJSON(data, 'cnf', obj.contentInfo)
	INT.addToElementJSON(data, 'con', obj.content)
	return {'m2m:cin' : data}


###############################################################################
#
#	Group
#

def _Group_parseXML(obj, root):
	_resourceBase_parseXML(obj, root)
	obj.maxNrOfMembers = INT.toInt(INT.getElement(root, 'mnm', obj.maxNrOfMembers))
	obj.memberType = INT.toInt(INT.getElement(root, 'mt', obj.memberType))
	obj.currentNrOfMembers = INT.toInt(INT.getElement(root, 'cnm', obj.currentNrOfMembers))
	obj.memberIDs = INT.getElement(root, 'mid', obj.memberIDs)
	obj.memberTypeValidated = INT.getElement(root, 'mtv', obj.memberTypeValidated)
	obj.consistencyStrategy = INT.toInt(INT.getElement(root, 'csy', obj.consistencyStrategy))
	obj.groupName = INT.getElement(root, 'gn', obj.groupName)
	obj.fanOutPoint = INT.getElement(root, 'fopt', obj.fanOutPoint)


def _Group_createXML(obj, isUpdate):
	root = INT.createElement('grp', namespace='m2m')
	_resourceBase_createXML(obj, root, isUpdate)
	if obj.maxNrOfMembers and not isUpdate: 	# No mnm when updating
		INT.addToElement(root, 'mnm', obj.maxNrOfMembers)
	INT.addToElement(root, 'mt', obj.memberType)
	INT.addToElement(root, 'mid', obj.memberIDs, mandatory=True)
	if obj.consistencyStrategy and not isUpdate: 	# No csy when updating
		INT.addToElement(root, 'csy', obj.consistencyStrategy)
	INT.addToElement(root, 'gn', obj.groupName)
	return root


def _Group_parseJSON(obj, jsn):
	if 'm2m:grp' not in jsn:
		raise EXC.EncodingError('Wrong encoding: ' + str(jsn))
	_jsn = jsn['m2m:grp']
	if _jsn is None:
		raise EXC.EncodingError('Wrong encoding: ' + jsn)
	_resourceBase_parseJSON(obj, _jsn)
	obj.maxNrOfMembers = INT.getElementJSON(_jsn, 'mnm', obj.maxNrOfMembers)
	obj.memberType = INT.getElementJSON(_jsn, 'mt', obj.memberType)
	obj.currentNrOfMembers = INT.getElementJSON(_jsn, 'cnm', obj.currentNrOfMembers)
	obj.memberIDs = INT.getElementJSON(_jsn, 'mid', obj.memberIDs)
	obj.memberTypeValidated = INT.getElementJSON(_jsn, 'mtv', obj.memberTypeValidated)
	obj.consistencyStrategy = INT.getElementJSON(_jsn, 'csy', obj.consistencyStrategy)
	obj.groupName = INT.getElementJSON(_jsn, 'gn', obj.groupName)
	obj.fanOutPoint = INT.getElementJSON(_jsn, 'fopt', obj.fanOutPoint)


def _Group_createJSON(obj, isUpdate):
	data = {}
	_resourceBase_createJSON(obj, data, isUpdate)
	if obj.maxNrOfMembers and not isUpdate: 	# No mnm when updating
		INT.addToElementJSON(data, 'mnm', obj.maxNrOfMembers)
	INT.addToElementJSON(data, 'mt', obj.memberType)
	INT.addToElementJSON(data, 'mid', obj.memberIDs, mandatory=True)
	if obj.consistencyStrategy and not isUpdate: 	# No csy when updating
		INT.addToElementJSON(data, 'csy', obj.consistencyStrategy)
	INT.addToElementJSON(data, 'gn', obj.groupName)
	return {'m2m:grp' : data}



###############################################################################
#
#	Subscription
#

def _Subscription_parseXML(obj, root):
	_resourceBase_parseXML(obj, root)
	obj.notificationURI = INT.getElement(root, 'nu', obj.notificationURI)
	obj.notificationContentType = INT.toInt(INT.getElement(root, 'nct', obj.notificationContentType))
	obj.expirationCounter = INT.toInt(INT.getElement(root, 'exc', obj.expirationCounter))
	obj.latestNotify = INT.getElement(root, 'ln', obj.latestNotify)
	obj.groupID = INT.getElement(root, 'gpi', obj.groupID)
	obj.notificationForwardingURI = INT.getElement(root, 'nfu', obj.notificationForwardingURI)
	obj.subscriberURI = INT.getElement(root, 'su', obj.subscriberURI)


def _Subscription_createXML(obj, isUpdate=False):
	root = INT.createElement('sub', namespace='m2m')
	_resourceBase_createXML(obj, root, isUpdate)
	INT.addToElement(root, 'nu', obj.notificationURI)
	INT.addToElement(root, 'nct', obj.notificationContentType)
	if obj.expirationCounter != -1:
		INT.addToElement(root, 'exc', obj.expirationCounter)
	if obj.latestNotify:
		INT.addToElement(root, 'ln', obj.latestNotify)
	if obj.groupID:
		INT.addToElement(root, 'gpi', obj.groupID)
	if obj.notificationForwardingURI:
		INT.addToElement(root, 'nfu', obj.notificationForwardingURI)
	if obj.subscriberURI:
		INT.addToElement(root, 'su', obj.subscriberURI)
	return root


def _Subscription_parseJSON(obj, jsn):
	if 'm2m:sub' not in jsn:
		raise EXC.EncodingError('Wrong encoding: ' + str(jsn))
	_jsn = jsn['m2m:sub']
	if _jsn is None:
		raise EXC.EncodingError('Wrong encoding: ' + jsn)
	_resourceBase_parseJSON(obj, _jsn)
	obj.notificationURI = INT.getElementJSON(_jsn, 'nu', obj.notificationURI)
	obj.notificationContentType = INT.getElementJSON(_jsn, 'nct', obj.notificationContentType)
	obj.expirationCounter = INT.getElementJSON(_jsn, 'exc', obj.expirationCounter)
	obj.latestNotify = INT.getElementJSON(_jsn, 'ln', obj.latestNotify)
	obj.groupID = INT.getElementJSON(_jsn, 'gpi', obj.groupID)
	obj.notificationForwardingURI = INT.getElementJSON(_jsn, 'nfu', obj.notificationForwardingURI)
	obj.subscriberURI = INT.getElementJSON(_jsn, 'su', obj.subscriberURI)


def _Subscription_createJSON(obj, isUpdate=False):
	data = {}
	_resourceBase_createJSON(obj, data, isUpdate)
	INT.addToElementJSON(data, 'nu', obj.notificationURI)
	INT.addToElementJSON(data, 'nct', obj.notificationContentType)
	if obj.expirationCounter != -1:
		INT.addToElementJSON(data, 'exc', obj.expirationCounter)
	if obj.latestNotify:
		INT.addToElementJSON(data, 'ln', obj.latestNotify)
	if obj.groupID:
		INT.addToElementJSON(data, 'gpi', obj.groupID)
	if obj.notificationForwardingURI:
		INT.addToElementJSON(data, 'nfu', obj.notificationForwardingURI)
	if obj.subscriberURI:
		INT.addToElementJSON(data, 'su', obj.subscriberURI)
	return {'m2m:sub' : data}
