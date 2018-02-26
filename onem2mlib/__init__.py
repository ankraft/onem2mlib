"""
This Python3 module implements a library to access and manage resources on a oneM2M CSE.

(c) 2017 by Andreas Kraft  
Licensed under the BSD 3-Clause License. See the LICENSE file for further details.

"""
import json, uuid

import onem2mlib.constants as CON
import onem2mlib.exceptions
import onem2mlib.utilities as UT
import onem2mlib.marshalling as M
import onem2mlib.mcarequests as MCA
import onem2mlib.internal as INT
import onem2mlib.exceptions as EXC
import onem2mlib.notifications as NOT



__all__ = [	'AccessControlPolicy', 'AccessControlRule', 'AE', 'Container',
			'ContentInstance', 'CSEBase', 'Group', 'RemoteCSE', 'Subscription', 
			'ResourceBase', 'Session',
			'constants', 'exceptions', 'utilities', 'notifications',
			'retrieveResourceFromCSE']


###############################################################################


class Session:
	"""
	A Session object is used when connecting to a oneM2M CSE. It holds various information
	about the current session, such as the CSE endpoint, credentials, desired encoding, etc.
	"""

	def __init__(self, address,  originator, encoding=CON.Encoding_JSON):
		"""
		Initialize a Session object. 

		Please note, the credentials (the originator) are currently hold unsecured in
		Session instances.

		Args:

		- *address*: String. The URL of the CSE host to connect to. This includes the protocol, hostname, 
			port number, and any API prefix etc.
		- *originator*: String. The originator for identification in access control policies.
		- *encoding*: Integer. The encoding of request content. Optional, the default is
			`onem2mlib.constants.Encoding_JSON`. Providing a wrong encoding will throw a `onem2mlib.exceptions.NotSupportedError`
			exception.
		"""
		self.address = address
		""" String. The URL of the CSE host to connect to. The address includes the protocol, hostname, 
			port number, and any API prefix etc. """
		while self.address is not None and self.address.endswith('/'):
			self.address = self.address[:-1]

		self.originator = originator
		""" String. This specifies the originator for identification in access control policies. 
			It can be a domain, an originatorID, the string "all", or a role-ID. """

		self.encoding = encoding
		"""	Integer, either `onem2mlib.constants.Encoding_XML` or `onem2mlib.constants.Encoding_JSON`.
			It specifies the type of encoding for requests between the AE and the CSE. """
		if self.encoding not in [CON.Encoding_XML, CON.Encoding_JSON]:
			raise EXC.NotSupportedError('Unsupported encoding: ' + str(self.encoding))

		if not self.originator:
			raise EXC.AuthenticationError('Missing accessControlOriginator.')


	def __str__(self):
		result = 'Session:\n'
		result += INT.strResource('address', None, self.address)
		result += INT.strResource('originator', None, self.originator)
		result += INT.strResource('encoding', None, self.encoding)
		return result



###############################################################################

class ResourceBase:
	"""
	The ResourceBase is the base class for most of resource classes. It handles the common
	resource attributes.
	"""

	def __init__(self, parent, resourceName, resourceID, type, labels = []):
		"""
		Initialize a ResourceBase instance.

		Args:

		- *parent*: The parent resource object in which the resource
			will be created.
		- All other arguments initialize the status variables of the same name in the
			ResourceBase instance.
		"""		
		self.parent	= parent
		""" Resource instance object. The parent resource of this resource. """

		self.session = None
		""" Session. The Session object of the parent. """
		if parent:
			self.session = parent.session
		
		self.type = type
		""" Integer. The type of the resource. """
		
		self.resourceID	= resourceID
		""" String. The resource ID of the resource. Assigned by the CSE.
			For a &lt;CSEBase> this is the *cseID*.2"""
		
		self.resourceName= resourceName
		""" String. The resource name of the resource. Assigned by the application or the CSE. 
			For a &lt;CSEBase> this is the *cseName*."""
		
		self.parentID = None
		""" String. The resource ID of the parent resource. Assigned by the CSE. """
		
		self.creationTime = None
		""" String. The time of creation of the resource in the CSE. Assigned by the CSE. R/O. """
		
		self.lastModifiedTime = None
		""" String. The time of the last modification of the resource. Assigned by the CSE. R/O. """
		
		self.accessControlPolicyIDs = []
		""" List of String. A list of ACP resources. This might be an empty list."""
		
		self.expirationTime	= None
		""" String. The expiration time of the resource, or None. Assigned by the CSE. R/O. """
		
		self.stateTag = 0
		"""Integer. An incremental counter of modification on the resource. Assigned by the CSE. R/O."""
		
		self.labels = labels
		""" List of String. A list of labels of the resource. This might be an empty list. """
		
		self.dynamicAuthorizationConsultationIDs = []
		""" List of String. A List of dynamic authorization consultation IDs. This might be an empty list. """
		
		self.announceTo = []
		""" List of String. A list of URLs that point to the CSE(s) to which this resource is announced to,
			or an empty list. """
		
		self.announcedAttribute = []
		""" List of String. A list of the announced attribute names of an original resource, 
			or an empty list. """


	def __str__(self):
		result = ''
		result += INT.strResource('type', 'ty', self.type)
		result += INT.strResource('resourceName', 'rn', self.resourceName)
		result += INT.strResource('resourceID', 'ri', self.resourceID)
		result += INT.strResource('parentID', 'pi', self.parentID)
		result += INT.strResource('creationTime', 'ct', self.creationTime)
		result += INT.strResource('lastModifiedTime', 'lt', self.lastModifiedTime)
		result += INT.strResource('stateTag', 'st', self.stateTag)
		result += INT.strResource('labels', 'lbl', self.labels)
		result += INT.strResource('accessControlPolicyIDs', 'acpi', self.accessControlPolicyIDs)
		result += INT.strResource('expirationTime', 'et', self.expirationTime)
		result += INT.strResource('dynamicAuthorizationConsultationIDs', 'daci', self.dynamicAuthorizationConsultationIDs)
		result += INT.strResource('announceTo', 'at', self.announceTo)
		result += INT.strResource('announcedAttribute', 'aa', self.announcedAttribute)
		return result


	def setAccessControlPolicies(self, acps):
		"""
		Set the &lt;ccessControlPolicy> resource ID(s) for a resource (if the resource type supports 
		AccessControlPolicies). 

		*acps* could either be a single *AccessControlPolicies* object or a list of
		*AccessControlPolicy* objects. If *acps* is *None*, then the accessControlPolicies
		of this resource are set to an empty list.

		This method may throw a `onem2mlib.exceptions.NotSupportedError` exception when called on a resource that doesn't
		support accessControlPolicies.
		"""
		self.accessControlPolicyIDs = []

		if isinstance(self, ContentInstance):
			raise EXC.NotSupportedError('Resource does not support AccessControlPolicies.')

		if acps is not None:
			if isinstance(acps, AccessControlPolicy) and acps.resourceID is not None:
				self.accessControlPolicyIDs.append(acps.resourceID)
			else:
				for acp in acps:
					if isinstance(acp, AccessControlPolicy) and acp.resourceID is not None:
						self.accessControlPolicyIDs.append(acp.resourceID)


	def retrieveFromCSE(self):
		"""
		Retrieve the resource from the &lt;CSEBase>. This object instance is updated accordingly. 

		The method returns *True* or *False*, depending on the success of the operation.

		The `onem2mlib.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		return MCA.retrieveFromCSE(self)


	def deleteFromCSE(self):
		"""
		Delete the resource and all its sub-resources from the &lt;CSEBase>. 

		The method returns *True* or *False*, depending on the success of the operation.
		It may throw a `onem2mlib.exceptions.NotSupportedError` exception when the operation is not supported
		by the resource type.

		The `onem2mlib.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		if self.type in [CON.Type_CSEBase, CON.Type_RemoteCSE]: # not allowed
			raise EXC.NotSupportedError('Resource doesn''t support deleting.')
		return MCA.deleteFromCSE(self)


	def createInCSE(self):
		"""
		Create the resource in the &lt;CSEBase>.

		The method returns *True* or *False*, depending on the success of the operation.'
		It may throw a `onem2mlib.exceptions.NotSupportedError` exception when the operation is not supported
		by the resource type.

		The `onem2mlib.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		if self.type in [CON.Type_CSEBase, CON.Type_RemoteCSE]: # not allowed
			raise EXC.NotSupportedError('Resource doesn''t support updating.')
		return MCA.createInCSE(self, self.type)


	def updateInCSE(self):
		"""
		Update the existing resource with new attributes.

		The method returns *True* or *False*, depending on the success of the operation.
		It may throw a `onem2mlib.exceptions.NotSupportedError` exception when the operation is not supported
		by the resource type.

		The `onem2mlib.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		if self.type in [CON.Type_ContentInstance, CON.Type_CSEBase, CON.Type_RemoteCSE]: # not allowed
			raise EXC.NotSupportedError('Resource doesn''t support updating.')
		return MCA.updateInCSE(self, self.type)


	def get(self):
		"""
		Retrieve the resource from the &lt;CSEBase>, or create it if it doesn't exist.
		This object instance is updated accordingly. 

		The method returns *True* or *False*, depending on the success of the operation.

		The `onem2mlib.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		if self.resourceID:
			return self.retrieveFromCSE()
		if self.resourceName:
			if self.retrieveFromCSE():
				return True
		return self.createInCSE()


	def discover(self, filter, filterOperation=CON.Dsc_AND):
		"""
		Discover a rsource on the CSE, starting with the resource as a root for
		discovery.

		Args:

		- *filter*: A list of *filterCriteria*. These critera can be constructed using the
		*onem2mlib.utilties.new...FilterCriteria* functions.
		- *filterOperation*. A boolean value that Indicates the logical operation (AND/OR) 
		to be used for different condition tags. The default value is logical AND.

		The method returns a list of found resources, or an empty list.

		**Note**

		Currently, only *label* and *resoureType* are supported in filters.
		"""
		rids = MCA.discoverInCSE(self, filter=filter, filterOperation=filterOperation)
		if rids is None:
			return []
		return [ retrieveResourceFromCSE(self, id) for id in rids ]


	def subscribe(self, callback=None):
		"""
		Create a &lt;subscription> to resource and receive notifications. For this, the notification
		sub-module must be enabled, ie. `onem2mlib.notifications.setupNotifications`() must have
		been called sucessfully. To stop notification from the resource and to remove the
		subscription, the `onem2mlib.ResourceBase.unsubscribe`() method must be called.

		This method might throw	a `onem2mlib.exceptions.NotSupportedError` exception in case
		the target resource type doesn't support subscriptions.

		Args:

		- *callback*: An optional reference to a callback functions that is called when a
		notification is received for the subscription. If this argument is ommitted then the
		default callback function, provided with `onem2mlib.notifications.setupNotifiations`(),
		is called instead.

		The method returns a Boolean indicating whether the subscription was successfull.

		**Note**

		The &lt;subsription> resource created with this method is only valid for the
		runtime of the calling program. The scubscription will be removed at least when the
		program terminates, or when `onem2mlib.notifications.shutdownNotifications`() is called.

		"""
		if self.type not in NOT._allowedSubscriptionResources:
			raise EXC.NotSupportedError('Subscription not supported for this resource type')
		if not NOT.isNotificationEnabled():
			return False
		return NOT.addSubscription(self, callback)


	def unsubscribe(self):
		"""
		Unsubscripte from the notifications of a resource. The subscription must have
		been created before with the `onem2mlib.ResourceBase.subscribe`() method.

		This method might throw	a `onem2mlib.exceptions.NotSupportedError` exception in case
		the target resource type doesn't support subscriptions.

		The method returns a Boolean indicating whether the subscription was successfull.
		"""
		if self.type not in NOT._subscriptionResources:
			raise EXC.NotSupportedError('Subscription not supported for this resource type')
		return NOT.removeSubscription(self)


	def subscriptions(self):
		"""
		Return a list of &lt;subscription> resources of a rersource, or an empty list.

		This method might throw	a `onem2mlib.exceptions.NotSupportedError` exception in case
		the target resource type doesn't support subscriptions.
		"""
		if self.type not in NOT._allowedSubscriptionResources:
			raise EXC.NotSupportedError('Subscription not supported for this resource type')
		return INT._findSubResource(self, CON.Type_Subscription)


	def findSubscription(self, resourceName):
		"""
		Find a specific &lt;subscription> resource by its *resourceName*, or None otherwise.

		This method might throw	a `onem2mlib.exceptions.NotSupportedError` exception in case
		the target resource type doesn't support subscriptions.
		"""
		return INT._getResourceFromCSEByResourceName(CON.Type_Subscription, resourceName, self)


	# Recursivly construct a structured resourceName
	def _structuredResourceID(self):
		if self.type == CON.Type_CSEBase:		# CSEBase means end of recursion
			if self.resourceID.startswith('/'):	# special handling for CSE ID's that start with a /
				return self.resourceID + '/' + self.resourceName
			return '/' + self.resourceID + '/' + self.resourceName
		return self.parent._structuredResourceID() + '/' + self.resourceName


	def _parseResponse(self, response):
		#print(response.text)
		if self.session.encoding == CON.Encoding_XML:
			return self._parseXML(INT.responseToXML(response))
		elif self.session.encoding == CON.Encoding_JSON:
			return self._parseJSON(response.json())
		raise EXC.NotSupportedError('Encoding not supported: ' + str(self.session.encoding))


	def _createContent(self, isUpdate=False):
		if self.session.encoding == CON.Encoding_XML:
			return INT.xmlToString(self._createXML(isUpdate))
		elif self.session.encoding == CON.Encoding_JSON:
			return json.dumps(self._createJSON(isUpdate))
		raise EXC.NotSupportedError('Encoding not supported: ' + str(self.session.encoding))


	def _copy(self, resource):
		self.resourceName = resource.resourceName
		self.type = resource.type
		self.stateTag = resource.stateTag
		self.labels = resource.labels
		self.resourceID = resource.resourceID
		self.parentID = resource.parentID
		self.creationTime = resource.creationTime
		self.lastModifiedTime = resource.lastModifiedTime
		self.accessControlPolicyIDs = resource.accessControlPolicyIDs
		self.expirationTime = resource.expirationTime
		self.announceTo = resource.announceTo
		self.announcedAttribute = resource.announcedAttribute



###############################################################################

class CSEBase(ResourceBase):
	"""
	CSEBase holds the attributes of a CSE and gives access to resources under it.

	When created and initialized correctly, it is automatically retrieved from the
	CSE immediatly.
	"""

	def __init__(self, session=None, cseID=None, resourceName=None, instantly=True):
		"""
		Initialize a CSEBase object.

		Args:

		- *session*: A `onem2mlib.Session` object that holds the information to connect to a CSE.
		- *cseid*: The CSE-ID of the CSE.

		Internally, the *cseID* is assigned to the `onem2mlib.ResourceBase.resourceID` attribute, and the *csename* is handled
		by the *resourceName*. 
		"""
		super().__init__(None, resourceName, cseID, CON.Type_CSEBase)

		self.session = session # Must assign session manually.
		
		self.cseType = None
		""" Integer. The type of the CSE. See also the `Constants.CSE_Type_*` constants.
			Assigned by the CSE. R/O."""
		
		self.supportedResourceTypes = []
		""" List of String. A list of supported resource types of this CSE.	Assigned by the CSE. R/O. """
		
		self.pointOfAccess = []
		""" List of String. A list of physical addresses to be used by remote CSEs to connect to this CSE.
			Assigned by the CSE. R/O. """

		if instantly:
			if not self.retrieveFromCSE():
				raise EXC.CSEOperationError('Cannot get CSEBase. ' + MCA.lastError)


	def __str__(self):
		result = 'CSEBase:\n'
		result += super().__str__()
		result += INT.strResource('cseType', 'cst', self.cseType)
		result += INT.strResource('supportedResourceTypes', 'srt', self.supportedResourceTypes)
		result += INT.strResource('pointOfAccess', 'poa', self.pointOfAccess)
		return result


	def accessControlPolicies(self):
		"""
		Return a list of &lt;accessControlPolicy> resources from this CSE, or an empty list.
		"""
		return INT._findSubResource(self, CON.Type_ACP)


	def findAccessControlPolicy(self, resourceName):
		"""
		Find a specific &lt;accessControlPolicy> resource by its *resourceName*, or None.
		"""
		return INT._getResourceFromCSEByResourceName(CON.Type_ACP, resourceName, self)


	def aes(self):
		"""
		Return a list of &lt;AE> resources from this CSE, or an empty list.
		"""
		return INT._findSubResource(self, CON.Type_AE)


	def findAE(self, resourceName):
		"""
		Find a specific &lt;AE> resource by its *resourceName*, or None otherwise.
		"""
		return INT._getResourceFromCSEByResourceName(CON.Type_AE, resourceName, self)


	def addAE(self, resourceName=None, appID=None, AEID=None, resourceID=None, requestReachability=True, labels=[]):
		"""
		Add a new AE. This is a convenience function that actually creates a new
		&lt;AE> resource in the &lt;CSEBase>. It returns the new
		*AE* object, or None.
		"""
		return AE(self, resourceName, appID, AEID, resourceID, requestReachability, labels)


	def containers(self):
		"""
		Return a list of all &lt;container> resources of this &lt;CSEBase>, or an empty list.
		"""
		return INT._findSubResource(self, CON.Type_Container)


	def findContainer(self, resourceName):
		"""
		Find a &lt;container> resource by its *resourceName*, or None.
		"""
		return INT._getResourceFromCSEByResourceName(CON.Type_Container, resourceName, self)


	def addContainer(self, resourceName=None, maxNrOfInstances=None, maxByteSize=None, maxInstanceAge=None, labels=[]):
		"""
		Add a new container. This is a convenience function that actually creates a new
		&lt;container> resource in the &lt;CSEBase>. It returns the new
		*Container* object, or None.
		"""
		return Container(self, resourceName, maxNrOfInstances, maxByteSize, maxInstanceAge, labels)


	def groups(self):
		"""
		Return a list of &lt;group> resources from this CSE, or an empty list.
		"""
		return INT._findSubResource(self, CON.Type_Group)


	def findGroup(self, resourceName):
		"""
		Find a specific &lt;group> resource by its *resourceName*, or None.
		"""
		return INT._getResourceFromCSEByResourceName(CON.Type_Group, resourceName, self)


	def addGroup(self, resourceName=None, resources=[], maxNrOfMembers=CON.Grp_def_maxNrOfMembers, consistencyStrategy=CON.Grp_ABANDON_MEMBER, groupName=None, labels = [], instantly=True):
		"""
		Add a new group. This is a convenience function that actually creates a new
		&lt;group> resource in the &lt;CSEBase>. It returns the new
		*Group* object, or None.
		"""
		return Group(self, resourceName=resourceName, resources=resources, maxNrOfMembers=maxNrOfMembers, consistencyStrategy=consistencyStrategy, groupName=groupName, labels=labels)


	def remoteCSEs(self):
		"""
		Return a list of &lt;remoteCSE> resources from this CSE, or an empty list.
		"""
		return INT._findSubResource(self, CON.Type_RemoteCSE)


	def findRemoteCSE(self, resourceName):
		"""
		Find a specific &lt;remoteCSE> resource by its *resourceName*, or None.
		"""
		return INT._getResourceFromCSEByResourceName(CON.Type_RemoteCSE, resourceName, self)


	def _parseXML(self, root):
		M._CSEBase_parseXML(self, root)


	def _parseJSON(self, jsn):
		M._CSEBase_parseJSON(self, jsn)


	def _copy(self, resource):
		super()._copy(resource)
		self.cseType = resource.cseType
		self.supportedResourceTypes = resource.supportedResourceTypes
		self.pointOfAccess = self.pointOfAccess


###############################################################################

class RemoteCSE(ResourceBase):
	"""
	This class implements the oneM2M &lt;remoteCSE> resource. 

	It is  a sub-resource of the &lt;CSEBase> resource, and it represents and grants access to a
	remote CSE.
	"""
	def __init__(self, parent=None, resourceName=None, resourceID=None, requestReachability=None, instantly=True):
	
		"""
		Initialize a RemoteCSE object.
		Usually, objects of this class are created only by the onem2m lib..

		Args:

		- *parent*: The parent resource object in which the &lt;remoteCSE> resource
			will be created. This must be a &lt;CSEBase>. This might throw a *ParameterError*
			exception if this is not the case.
		- *instantly*: The resource will be instantly retrieved from the CSE. This might throw
			a *CSEOperationError* exception in case of an error.
		- All other arguments initialize the status variables of the same name in the
			&lt;remoteCSE> instance or `onem2mlib.ResourceBase`.
		"""
		super().__init__(parent, resourceName, resourceID, CON.Type_RemoteCSE)
		if parent is not None and parent.type != CON.Type_CSEBase and parent.type != CON.Type_RemoteCSE:
			raise EXC.ParameterError('Parent must be <CSE> or <remoteCSE>.')

		self.pointOfAccess = []
		""" List of String. A list of physical addresses to be used by remote CSEs to connect to this CSE.
			Assigned by the CSE. R/O. """

		self.cseBase = None
		""" URI. The address of the CSEBase resource represented by this &lt;remoteCSE> resource. """

		self.cseID = None
		""" String. The CSE identifier of a remote CSE in SP-relative CSE-ID format. """

		self.requestReachability = requestReachability
		""" Boolean. This indicates the reachability of the RemoteCSE. Assigned by the application or the CSE. """

		if instantly:
			if not self.get():
				raise EXC.CSEOperationError('Cannot get remoteCSE.' + MCA.lastError)


	def __str__(self):
		result = 'RemoteCSE:\n'
		result += super().__str__()
		result += INT.strResource('requestReachability', 'rr', self.requestReachability)
		result += INT.strResource('pointOfAccess', 'poa', self.pointOfAccess)
		result += INT.strResource('CSEBase', 'cb', self.cseBase)
		result += INT.strResource('cse-ID', 'csi', self.cseID)
		return result


	def cseFromLocalCSE(self, instantly=True):
		"""
		Return a `onem2mlib.CSEBase` resource instance that grants access to the remote CSE via the local
		(the CSE from which this &lt;RemoteCSE> resource originates). This means, that all requests to the
		remote CSE are routed through the local CSE.

		Args:

		- *instantly*: The CSE resource will be instantly retrieved from the CSE. This might throw
			a *CSEOperationError* exception in case of an error.
		"""
		return CSEBase(self.session, self.cseID, self.resourceName, instantly=instantly)


	def cseFromRemoteCSE(self, session=None, instantly=True):
		"""
		Return a `onem2mlib.CSEBase` resource instance that grants direct access to the remote CSE.
		This means, that all requests to the remote CSE are directly targeting the remote CSE.

		This might throw a *CSEOperationError* exception if there is a problem with missing or wrong
		parameters for the remote CSE.

		Args:

		- *session*: Optionally provide a `onem2mlib.Session` instance to use for the remote CSE.
			Otherwise the current Session instance is used.
		- *instantly*: The CSE resource will be instantly retrieved from the CSE. This might throw
			a *CSEOperationError* exception in case of an error.
		"""
		if self.pointOfAccess == None or len(self.pointOfAccess) == 0:
			raise EXC.CSEOperationError('Missing PointOfAccess of remote CSE.')

		if session is None:
			nSession = Session(self.pointOfAccess[0], self.session.originator, self.session.encoding)
		else:
			nSession = Session(self.pointOfAccess[0], session.originator, session.encoding)
		return CSEBase(nSession, self.cseID, instantly=instantly)


	def _parseXML(self, root):
		M._remoteCSE_parseXML(self, root)


	def _parseJSON(self, jsn):
		M._remoteCSE_parseJSON(self, jsn)


	def _copy(self, resource):
		super()._copy(resource)
		self.cseBase = resource.cseBase
		self.cseID = resource.cseID
		self.pointOfAccess = resource.pointOfAccess
		self.requestReachability = resource.requestReachability


# README






###############################################################################

class AccessControlPolicy(ResourceBase):
	"""
	This class implements the oneM2M &lt;accessControlPolicy> resource. 

	It is always a sub-resource of a &lt;CSEBase> or a &lt;remoteCSE> resource, and it contains access right
	privileges to resources.

	**Note**: Delete associated resources first before deleting the	&lt;accessControlPolicy> resource.
	"""

	def __init__(self, parent=None, resourceName=None, resourceID=None, privileges = [], selfPrivileges=[], instantly=True):
		"""
		Initialize the &lt;accessControlPolicy> resource. 

		Args:

		- *parent*: The parent resource object in which the &lt;accessControlPolicy> resource
			will be created. This must be a &lt;CSEBase> or &lt;remoteCSE> resource. This might throw a
			*ParameterError* exception if this is not the case.
		- *instantly*: The resource will be instantly retrieved from or created on the CSE. This might throw
			a *CSEOperationError* exception in case of an error.
		- All other arguments initialize the status variables of the same name in the
			&lt;accessControlPolicy> instance or `onem2mlib.ResourceBase`.
		"""
		super().__init__(parent, resourceName, resourceID, CON.Type_ACP)
		if parent is not None and parent.type != CON.Type_CSEBase and parent.type != CON.Type_RemoteCSE:
			raise EXC.ParameterError('Parent must be <CSE> or <remoteCSE>.')

		self.privileges = privileges
		""" A list of *AccessControlRules* that applies to resources referencing this 
		&lt;accessControlPolicy> resource using the accessControlPolicyID attribute. """
		
		self.selfPrivileges = selfPrivileges
		""" A list of *AccessControlRules* that apply to the &lt;accessControlPolicy> resource itself. """

		if instantly:
			if not self.get():
				raise EXC.CSEOperationError('Cannot get or create ACP. ' + MCA.lastError)


	def __str__(self):
		result = 'ACP:\n'
		result += super().__str__()
		result += '\tPrivileges:\n'
		for p in self.privileges:
			result += str(p)
		result += '\tSelfPrivileges:\n'
		for p in self.selfPrivileges:
			result += str(p)
		return result


	def _parseXML(self, root):
		M._accessControlPolicy_parseXML(self, root)


	def _parseJSON(self, jsn):
		M._accessControlPolicy_parseJSON(self, jsn)


	def _createXML(self, isUpdate=False):
		return M._accessControlPolicy_createXML(self, isUpdate)


	def _createJSON(self, isUpdate=False):
		return M._accessControlPolicy_createJSON(self, isUpdate)


	def _copy(self, resource):
		super()._copy(resource)
		self.privileges = resource.privileges
		self.selfPrivileges = resource.selfPrivileges


class AccessControlRule():
	"""
	This class provides the structure for access control rules that shall be used to define
	privileges in &lt;accessControlPolicy> resources. It contains:

	- *accessControlOriginators* : The accessControlOriginators is a mandatory parameter in an
		AccessControlRule. It represents the list of Originators that shall be allowed to use
		an access control rule. The list of Originators is described as a list of parameters, where the
		types of the parameter can vary within the list.
		See also table Table 9.6.2.1-1 of oneM2M's TS-0001.
	- *accessControlOperations* : The accessControlOperations is a mandatory parameter in an
		AccessControlRule structure that represents the set of operations that are authorized
		using this access control rule.
	"""

	def __init__(self, accessControlOriginators=[], accessControlOperations=0):
		"""
		Initialize the AccessControlRule. 

		Args:

		- *accessControlOriginators*: A list of originators.
		- *accessControlOperations*: The combination of operation privileges.
		"""

		self.accessControlOriginators = accessControlOriginators
		""" List of string. This attribute specifies the list of originators. R/W. """
		
		self.accessControlOperations = accessControlOperations
		""" Integer. This attribute is an OR'ed combination of the operation privileges for this AccessControlRule. R/W. """

	def __str__(self):
		result =  '\t  accessControlRule(acr):\n'
		result += INT.strResource('    ' + 'accessControlOriginators', 'acor', self.accessControlOriginators)
		result += INT.strResource('    ' + 'accessControlOperations', 'acop', self.accessControlOperations)
		return result


	def _parseXML(self, root):
		M._accessControlRule_parseXML(self, root)


	def _createXML(self, root):
		M._accessControlRule_createXML(self, root)


	def _parseJSON(self, jsn):
		M._accessControlRule_parseJSON(self, jsn)


	def _createJSON(self):
		return M._accessControlRule_createJSON(self)


###############################################################################


class AE(ResourceBase):
	"""
	This class implements the oneM2M &lt;AE> resource. 

	It is usually a sub-resource of the &lt;CSEBase> resource, and it represents an 
	application and the sub-structure of resources beneath it.
	"""

	def __init__(self, parent=None, resourceName=None, appID=None, AEID=None, resourceID=None, requestReachability=True, labels=[], instantly=True):
		"""
		Initialize the &lt;AE> resource. 

		Args:

		- *parent*: The parent resource object in which the &lt;AE> resource
			will be created.
		- *instantly*: The resource will be instantly retrieved from or created on the CSE. This might throw
			a `onem2mlib.exceptions.CSEOperationError` exception in case of an error.
		- All other arguments initialize the status variables of the same name in the
			&lt;AE> instance or `onem2mlib.ResourceBase`.
		"""
		super().__init__(parent, resourceName, resourceID, CON.Type_AE, labels=labels)

		self.appID = appID
		""" String. The identifier of the Application. Assigned by the application or the CSE. """
		if not self.appID:
			self.appID = self.resourceName

		self.AEID = AEID
		""" String. The identifier of the Application Entity. Assigned by the application or the CSE. """

		self.requestReachability = requestReachability
		""" Boolean. This indicates the reachability of the AE.	Assigned by the application or the CSE. """

		self.pointOfAccess = []
		""" List of String. The list of addresses for communicating with the registered AE. """

		if instantly:
			if not self.get():
				EXC.CSEOperationError('Cannot get or create AE. '  + MCA.lastError)


	def __str__(self):
		result = 'AE:\n'
		result += super().__str__()
		result += INT.strResource('appID', 'api', self.appID)
		result += INT.strResource('AEID', 'aei', self.AEID)
		result += INT.strResource('requestReachability', 'rr', self.requestReachability)
		result += INT.strResource('pointOfAccess', 'poa', self.pointOfAccess)
		return result


	def containers(self):
		"""
		Return a list of all &lt;container> resources of this &lt;AE>, or an empty list.
		"""
		return INT._findSubResource(self, CON.Type_Container)


	def findContainer(self, resourceName):
		"""
		Find a &lt;container> resource by its *resourceName*, or None.
		"""
		return INT._getResourceFromCSEByResourceName(CON.Type_Container, resourceName, self)



	def addContainer(self, resourceName=None, maxNrOfInstances=None, maxByteSize=None, maxInstanceAge=None, labels=[]):
		"""
		Add a new container. This is a convenience function that actually creates a new
		&lt;container> resource in the &lt;AE>. It returns the new
		*Container* object, or None.
		"""
		return Container(self, resourceName, maxNrOfInstances, maxByteSize, maxInstanceAge, labels)


	# def flexContainers(self):
	# 	"""
	# 	Return a list of all &lt;flexContainer> resources of this &lt;AE>, or an empty list.
	# 	"""
	# 	return _findSubResource(self, CON.Type_FlexContainer)


	# def findFlexContainer(self, resourceName):
	# 	"""
	# 	Find a &lt;flexContainer> resource by its *resourceName*, or None.
	# 	"""
	# 	return _getResourceFromCSEByResourceName(CON.Type_FlexContainer, resourceName, self)


	def groups(self):
		"""
		Return a list of all &lt;group> resources of this &lt;AE>, or an empty list.
		"""
		return INT._findSubResource(self, CON.Type_Group)


	def findGroup(self, resourceName):
		"""
		Find a specific &lt;group> resource by its *resourceName*, or None.
		"""
		return INT._getResourceFromCSEByResourceName(CON.Type_Group, resourceName, self)


	def addGroup(self, resourceName=None, resources=[], maxNrOfMembers=CON.Grp_def_maxNrOfMembers, consistencyStrategy=CON.Grp_ABANDON_MEMBER, groupName=None, labels = [], instantly=True):
		"""
		Add a new group. This is a convenience function that actually creates a new
		&lt;group> resource in the &lt;AE>. It returns the new
		*Group* object, or None.
		"""
		return Group(self, resourceName=resourceName, resources=resources, maxNrOfMembers=maxNrOfMembers, consistencyStrategy=consistencyStrategy, groupName=groupName, labels=labels)


	def _parseXML(self, root):
		M._AE_parseXML(self, root)


	def _createXML(self, isUpdate=False):
		return M._AE_createXML(self, isUpdate)


	def _parseJSON(self, jsn):
		M._AE_parseJSON(self, jsn)


	def _createJSON(self, isUpdate=False):
		return M._AE_createJSON(self, isUpdate)


	def _copy(self, resource):
		super()._copy(resource)
		self.appID = resource.appID
		self.AEID = resource.AEID
		self.requestReachability = resource.requestReachability
		self.pointOfAccess = resource.pointOfAccess


###############################################################################


class Container(ResourceBase):
	"""
	This class implements the oneM2M &lt;container> resource. 

	It is usually a sub-resource of the &lt;AE> or other resources.
	"""

	def __init__(self, parent=None, resourceName=None, resourceID=None, maxNrOfInstances=None, maxByteSize=None, maxInstanceAge=None, labels=[], instantly=True):
		"""
		Initialize the &lt;container> resource. 

		Args:

		- *parent*: The parent resource object in which the &lt;container> resource
			will be created.
		- *instantly*: The resource will be instantly retrieved from or created on the CSE. This might throw
			a `onem2mlib.exceptions.CSEOperationError` exception in case of an error.
		- All other arguments initialize the status variables of the same name in the
			&lt;container> instance or `onem2mlib.ResourceBase`.
		"""	
		super().__init__(parent, resourceName, resourceID, CON.Type_Container, labels=labels)

		self.maxNrOfInstances = maxNrOfInstances
		""" Integer. Maximum number of direct child &lt;contentInstance> resources in the 
		&lt;container> resource."""

		self.maxByteSize = maxByteSize
		""" Integer. Maximum size in bytes of data (i.e. content attribute of a &lt;contentInstance>
		resource) that is allocated for the &lt;container> resource for all direct child 
		&lt;contentInstance> resources in the &lt;container> resource."""

		self.maxInstanceAge = maxInstanceAge
		""" Integer.Maximum age of a direct child &lt;contentInstance> resource in the &lt;container>
		resource. The value is expressed in seconds. R/O."""

		self.currentNrOfInstances = None
		""" Integer. Current number of direct child &lt;contentInstance> resource in the &lt;container> 
		resource. It is limited by the `onem2mlib.Container.maxNrOfInstances` property. R/O."""
		
		self.currentByteSize = None
		""" Integer. Current size in bytes of data (i.e. content attribute of a &lt;contentInstance>
		resource) stored in all direct child <contentInstance> resources of a &lt;container> resource.
		This is the summation of contentSize attribute values of the &lt;contentInstance> resources. 
		It is limited by the `onem2mlib.Container.maxByteSize` property. R/O."""

		self.oldest = None
		""" String. The resourceID of the oldest &lt;contentInstance> resource in this &lt;container>
		resource. R/O. """

		self.latest = None
		""" String. The resourceID of the latest (newest) &lt;contentInstance> resource in this 
		&lt;container>. R/O. """

		if instantly:
			if not self.get():
				raise EXC.CSEOperationError('Cannot get or create Container. '  + MCA.lastError)


	def __str__(self):
		result = 'Container:\n'
		result += super().__str__()
		result += INT.strResource('maxNrOfInstances', 'mni', self.maxNrOfInstances)
		result += INT.strResource('maxByteSize', 'mbs', self.maxByteSize)
		result += INT.strResource('maxInstanceAge', 'mia', self.maxInstanceAge)
		result += INT.strResource('currentNrOfInstances', 'cni', self.currentNrOfInstances)
		result += INT.strResource('currentByteSize', 'cbs', self.currentByteSize)
		result += INT.strResource('oldest', 'ol', self.oldest)
		result += INT.strResource('latest', 'la', self.latest)
		return result


	def containers(self):
		"""
		Return all &lt;container> sub-resources from this container, or an empty list.
		"""
		return INT._findSubResource(self, CON.Type_Container)


	def findContainer(self, resourceName):
		"""
		Find a &lt;container> resource by its *resourceName*, or None.
		"""
		return INT._getResourceFromCSEByResourceName(CON.Type_Container, resourceName, self)


	def addContainer(self, resourceName=None, maxNrOfInstances=None, maxByteSize=None, maxInstanceAge=None, labels=[]):
		"""
		Add a new container. This is a convenience function that actually creates a new
		&lt;container> resource in the &lt;container>. It returns the new
		*Container* object, or None.
		"""
		return Container(self, resourceName, maxNrOfInstances, maxByteSize, maxInstanceAge, labels)


	def contentInstances(self):
		"""
		Return all &lt;contentInstance> sub-resources from this container, or an empty list.
		"""
		return INT._findSubResource(self, CON.Type_ContentInstance)


	def findContentInstance(self, resourceName):
		"""
		Find a &lt;ContentInstance> resource by its *resourceName*, or None.
		"""
		return INT._getResourceFromCSEByResourceName(CON.Type_ContentInstance, resourceName, self)


	def contents(self):
		"""
		Return all content from all &lt;contentInstance>'s in list, or an empty list.
		"""
		return [cin.content for cin in self.contentInstances()]


	def addContent(self, value, labels=[]):
		"""
		Add a new value to a container. The value is automatically converted to its string
		representation.
		This is a convenience function that actually creates a new&lt;contentInstance> resource
		for that value in the &lt;container>. returns the new *ContentInstance* object, or None.
		"""
		if not isinstance(value, str):
			value = str(value)
		return ContentInstance(self, content=value, labels=labels)


	def latestContentInstance(self):
		"""
		Return the latest (newest) &lt;contentInstance> sub-resource from this container, or None.
		"""
		return self._getContentInstance(self.latest)


	def oldestContentInstance(self):
		"""
		Return the oldest &lt;contentInstance> sub-resource from this container, or None.
		"""
		return self._getContentInstance(self.oldest)


	def latestContent(self):
		"""
		Return the value of the latest (newest) &lt;contentInstance> sub-resource from this container, or None.
		This is a convenience function to access content values. It actually retrieves the latest &lt;contentInsnace>
		resource from a CSE.
		"""
		cin = self.latestContentInstance()
		if cin:
			return cin.content
		return None


	def oldestContent(self):
		"""
		Return the value of the oldest &lt;contentInstance> sub-resource from this container, or None.
		This is a convenience function to access content values. It actually retrieves the oldest &lt;contentInsnace>
		resource from a CSE.
		"""
		cin = self.oldestContentInstance()
		if cin:
			return cin.content
		return None


	def _getContentInstance(self, path):
		if not self.session or not path: return None
		response = MCA.get(self.session, path)
		if response and response.status_code == 200:
			contentInstance = ContentInstance(self, instantly=False)
			contentInstance._parseResponse(response)
			return contentInstance
		return None


	def _parseXML(self, root):
		M._Container_parseXML(self, root)


	def _createXML(self, isUpdate=False):
		return M._Container_createXML(self, isUpdate)


	def _parseJSON(self, jsn):
		M._Container_parseJSON(self, jsn)


	def _createJSON(self, isUpdate=False):
		return M._Container_createJSON(self, isUpdate)


	def _copy(self, resource):
		super()._copy(resource)
		self.maxNrOfInstances = resource.maxNrOfInstances
		self.maxByteSize = resource.maxByteSize
		self.maxInstanceAge = resource.maxInstanceAge
		self.currentNrOfInstances = resource.currentNrOfInstances
		self.currentByteSize = resource.currentByteSize
		self.oldest = resource.oldest
		self.latest = resource.latest


###############################################################################


class ContentInstance(ResourceBase):
	"""
	This class implements the oneM2M &lt;contentInstance> resource. This type of resource can
	only be created or deleted, but not updated.

	It is usually a sub-resource of the &lt;container> resource.

	To publish data in a &lt;contentInstance> resource, one must first encode the data so 
	that it	can be transfered as a string value and must then  set the encoding type in the 
	`onem2mlib.ContentInstance.contentInfo` state variable. The default is 
	`text/plain:0`. See also the oneM2M specification for further details.

	To retrieve the actual content value of the resource 
	(from `onem2mlib.ContentInstance.content`) one must first check the 
	`onem2mlib.ContentInstance.contentInfo` state variable to determine the
	type of the content and decode it accordingly.
	"""


	def __init__(self, parent=None, resourceName=None, content=None, contentInfo=None, resourceID=None, labels = [], instantly=True):
		"""
		Initialize the &lt;contentInstance> resource. 

		Args:

		- *parent*: The parent resource object in which the &lt;contentInstance> resource
			will be created.
		- *instantly*: The resource will be instantly retrieved from or created on the CSE. This might throw
			a `onem2mlib.exceptions.CSEOperationError` exception in case of an error.
		- All other arguments initialize the status variables of the same name in
			&lt;contentInstance> instance or `onem2mlib.ResourceBase`.
		"""
		super().__init__(parent, resourceName, resourceID, CON.Type_ContentInstance, labels=labels)

		self.contentInfo = contentInfo
		""" String. The type of the data in the `onem2mlib.ContentInstance.content` 
		state variable."""

		self.contentSize = 0
		""" String. The size of the data in the `onem2mlib.ContentInstance.content` 
		state variable. R/O."""

		self.content = content
		""" Usually an encoded String. The actual content of the &lt;contentInstance> resource."""

		if instantly:
			if not self.get():
				raise EXC.CSEOperationError('Cannot get or create ContentInstance. '  + MCA.lastError)


	def __str__(self):
		result = 'ContentInstance:\n'
		result += super().__str__()
		result += INT.strResource('contentInfo', 'cnf', self.contentInfo)
		result += INT.strResource('contentSize', 'cs', self.contentSize)
		result += INT.strResource('content', 'con', self.content)
		return result


	def _parseXML(self, root):
		M._ContentInstance_parseXML(self, root)


	def _createXML(self, isUpdate=False):
		return M._ContentInstance_createXML(self, isUpdate)


	def _parseJSON(self, jsn):
		M._ContentInstance_parseJSON(self, jsn)


	def _createJSON(self, isUpdate=False):
		return M._ContentInstance_createJSON(self, isUpdate)


	def _copy(self, resource):
		super()._copy(resource)
		self.contentInfo = resource.contentInfo
		self.contentSize = resource.contentSize
		self.content = resource.content


###############################################################################


class Group(ResourceBase):
	"""
	This class implements the oneM2M &lt;group> resource. 

	The &lt;group> resource represents a group of resources of the same or mixed types. 
	The &lt;group> resource can be used to do bulk manipulations on the resources represented by the
	`onem2mlib.Group.memberIDs` attribute. The &lt;group> resource contains an attribute that represents the members of 
	the group and the &lt;fanOutPoint> virtual resource that enables generic operations to be applied 
	to all the resources represented by those members.
	"""
	def __init__(self, parent=None, resourceName=None, resourceID=None, resources=[], maxNrOfMembers=CON.Grp_def_maxNrOfMembers, consistencyStrategy=CON.Grp_ABANDON_MEMBER, groupName=None, labels = [], instantly=True):
		"""
		Initialize the &lt;group> resource. 

		Args:

		- *parent*: The parent resource object in which the &lt;group> resource
			will be created.
		- *instantly*: The resource will be instantly retrieved from or created on the CSE. This might throw
			a `onem2mlib.exceptions.CSEOperationError` exception in case of an error.
		- All other arguments initialize the status variables of the same name in
			&lt;group> instance or `onem2mlib.ResourceBase`.
		"""		
		super().__init__(parent, resourceName, resourceID, CON.Type_Group, labels=labels)

		self.maxNrOfMembers = maxNrOfMembers
		""" Integer. Maximum number of members in the &lt;group>. """

		self.resources = resources
		""" List of resource instances. The resources in this &lt;group>. """
		
		self.currentNrOfMembers = len(resources)
		""" Integer. Current number of members in a &lt;group>. It shall not be larger than 
		`onem2mlib.Group.maxNrOfMembers`. R/O. """
		
		self.memberTypeValidated = None
		""" Boolean, or None. Denotes if the resource types of all members resources 
		of the &lt;group> has been validated by the Hosting CSE. In the case that the `onem2mlib.Group.memberType` 
		attribute of the &lt;group> resource is not 'mixed', then this attribute shall be set. """

		self.consistencyStrategy = consistencyStrategy
		""" Integer. This attribute determines how to deal with the &lt;group> resource if the `onem2mlib.Group.memberType`
		validation fails. Its possible values (from the `onem2mlib.constants` sub-module) are

		- *Grp_ABANDON_MEMBER* : delete the inconsistent member
		- *Grp_ABANDON_GROUP* : delete the group
		- *Grp_SET_MIXED* : set the *memberType* to "mixed"

		The default is *Grp_ABANDON_MEMBER*. """
		
		self.groupName = groupName
		""" String. Human readable name of the &lt;group>. """

		self.fanOutPoint = None
		""" String. The resourceID of the virtial &lt;fanOutPoint> resource. Whenever a request is sent 
		to the &lt;fanOutPoint> resource, the request is fanned out to each of the members of the
		&lt;group> resource indicated by the `onem2mlib.Group.memberIDs` attribute of the &lt;group> resource. R/O. """

		# Find the common type, or mixed
		t = -1
		for res in self.resources:
			if res.type != t:
				if t == -1:
					t = res.type
				else:
					t = CON.Type_Mixed
					break
		if t == -1:
			t = CON.Type_Mixed
		
		self.memberType = t
		""" Integer. This is the resource type of the member resources of the group, if all member
		resources (including the member resources in any sub-groups) are of the same type.
		Otherwise, it is of type 'mixed'. W/O. """

		# assign the resource ids
		self.memberIDs = [ res.resourceID for res in self.resources ]
		""" List String, member resource IDs. Each memberID should refer to a member resource or a 
		(sub-) &lt;group> resource of the &lt;group>. """

		if instantly:
			if not self.get():
				raise EXC.CSEOperationError('Cannot get or create Group. '  + MCA.lastError)


	def __str__(self):
		result = 'Group:\n'
		result += super().__str__()
		result += INT.strResource('maxNrOfMembers', 'mnm', self.maxNrOfMembers)
		result += INT.strResource('memberType', 'mt', self.memberType)
		result += INT.strResource('currentNrOfMembers', 'cnm', self.currentNrOfMembers)
		result += INT.strResource('memberIDs', 'mid', self.memberIDs)
		result += INT.strResource('memberTypeValidated', 'mtv', self.memberTypeValidated)
		result += INT.strResource('consistencyStrategy', 'csy', self.consistencyStrategy)
		result += INT.strResource('groupName', 'gn', self.groupName)
		result += INT.strResource('fanOutPoint', 'fopt', self.fanOutPoint)
		return result


	def getGroupResources(self):
		"""
		Return the resources that are managed by this &lt;group> resource. This method returns a list of
		the resources, or *None*.
		"""
		if not self._isValidFanOutPoint: return None
		response = MCA.get(self.session, self.fanOutPoint)
		return self._parseFanOutPointResponse(response)


	def deleteGroupResources(self):
		"""
		Delete the resources that are managed by this &lt;group> resource. 
		It returns *True* or *False* respectively.

		Note, that the &lt;group> itself is not deleted or altered. It must be deleted separately, 
		if necessary.
		"""
		if not self._isValidFanOutPoint: return None
		response = MCA.delete(self.session, self.fanOutPoint)
		return response and response.status_code == 200


	def updateGroupResources(self, resource):
		"""
		Update the resources that are managed by this &lt;group> resource.

		Args:

		- *resource*: A resource object that acts as a template to update the group resources.

		It returns a list of the updated resources, or *None* in case of an error.
		Please note, that in the returned resource instances only the properties are set that have been
		updated either by the update operation or as a side effect by the CSE, such as the
		`onem2mlib.ResourceBase.lastModifiedTime`. The order of the instances in the result list is the same as the order of 
		the resource identifiers in `onem2mlib.Group.memberIDs`.
		"""
		if not self._isValidFanOutPoint: return None
		if self.session.encoding == CON.Encoding_XML:
			body = INT.xmlToString(resource._createXML(isUpdate=True))
		elif self.session.encoding == CON.Encoding_JSON:
			body = json.dumps(resource._createJSON(isUpdate=True))
		else:
			raise EXC.NotSupportedError('Encoding not supported: ' + str(self.session.encoding))
		response = MCA.update(self.session, self.fanOutPoint, resource.type, body)
		return self._parseFanOutPointResponse(response)


	def createGroupResources(self, resource):
		"""
		Create/add a resource at all the resources managed by this &lt;group> resource.

		It returns a list of the created resources, or *None* in case of an error.
		"""
		if not self._isValidFanOutPoint: return None
		if self.session.encoding == CON.Encoding_XML:
			body = INT.xmlToString(resource._createXML(isUpdate=True))
		elif self.session.encoding == CON.Encoding_JSON:
			body = json.dumps(resource._createJSON(isUpdate=True))
		else:
			raise EXC.NotSupportedError('Encoding not supported: ' + str(self.session.encoding))
		response = MCA.create(self.session, self.fanOutPoint, resource.type, body)
		return self._parseFanOutPointResponse(response)


	def _parseXML(self, root):
		M._Group_parseXML(self, root)


	def _createXML(self, isUpdate=False):
		return M._Group_createXML(self, isUpdate)


	def _parseJSON(self, jsn):
		M._Group_parseJSON(self, jsn)


	def _createJSON(self, isUpdate=False):
		return M._Group_createJSON(self, isUpdate)


	def _parseFanOutPointResponse(self, response):
		# Get the resources from the answer
		if response and response.status_code == 200:
			if self.session.encoding == CON.Encoding_XML:
				rsps = INT.getElements(INT.responseToXML(response), 'pc')	# deep-search the tree for all <pc> elements
				if not rsps or not len(rsps) > 0: return None
				resources = []
				for rsp in rsps: # each <pc>  contains a onem2m resource 

					# The following is a hack to get a stand-alone XML tree. Otherwise the XML parser always only
					# finds the first resource in the whole response tree.
					# Take the XML as a string and parse it again.
					xml = INT.stringToXML(INT.xmlToString(rsp[0]))
					tag = INT.xmlQualifiedName(xml, True)
					# The resources get the group as a parent to pass on the Session.
					# Yes, this is halfway wrong, it will not result in a fully qualified path later.
					# But at least the resources can be used by the application
					resource = INT._newResourceFromTypeString(tag, self)
					if resource:
						resource._parseXML(xml)
						resources.append(resource)
				return resources
			elif self.session.encoding == CON.Encoding_JSON:
				elements = INT.getALLSubElementsJSON(response.json(), 'm2m:pc')
				resources = []
				for elem in elements:
					keyWithoutPrefix = list(elem.keys())[0].replace('m2m:','')
					resource = INT._newResourceFromTypeString(keyWithoutPrefix, self)
					if resource:
						resource._parseJSON(elem)
						resources.append(resource)
				return resources

			else:
				raise EXC.NotSupportedError('Encoding not supported: ' + str(self.session.encoding))
		return None


	def _isValidFanOutPoint(self):
		return  self.fanOutPoint and len(self.fanOutPoint) > 0 and self.session


	def _copy(self, resource):
		super()._copy(resource)
		self.maxNrOfMembers = resource.maxNrOfMembers
		self.memberType = resource.memberType
		self.currentNrOfMembers = resource.currentNrOfMembers
		self.memberIDs = resource.memberIDs
		self.memberTypeValidated = resource.memberTypeValidated
		self.consistencyStrategy = resource.consistencyStrategy
		self.groupName = resource.groupName
		self.fanOutPoint = resource.fanOutPoint



###############################################################################


class Subscription(ResourceBase):
	"""
	This class implements the oneM2M &lt;subscription> resource. 

	It is used to manage targets for notifications sent whenever a subscribed-to resource
	is changed.
	"""

	def __init__(self, parent=None, resourceName=None, resourceID=None, notificationURI=[], labels = [], instantly=True):
		"""
		Initialize the &lt;subscription> resource. 

		Args:

		- *parent*: The parent resource object in which the &lt;contentInstance> resource
			will be created.
		- *notificationURI*: A list consisting of one or more targets that the Hosting CSE
		shall send notifications to.
		- *instantly*: The resource will be instantly retrieved from or created on the CSE. This might throw
			a `onem2mlib.exceptions.CSEOperationError` exception in case of an error.
		- All other arguments initialize the status variables of the same name in
			&lt;subscription> instance or `onem2mlib.ResourceBase`.
		"""
	
		super().__init__(parent, resourceName, resourceID, CON.Type_Subscription, labels=labels)

		self.notificationURI = notificationURI
		"""
		A list consisting of one or more targets that the Hosting CSE shall send notifications to. 
		A target is either a oneM2M compliant Resource-ID (either structured or unstructured),
		or as a URL with one of oneM2M supported protocol binding, e.g. http.
		"""

		self.notificationContentType = CON.Sub_AllAttributes
		"""
		This attribute indicates a notification content type that shall be contained in
		notifications. The allowed values are one of the following constants:

		- Sub_AllAttributes (the default)
		- Sub_ModefiedAttributes
		- Sub_ResourceID 
		"""

		self.expirationCounter = -1
		"""
		This attribute indicates that the life of this subscription is set to a limit of a
		maximum number of notifications. After thix maximum number is reached, the subscription
		is deleted.
		"""

		self.latestNotify = None
		"""
		This attribute indicates if the subscriber wants only the latest notification. 
		If multiple notifications of this subscription are buffered, and if the value of
		this attribute is set to true, then only the last notification shall be sent and 
		it shall have the Event Category value set to "latest".
		"""

		self.groupID = None
		"""
		
		The ID of a &lt;group> resource in case the subscription is made through a group.
		"""

		self.notificationForwardingURI = None
		"""
		The attribute is a forwarding attribute that is present only for group related 
		subscriptions. It represents the resource subscriber notificationtarget. 
		"""

		self.subscriberURI = None
		"""
		This attribute is configured with the target of the subscriber. The target is used by the
		CSE to determine where to send a notification when the subscription is deleted. 
		A target is either a oneM2M compliant Resource-ID (either structured or unstructured),
		or as a URL with one of oneM2M supported protocol binding, e.g. http.
		"""


		# TODO: determine NotificationURi automatically
		#if not self.notificationURI or len(self.notificationURI) == 0:
		#	self.notificationURI = [ 'http://localhost:1400' + '?ri=' + parent.resourceID + '&nonce=' + str(uuid.uuid4().hex) ]

		if instantly:
			if not self.get():
				raise EXC.CSEOperationError('Cannot get or create Subscription. '  + MCA.lastError)


	def __str__(self):
		result = 'Subscription:\n'
		result += super().__str__()
		result += INT.strResource('notificationURI', 'nu', self.notificationURI)
		result += INT.strResource('notificationContentType', 'nct', self.notificationContentType)
		if self.expirationCounter != -1:
			result += INT.strResource('expirationCounter', 'exc', self.expirationCounter)
		if self.latestNotify:
			result += INT.strResource('latestNotify', 'ln', self.latestNotify)
		if self.groupID:
			result += INT.strResource('groupID', 'gpi', self.groupID)
		if self.notificationForwardingURI:
			result += INT.strResource('notificationForwardingURI', 'nfu', self.notificationForwardingURI)
		if self.subscriberURI:
			result += INT.strResource('subscriberURI', 'su', self.subscriberURI)
		return result


	def _parseXML(self, root):
		M._Subscription_parseXML(self, root)


	def _createXML(self, isUpdate=False):
 		return M._Subscription_createXML(self, isUpdate)


	def _parseJSON(self, jsn):
		M._Subscription_parseJSON(self, jsn)


	def _createJSON(self, isUpdate=False):
		return M._Subscription_createJSON(self, isUpdate)


	def _copy(self, resource):
		super()._copy(resource)
		self.notificationURI = resource.notificationURI
		self.notificationContentType = resource.notificationContentType
		self.expirationCounter = resource.expirationCounter
		self.latestNotify = resource.latestNotify
		self.groupID = resource.groupID
		self.notificationForwardingURI = resource.notificationForwardingURI



###############################################################################
#
#	General functions
#

def retrieveResourceFromCSE(parent, resourceID):
	"""
	Retrieve a resource by its *resourceID* from the CSE. Any valid *parent* resource
	instance from that CSE must be given as the first parameter to pass on various internal
	attributes. 
	The type of the resource is determined during retrieval.

	When successful, this method returns the retrieved resource, or None otherwise.
	"""
	if not parent.session or not resourceID or not len(resourceID):
		return False
	result = None
	response = MCA.get(parent.session, resourceID)
	if response and response.status_code == 200:
		ty = INT.getTypeFromResponse(response, parent.session.encoding)
		if parent.session.encoding == CON.Encoding_XML:
			root = INT.responseToXML(response)
			result = INT._newResourceFromRID(ty, resourceID, parent)
			if result:
				result._parseXML(root)
		elif parent.session.encoding == CON.Encoding_JSON:
			jsn = response.json()
			result = INT._newResourceFromRID(ty, resourceID, parent)
			if result:
				result._parseJSON(jsn)
	return result


###############################################################################
#
#	Exclude some docstrings to keep the documentation leaner.

__pdoc__                                                 = {}
__pdoc__['CSEBase.createInCSE']                 	     = None
__pdoc__['CSEBase.deleteFromCSE']                        = None
__pdoc__['CSEBase.updateInCSE']                 	     = None
__pdoc__['CSEBase.retrieveFromCSE']                      = None
__pdoc__['CSEBase.get']                                  = None
__pdoc__['CSEBase.discover']                             = None
__pdoc__['CSEBase.setAccessControlPolicies']             = None
__pdoc__['CSEBase.subscribe']                            = None
__pdoc__['CSEBase.unsubscribe']                          = None
__pdoc__['CSEBase.subscriptions']                        = None
__pdoc__['CSEBase.findSubscription']                     = None

__pdoc__['AE.createInCSE']                               = None
__pdoc__['AE.deleteFromCSE']                             = None
__pdoc__['AE.updateInCSE']                               = None
__pdoc__['AE.retrieveFromCSE']                           = None
__pdoc__['AE.get']                                       = None
__pdoc__['AE.discover']                                  = None
__pdoc__['AE.setAccessControlPolicies']                  = None
__pdoc__['AE.subscribe']                                 = None
__pdoc__['AE.unsubscribe']                               = None
__pdoc__['AE.subscriptions']                             = None
__pdoc__['AE.findSubscription']                          = None

__pdoc__['AccessControlPolicy.createInCSE']              = None
__pdoc__['AccessControlPolicy.deleteFromCSE']            = None
__pdoc__['AccessControlPolicy.updateInCSE']              = None
__pdoc__['AccessControlPolicy.retrieveFromCSE']          = None
__pdoc__['AccessControlPolicy.get']                      = None
__pdoc__['AccessControlPolicy.discover']                 = None
__pdoc__['AccessControlPolicy.setAccessControlPolicies'] = None
__pdoc__['AccessControlPolicy.subscribe']                = None
__pdoc__['AccessControlPolicy.unsubscribe']              = None
__pdoc__['AccessControlPolicy.subscriptions']            = None
__pdoc__['AccessControlPolicy.findSubscription']         = None

__pdoc__['Container.createInCSE']                        = None
__pdoc__['Container.deleteFromCSE']                      = None
__pdoc__['Container.updateInCSE']                        = None
__pdoc__['Container.retrieveFromCSE']                    = None
__pdoc__['Container.get']                                = None
__pdoc__['Container.discover']                           = None
__pdoc__['Container.setAccessControlPolicies']           = None
__pdoc__['Container.subscribe']                          = None
__pdoc__['Container.unsubscribe']                        = None
__pdoc__['Container.subscriptions']                      = None
__pdoc__['Container.findSubscription']                   = None

__pdoc__['ContentInstance.createInCSE']                  = None
__pdoc__['ContentInstance.deleteFromCSE']                = None
__pdoc__['ContentInstance.updateInCSE']                  = None
__pdoc__['ContentInstance.retrieveFromCSE']              = None
__pdoc__['ContentInstance.get']                          = None
__pdoc__['ContentInstance.discover']                     = None
__pdoc__['ContentInstance.setAccessControlPolicies']     = None
__pdoc__['ContentInstance.subscribe']                    = None
__pdoc__['ContentInstance.unsubscribe']                  = None
__pdoc__['ContentInstance.subscriptions']                = None
__pdoc__['ContentInstance.findSubscription']             = None

__pdoc__['Group.createInCSE']                            = None
__pdoc__['Group.deleteFromCSE']                          = None
__pdoc__['Group.updateInCSE']                            = None
__pdoc__['Group.retrieveFromCSE']                        = None
__pdoc__['Group.get']                                    = None
__pdoc__['Group.discover']                               = None
__pdoc__['Group.setAccessControlPolicies']       		 = None
__pdoc__['Group.subscribe']                              = None
__pdoc__['Group.unsubscribe']                            = None
__pdoc__['Group.subscriptions']                          = None
__pdoc__['Group.findSubscription']                       = None

__pdoc__['RemoteCSE.createInCSE']         		 		 = None
__pdoc__['RemoteCSE.deleteFromCSE']  		             = None
__pdoc__['RemoteCSE.updateInCSE']     		             = None
__pdoc__['RemoteCSE.retrieveFromCSE'] 		             = None
__pdoc__['RemoteCSE.get']              			         = None
__pdoc__['RemoteCSE.discover']            		         = None
__pdoc__['RemoteCSE.setAccessControlPolicies']		     = None
__pdoc__['RemoteCSE.subscribe']                          = None
__pdoc__['RemoteCSE.unsubscribe']                        = None
__pdoc__['RemoteCSE.subscriptions']                      = None
__pdoc__['RemoteCSE.findSubscription']                   = None

__pdoc__['Subscription.createInCSE']         		     = None
__pdoc__['Subscription.deleteFromCSE']  		         = None
__pdoc__['Subscription.updateInCSE']     		         = None
__pdoc__['Subscription.retrieveFromCSE'] 		         = None
__pdoc__['Subscription.get']              			     = None
__pdoc__['Subscription.discover']            		     = None
__pdoc__['Subscription.setAccessControlPolicies']		 = None
__pdoc__['Subscription.subscribe']                       = None
__pdoc__['Subscription.unsubscribe']                     = None
__pdoc__['Subscription.subscriptions']       		     = None
__pdoc__['Subscription.findSubscription']                = None

