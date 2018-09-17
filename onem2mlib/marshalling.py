#
#	marshalling.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module defines various internal functions for marchalling and unmarshalling of objects.
#

import json, logging
import onem2mlib
import onem2mlib.internal as INT
import onem2mlib.exceptions as EXC

logger = logging.getLogger(__name__)

###############################################################################
#
#	Resource Base
#

def _resourceBase_parseXML(obj, root):
	rootTag = INT.xmlQualifiedName(root)

	obj.resourceName = INT.getAttribute(root, rootTag[1] + ':' + rootTag[0], 'rn', obj.resourceName)
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
def _resourceBase_createXML(obj, isUpdate):
	root = INT.createElement(obj.typeShortName, namespace=obj.namespace )
	if obj.resourceName and not isUpdate: 	# No RN when updating
		root.attrib['rn'] = obj.resourceName
	INT.addToElement(root, 'lbl', obj.labels)
	INT.addToElement(root, 'aa', obj.announcedAttribute)
	INT.addToElement(root, 'at', obj.announceTo)
	INT.addToElement(root, 'acpi', obj.accessControlPolicyIDs)
	return root


def _resourceBase_parseJSON(obj, jsn):
	name = obj.namespace + ':' + obj.typeShortName
	if name not in jsn:
		logger.error('Wrong encoding: ' + str(jsn))
		raise EXC.EncodingError('Wrong encoding: ' + str(jsn))
	_jsn = jsn[name]
	# if _jsn is None:
	# 	logger.error('Wrong encoding: ' + str(jsn))
	# 	raise EXC.EncodingError('Wrong encoding: ' + str(jsn))
	obj.resourceName = INT.getElementJSON(_jsn, 'rn', obj.resourceName)
	obj.type = INT.getElementJSON(_jsn, 'ty', obj.type)
	obj.stateTag = INT.toInt(INT.getElementJSON(_jsn, 'st', obj.stateTag))
	obj.labels = INT.getElementJSON(_jsn, 'lbl', obj.labels)
	obj.resourceID = INT.getElementJSON(_jsn, 'ri', obj.resourceID)
	obj.parentID = INT.getElementJSON(_jsn, 'pi', obj.parentID)
	obj.creationTime = INT.getElementJSON(_jsn, 'ct', obj.creationTime)
	obj.lastModifiedTime = INT.getElementJSON(_jsn, 'lt', obj.lastModifiedTime)
	obj.accessControlPolicyIDs = INT.getElementJSON(_jsn, 'acpi', obj.accessControlPolicyIDs)
	obj.expirationTime = INT.getElementJSON(_jsn, 'et', obj.expirationTime)
	obj.announceTo = INT.getElementJSON(_jsn, 'at', obj.announceTo)
	obj.announcedAttribute = INT.getElementJSON(_jsn, 'aa', obj.announcedAttribute)
	return _jsn


# Create the JSON for only some of the writable attributes.
def _resourceBase_createJSON(obj, isUpdate):
	jsn = {}
	if obj.resourceName and not isUpdate: 	# No RN when updating
		INT.addToElementJSON(jsn, 'rn', obj.resourceName)
	INT.addToElementJSON(jsn, 'lbl', obj.labels)
	INT.addToElementJSON(jsn, 'aa', obj.announcedAttribute)
	INT.addToElementJSON(jsn, 'at', obj.announceTo)
	INT.addToElementJSON(jsn, 'acpi', obj.accessControlPolicyIDs)
	return jsn


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
	_jsn = _resourceBase_parseJSON(obj, jsn)
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
	_jsn = _resourceBase_parseJSON(obj, jsn)
	obj.requestReachability = INT.getElementJSON(_jsn, 'rr', obj.requestReachability)
	obj.pointOfAccess = INT.getElementJSON(_jsn, 'poa', obj.pointOfAccess)
	obj.cseBase = INT.getElementJSON(_jsn, 'cb', obj.cseBase)
	obj.cseID = INT.getElementJSON(_jsn, 'csi', obj.cseID)


###############################################################################
#
#	AccessControlPolicy
#

def _accessControlPolicy_parseXML(obj, root):
	_resourceBase_parseXML(obj, root)
	obj.privileges = []
	pv = INT.getElementWithChildren(root, 'pv')
	if pv is not None and len(pv)>0:
		acrs = INT.getElements(pv[0], 'acr', relative=True) # only the first element[0]
		for a in acrs:
			acr = onem2mlib.AccessControlRule()
			_accessControlPolicy_parseXML(acr, a)
			#acr._parseXML(a)
			obj.privileges.append(acr)
	obj.selfPrivileges = []
	pvs = INT.getElementWithChildren(root, 'pvs')
	if pvs is not None and len(pvs)>0:
		acrs = INT.getElements(pvs[0], 'acr', relative=True) # only the first element[0]
		for a in acrs:
			acr = onem2mlib.AccessControlRule()
			_accessControlPolicy_parseXML(acr, a)
			#acr._parseXML(a)
			obj.selfPrivileges.append(acr)


def _accessControlPolicy_createXML(obj, isUpdate=False):
	# add resource attributes
	root = _resourceBase_createXML(obj, isUpdate)
	pv = INT.addElement(root, 'pv')
	for p in obj.privileges:
		_accessControlRule_createXML(p, pv)
		#p._createXML(pv)
	pvs = INT.addElement(root, 'pvs')
	for p in obj.selfPrivileges:
		_accessControlRule_createXML(p, pvs)
		#p._createXML(pvs)
	return root


def _accessControlPolicy_parseJSON(obj, jsn):
	_jsn = _resourceBase_parseJSON(obj, jsn)
	obj.privileges = []
	pv = INT.getElementJSON(_jsn, 'pv')
	if pv:
		acrs = INT.getElementJSON(pv, 'acr')
		if acrs:
			for ajsn in acrs:
				acr = onem2mlib.AccessControlRule()
				_accessControlRule_parseJSON(acr, ajsn)
				#acr._parseJSON(ajsn)	
				obj.privileges.append(acr)	
	obj.selfPrivileges = []
	pvs = INT.getElementJSON(_jsn, 'pvs')
	if pvs:
		acrs = INT.getElementJSON(pvs, 'acr')
		if acrs:
			for ajsn in acrs:
				acr = onem2mlib.AccessControlRule()
				_accessControlRule_parseJSON(acr, ajsn)
				#acr._parseJSON(ajsn)
				obj.selfPrivileges.append(acr)	


def _accessControlPolicy_createJSON(obj, isUpdate=False):
	jsn = _resourceBase_createJSON(obj, isUpdate)
	if obj.privileges:
		pv = {}
		#pv['acr'] = [ p._createJSON() for p in obj.privileges ]
		pv['acr'] = [ _accessControlRule_createJSON(p) for p in obj.privileges ]
		jsn['pv'] = pv
	if obj.selfPrivileges:
		pvs = {}
		#pvs['acr'] = [ p._createJSON() for p in obj.selfPrivileges ]
		pvs['acr'] = [ _accessControlRule_createJSON(p) for p in obj.selfPrivileges ]
		jsn['pvs'] = pvs
	return INT.wrapJSON(obj, jsn)



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
	root = _resourceBase_createXML(obj, isUpdate)
	if obj.appID and not isUpdate: 		# No api when updating
		INT.addToElement(root, 'api', obj.appID)
	if obj.AEID and not isUpdate:	# No api when updating
		INT.addToElement(root, 'aei', obj.AEID)
	INT.addToElement(root, 'rr', obj.requestReachability)
	INT.addToElement(root, 'poa', obj.pointOfAccess)
	return root


def _AE_parseJSON(obj, jsn):
	_jsn = _resourceBase_parseJSON(obj, jsn)
	obj.appID = INT.getElementJSON(_jsn, 'api', obj.appID)
	obj.AEID = INT.getElementJSON(_jsn, 'aei', obj.AEID)
	obj.requestReachability = INT.getElementJSON(_jsn, 'rr', obj.requestReachability)
	obj.pointOfAccess = INT.getElementJSON(_jsn, 'poa', obj.pointOfAccess)


def _AE_createJSON(obj, isUpdate=False):
	jsn = _resourceBase_createJSON(obj, isUpdate)
	if obj.appID and not isUpdate: 		# No api when updating
		INT.addToElementJSON(jsn, 'api', obj.appID)
	if obj.AEID and not isUpdate:	# No api when updating
		INT.addToElementJSON(jsn, 'aei', obj.AEID)
	INT.addToElementJSON(jsn, 'rr', obj.requestReachability)
	INT.addToElementJSON(jsn, 'poa', obj.pointOfAccess)
	return INT.wrapJSON(obj, jsn)


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
	root = _resourceBase_createXML(obj, isUpdate)
	INT.addToElement(root, 'mni', obj.maxNrOfInstances)
	INT.addToElement(root, 'mbs', obj.maxByteSize)
	INT.addToElement(root, 'mia', obj.maxInstanceAge)
	return root


def _Container_parseJSON(obj, jsn):
	_jsn = _resourceBase_parseJSON(obj, jsn)
	obj.maxNrOfInstances = INT.getElementJSON(_jsn, 'mni', obj.maxNrOfInstances)
	obj.maxByteSize = INT.getElementJSON(_jsn, 'mbs', obj.maxByteSize)
	obj.maxInstanceAge = INT.getElementJSON(_jsn, 'mia', obj.maxInstanceAge)
	obj.currentNrOfInstances = INT.getElementJSON(_jsn, 'cni', obj.currentNrOfInstances)
	obj.currentByteSize = INT.getElementJSON(_jsn, 'cbs', obj.currentByteSize)
	obj.oldest = INT.getElementJSON(_jsn, 'ol', obj.oldest)
	obj.latest = INT.getElementJSON(_jsn, 'la', obj.latest)


def _Container_createJSON(obj, isUpdate=False):
	jsn = _resourceBase_createJSON(obj, isUpdate)
	INT.addToElementJSON(jsn, 'mni', obj.maxNrOfInstances)
	INT.addToElementJSON(jsn, 'mbs', obj.maxByteSize)
	INT.addToElementJSON(jsn, 'mia', obj.maxInstanceAge)
	return INT.wrapJSON(obj, jsn)


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
	root = _resourceBase_createXML(obj, isUpdate)
	INT.addToElement(root, 'cnf', obj.contentInfo)
	INT.addToElement(root, 'con', obj.content)
	return root


def _ContentInstance_parseJSON(obj, jsn):
	_jsn = _resourceBase_parseJSON(obj, jsn)
	obj.contentInfo = INT.getElementJSON(_jsn, 'cnf', obj.contentInfo)
	obj.contentSize = INT.getElementJSON(_jsn, 'cs', obj.contentSize)
	obj.content = INT.getElementJSON(_jsn, 'con', obj.content)


def _ContentInstance_createJSON(obj, isUpdate=False):
	jsn = _resourceBase_createJSON(obj, isUpdate)
	INT.addToElementJSON(jsn, 'cnf', obj.contentInfo)
	INT.addToElementJSON(jsn, 'con', obj.content)
	return INT.wrapJSON(obj, jsn)


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
	root = _resourceBase_createXML(obj, isUpdate)
	if obj.maxNrOfMembers and not isUpdate: 	# No mnm when updating
		INT.addToElement(root, 'mnm', obj.maxNrOfMembers)
	INT.addToElement(root, 'mt', obj.memberType)
	INT.addToElement(root, 'mid', obj.memberIDs, mandatory=True)
	if obj.consistencyStrategy and not isUpdate: 	# No csy when updating
		INT.addToElement(root, 'csy', obj.consistencyStrategy)
	INT.addToElement(root, 'gn', obj.groupName)
	return root


def _Group_parseJSON(obj, jsn):
	_jsn = _resourceBase_parseJSON(obj, jsn)
	obj.maxNrOfMembers = INT.getElementJSON(_jsn, 'mnm', obj.maxNrOfMembers)
	obj.memberType = INT.getElementJSON(_jsn, 'mt', obj.memberType)
	obj.currentNrOfMembers = INT.getElementJSON(_jsn, 'cnm', obj.currentNrOfMembers)
	obj.memberIDs = INT.getElementJSON(_jsn, 'mid', obj.memberIDs)
	obj.memberTypeValidated = INT.getElementJSON(_jsn, 'mtv', obj.memberTypeValidated)
	obj.consistencyStrategy = INT.getElementJSON(_jsn, 'csy', obj.consistencyStrategy)
	obj.groupName = INT.getElementJSON(_jsn, 'gn', obj.groupName)
	obj.fanOutPoint = INT.getElementJSON(_jsn, 'fopt', obj.fanOutPoint)


def _Group_createJSON(obj, isUpdate):
	jsn = _resourceBase_createJSON(obj, isUpdate)
	if obj.maxNrOfMembers and not isUpdate: 	# No mnm when updating
		INT.addToElementJSON(jsn, 'mnm', obj.maxNrOfMembers)
	INT.addToElementJSON(jsn, 'mt', obj.memberType)
	INT.addToElementJSON(jsn, 'mid', obj.memberIDs, mandatory=True)
	if obj.consistencyStrategy and not isUpdate: 	# No csy when updating
		INT.addToElementJSON(jsn, 'csy', obj.consistencyStrategy)
	INT.addToElementJSON(jsn, 'gn', obj.groupName)
	return INT.wrapJSON(obj, jsn)



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
	root = _resourceBase_createXML(obj, isUpdate)
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
	_jsn = _resourceBase_parseJSON(obj, jsn)
	obj.notificationURI = INT.getElementJSON(_jsn, 'nu', obj.notificationURI)
	obj.notificationContentType = INT.getElementJSON(_jsn, 'nct', obj.notificationContentType)
	obj.expirationCounter = INT.getElementJSON(_jsn, 'exc', obj.expirationCounter)
	obj.latestNotify = INT.getElementJSON(_jsn, 'ln', obj.latestNotify)
	obj.groupID = INT.getElementJSON(_jsn, 'gpi', obj.groupID)
	obj.notificationForwardingURI = INT.getElementJSON(_jsn, 'nfu', obj.notificationForwardingURI)
	obj.subscriberURI = INT.getElementJSON(_jsn, 'su', obj.subscriberURI)


def _Subscription_createJSON(obj, isUpdate=False):
	jsn = _resourceBase_createJSON(obj, isUpdate)
	INT.addToElementJSON(jsn, 'nu', obj.notificationURI)
	INT.addToElementJSON(jsn, 'nct', obj.notificationContentType)
	if obj.expirationCounter != -1:
		INT.addToElementJSON(jsn, 'exc', obj.expirationCounter)
	if obj.latestNotify:
		INT.addToElementJSON(jsn, 'ln', obj.latestNotify)
	if obj.groupID:
		INT.addToElementJSON(jsn, 'gpi', obj.groupID)
	if obj.notificationForwardingURI:
		INT.addToElementJSON(jsn, 'nfu', obj.notificationForwardingURI)
	if obj.subscriberURI:
		INT.addToElementJSON(jsn, 'su', obj.subscriberURI)
	return INT.wrapJSON(obj, jsn)



###############################################################################
#
#	FlexContainer
#

def _FlexContainer_parseXML(obj, root):
	_resourceBase_parseXML(obj, root)
	obj.contentDefinition = INT.getElement(root, 'cnd', obj.contentDefinition)
	# TODO attributes



def _FlexContainer_createXML(obj, isUpdate=False):
	root = _resourceBase_createXML(obj, isUpdate)
	INT.addToElement(root, 'cnd', obj.contentDefinition)
	# TODO attributes
	return root


def _FlexContainer_parseJSON(obj, jsn):
	_resourceBase_parseJSON(obj, _jsn)
	obj.contentDefinition = INT.getElementJSON(_jsn, 'cnd', obj.contentDefinition)
	# TODO Attributes


def _FlexContainer_createJSON(obj, isUpdate=False):
	jsn = _resourceBase_createJSON(obj, isUpdate)
	INT.addToElementJSON(data, 'cnd', obj.contentDefinition)
	# >TODO attribues
	return INT.wrapJSON(obj, jsn)
