#
#	resources.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module defines the oneM2M resource classes.
#

"""
This sub-module defines the oneM2M Resource and support classes of the onem2mlib module.

"""

import onem2mlib.utilities as UT
import onem2mlib.mcarequests as MCA
import onem2mlib.constants as CON
import onem2mlib.exceptions as EXC


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
		""" String. The resource ID of the resource. Assigned by the CSE. """

		self.resourceName= resourceName
		""" String. The resource name of the resource. Assigned by the application or the CSE. """

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
		result += UT.strResource('type', 'ty', self.type)
		result += UT.strResource('resourceName', 'rn', self.resourceName)
		result += UT.strResource('resourceID', 'ri', self.resourceID)
		result += UT.strResource('parentID', 'pi', self.parentID)
		result += UT.strResource('creationTime', 'ct', self.creationTime)
		result += UT.strResource('lastModifiedTime', 'lt', self.lastModifiedTime)
		result += UT.strResource('stateTag', 'st', self.stateTag)
		result += UT.strResource('labels', 'lbl', self.labels)
		result += UT.strResource('accessControlPolicyIDs', 'acpi', self.accessControlPolicyIDs)
		result += UT.strResource('expirationTime', 'et', self.expirationTime)
		result += UT.strResource('dynamicAuthorizationConsultationIDs', 'daci', self.dynamicAuthorizationConsultationIDs)
		result += UT.strResource('announceTo', 'at', self.announceTo)
		result += UT.strResource('announcedAttribute', 'aa', self.announcedAttribute)
		return result


	def setAccessControlPolicies(self, acps):
		"""
		Set the &lt;ccessControlPolicy> resource ID(s) for a resource (if the resource type supports 
		AccessControlPolicies). 

		*acps* could either be a single *AccessControlPolicies* object or a list of
		*AccessControlPolicy* objects. If *acps* is *None*, then the accessControlPolicies
		of this resource are set to an empty list.

		This method may throw a *NotSupportedError* exception when called on a resource that doesn't
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
						print(acp.resourceID)
						self.accessControlPolicyIDs.append(acp.resourceID)

	def _structuredResourceID(self):
		return self.parent._structuredResourceID() + '/' + self.resourceName


	def _parseResponse(self, response):
		#print(response.text)
		return self._parseXML(UT.responseToXML(response))


	def _parseXML(self, root):
		rootTag = UT.xmlQualifiedName(root)
		self.resourceName = UT.getAttribute(root, 'm2m:'+rootTag.localname, 'rn', self.resourceName)
		self.type = UT.getElement(root, 'ty', self.type)
		self.stateTag = UT.toInt(UT.getElement(root, 'st', self.stateTag))
		self.labels = UT.getElement(root, 'lbl', self.labels)
		self.resourceID = UT.getElement(root, 'ri', self.resourceID)
		self.parentID = UT.getElement(root, 'pi', self.parentID)
		self.creationTime = UT.getElement(root, 'ct', self.creationTime)
		self.lastModifiedTime = UT.getElement(root, 'lt', self.lastModifiedTime)
		self.accessControlPolicyIDs = UT.getElement(root, 'acpi', self.accessControlPolicyIDs)
		self.expirationTime = UT.getElement(root, 'et', self.expirationTime)
		self.announceTo = UT.getElement(root, 'at', self.announceTo)
		self.announcedAttribute = UT.getElement(root, 'aa', self.announcedAttribute)
		# todo: dynamicAuthorizationConsultationIDs


	# Create the XML for only some of the writable attributes.
	def _createXML(self, root):
		UT.addToElement(root, 'lbl', self.labels)
		UT.addToElement(root, 'aa', self.announcedAttribute)
		UT.addToElement(root, 'at', self.announceTo)
		UT.addToElement(root, 'acpi', self.accessControlPolicyIDs)


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

class CSEBase:
	"""
	CSEBase holds the attributes of a CSE and gives access to resources under it.
	"""

	def __init__(self, session=None, cseid=None):
		"""
		Initialize a CSEBase object.

		Args:

		- *session*: A Session object that points to a CSE.
		- *cseid*: The CSE-ID of the CSE.
		"""

		self.session = session
		"""Session. The Session object for the connection to the CSE. """

		self.type = CON.Type_CSEBase
		""" Integer. The type of the resource. """

		self.resourceID = None
		""" String. The resource ID of the CSE. Assigned by the CSE. R/O. """

		self.cseID = cseid
		""" String. The CSE-ID of the CSE. """

		self.cseType = None
		""" Integer. The type of the CSE. See also the `Constants.CSE_Type_*` constants.
			Assigned by the CSE. R/O."""

		self.csename = None
		""" String. The resource name of the CSE. Assigned by the CSE. R/O. """

		self.creationTime = None
		""" String. The creation time of the CSE. Assigned by the CSE. R/O. """

		self.lastModifiedTime = None
		""" String. The modification time of the CSE. Assigned by the CSE. R/O. """

		self.accessControlPolicyIDs = []
		""" List of String. A list of ACP resources. This might be an empty list."""

		self.supportedResourceType = []
		""" List of String. A list of supported resource types of this CSE.	Assigned by the CSE. R/O. """

		self.pointOfAccess = []
		""" List of String. A list of physical addresses to be used by remote CSEs to connect to this CSE.
			Assigned by the CSE. R/O. """

		if self.retrieveFromCSE():
			session.connected = True


	def __str__(self):
		result = 'CSEBase:\n'
		result += UT.strResource('cseID', 'csi', self.cseID)
		result += UT.strResource('csename', 'rn', self.csename)
		result += UT.strResource('resourceID', 'ri', self.resourceID)
		result += UT.strResource('cseType', 'cst', self.cseType)
		result += UT.strResource('creationTime', 'ct', self.creationTime)
		result += UT.strResource('lastModifiedTime', 'lt', self.lastModifiedTime)
		result += UT.strResource('accessControlPolicyIDs', 'acpi', self.accessControlPolicyIDs)
		result += UT.strResource('supportedResourceType', 'srt', self.supportedResourceType)
		result += UT.strResource('pointOfAccess', 'poa', self.pointOfAccess)
		return result


	def retrieveFromCSE(self):
		"""
		Retrieve the &lt;CSEBase> resource from the CSE. This object instance is updated accordingly. 

		The method returns *True* or *False*, depending on the success of the operation.

		The `onem2mlib.resources.CSEBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		response = MCA.get(self.session, self.cseID)
		if response and response.status_code == 200:
			#print(response.text)
			root = UT.responseToXML(response)
			self.csename = UT.getAttribute(root, 'm2m:cb', 'rn', self.csename)
			self.creationTime = UT.getElement(root, 'ct', self.creationTime)
			self.lastModifiedTime  = UT.getElement(root, 'lt', self.lastModifiedTime)
			self.accessControlPolicyIDs = UT.getElement(root, 'acpi', self.accessControlPolicyIDs)
			self.resourceID = UT.getElement(root, 'ri', self.resourceID)
			self.cseType = UT.toInt(UT.getElement(root, 'cst', self.cseType))
			self.supportedResourceType = UT.getElement(root, 'srt', self.supportedResourceType)
			# cseID (csi) ignored
			self.pointOfAccess = UT.getElement(root, 'poa', self.pointOfAccess)
			return True
		else:
			return False


	def accessControlPolicies(self):
		"""
		Return a list of &lt;accessControlPolicy> resources from this CSE, or an empty list.
		"""
		return _findSubResource(self, CON.Type_ACP)


	def findAccessControlPolicy(self, resourceName):
		"""
		Find a specific &lt;accessControlPolicy> resource by its *resourceName*, or None.
		"""
		return _findResourceInList(self.accessControlPolicies(), resourceName)


	def aes(self):
		"""
		Return a list of &lt;AE> resources from this CSE, or an empty list.
		"""
		return _findSubResource(self, CON.Type_AE)


	def findAE(self, resourceName):
		"""
		Find a specific &lt;AE> resource by its *resourceName*, or None otherwise.
		"""
		return _findResourceInList(self.aes(), resourceName)


	def groups(self):
		"""
		Return a list of &lt;group> resources from this CSE, or an empty list.
		"""
		return _findSubResource(self, CON.Type_Group)


	def retrieveResource(self, resourceID):
		"""
		Retrieve a resource by its *resourceID* from the CSE. When successful, this method returns the
		resource as an object, or None otherwise.
		"""
		if not self.session or not self.session.connected or not resourceID or not len(resourceID):	return False
		result = None
		response = MCA.get(self.session, resourceID)
		if response and response.status_code == 200:
			root = UT.responseToXML(response)
			type = UT.toInt(UT.getElement(root, 'ty'))
			if type == CON.Type_ContentInstance:	result = ContentInstance(self)
			elif type == CON.Type_Container:		result = Container(self)
			# elif type == CON.Type_FlexContainer:	result = FlexContainer(self)
			elif type == CON.Type_AE:				result = AE(self)
			elif type == CON.Type_Group:			result = Group(self)
			if result:
				result._parseXML(root)
		return result


	def _structuredResourceID(self):
		return '/' + self.cseID + '/' + self.csename


	def _copy(self, resource):
		self.csename = resource.csename
		self.creationTime = resource.creationTime
		self.lastModifiedTime = resource.lastModifiedTime
		self.accessControlPolicyIDs = resource.accessControlPolicyIDs
		self.resourceID = resource.resourceID
		self.cseType = resource.cseType
		self.supportedResourceType = resource.supportedResourceType
		self.cseID = resource.cseID
		self.pointOfAccess = self.pointOfAccess



###############################################################################

class AccessControlPolicy(ResourceBase):
	"""
	This class implements the oneM2M &lt;accessControlPolicy> resource. 

	It is always a sub-resource of a &lt;CSEBase> or a &lt;remoteCSE> resource, and it contains access right
	privileges to resources.
	"""

	def __init__(self, parent=None, resourceName=None, resourceID=None, privileges = [], selfPrivileges=[], instantly=False):
		"""
		Initialize the &lt;accessControlPolicy> resource. 

		Args:

		- *parent*: The parent resource object in which the &lt;accessControlPolicy> resource
			will be created. This must be a &lt;CSEBase> or &lt;remoteCSE> resource. This might raise a
			*ParameterError* exception if this is not the case.
		- *instantly*: The resource will be instantly retrieved from or created on the CSE. This might raise
			a *CSEOperationError* exception in case of an error.
		- All other arguments initialize the status variables of the same name in the
			&lt;accessControlPolicy> instance or `onem2mlib.resources.ResourceBase`.
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


	def retrieveFromCSE(self):
		"""
		Retrieve the &lt;accessControlPolicy> resource from the CSE. This object instance 
		is updated accordingly. 

		The method returns *True* or *False*, depending on the success of the operation.

		The `onem2mlib.resources.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		return MCA.retrieveFromCSE(self)


	def deleteFromCSE(self):
		"""
		Delete the &lt;accessControlPolicy> resource from the CSE. 

		The method returns *True* or *False*, depending on the success of the operation.'

		**Note**: One must delete associated resources first before delete the
		&lt;accessControlPolicy> resource.

		The `onem2mlib.resources.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		return MCA.deleteFromCSE(self)


	def createInCSE(self):
		"""
		Create the &lt;accessControlPolicy> resource in the &lt;CSEBase>.

		The method returns *True* or *False*, depending on the success of the operation.'

		The `onem2mlib.resources.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		return MCA.createInCSE(self, CON.Type_ACP)


	def updateInCSE(self):
		"""
		Update the existing &lt;accessControlPolicy> resource with new attributes.

		The method returns *True* or *False*, depending on the success of the operation.'

		The `onem2mlib.resources.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		return MCA.updateInCSE(self, CON.Type_ACP)


	def get(self):
		"""
		Retrieve the &lt;accessControlPolicy> resource from the CSE, or create it if 
		it doesn't exist. This object instance is updated accordingly. 

		The method returns *True* or *False*, depending on the success of the operation.

		The `onem2mlib.resources.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		return _retrieveOrCreateResource(self)


	def _parseXML(self, root):
		#print(UT.xmlToString(root))
		super()._parseXML(root)
		self.privileges = []
		pv = UT.getElementWithChildren(root, 'pv')
		if pv is not None and len(pv)>0:
			acrs = UT.getElements(pv[0], 'acr', relative=True) # only the first element[0]
			for a in acrs:
				acr = AccessControlRule()
				acr._parseXML(a)
				self.privileges.append(acr)
		self.selfPrivileges = []
		pvs = UT.getElementWithChildren(root, 'pvs')
		if pvs is not None and len(pvs)>0:
			acrs = UT.getElements(pvs[0], 'acr', relative=True) # only the first element[0]
			for a in acrs:
				acr = AccessControlRule()
				acr._parseXML(a)
				self.selfPrivileges.append(acr)


	def _createXML(self, isUpdate=False):
		root = UT.createElement('acp', namespace='m2m')
		# add resource attributes
		if self.resourceName and not isUpdate: 	# No RN when updating
			root.attrib['rn'] = self.resourceName
		super()._createXML(root)
		pv = UT.addElement(root, 'pv')
		for p in self.privileges:
			p._createXML(pv)
		pvs = UT.addElement(root, 'pvs')
		for p in self.selfPrivileges:
			p._createXML(pvs)
		return root


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
		result += UT.strResource('    ' + 'accessControlOriginators', 'acor', self.accessControlOriginators)
		result += UT.strResource('    ' + 'accessControlOperations', 'acop', self.accessControlOperations)
		return result


	def _parseXML(self, root):
		self.accessControlOriginators = []
		acors = UT.getElements(root, 'acor', relative=True)
		if acors:
			for acor in acors:
				self.accessControlOriginators.append(acor.text)
		self.accessControlOperations  = UT.getElement(root, 'acop', 0, relative=True)


	def _createXML(self, root):
		acr = UT.addElement(root, 'acr')
		#UT.addToElement(acr, 'acor', self.accessControlOriginators)
		for acor in self.accessControlOriginators:
			UT.addToElement(acr, 'acor', acor)
		UT.addToElement(acr, 'acop', self.accessControlOperations)


###############################################################################


class AE(ResourceBase):
	"""
	This class implements the oneM2M &lt;AE> resource. 

	It is usually a sub-resource of the &lt;CSEBase> resource, and it represents an 
	application and the sub-structure of resources beneath it.
	"""

	def __init__(self, parent=None, resourceName=None, appID=None, AEID=None, resourceID=None, requestReachability='true', labels=[], instantly=False):
		"""
		Initialize the &lt;AE> resource. 

		Args:

		- *parent*: The parent resource object in which the &lt;AE> resource
			will be created.
		- *instantly*: The resource will be instantly retrieved from or created on the CSE. This might raise
			a *CSEOperationError* exception in case of an error.
		- All other arguments initialize the status variables of the same name in the
			&lt;AE> instance or `onem2mlib.resources.ResourceBase`.
		"""
		super().__init__(parent, resourceName, resourceID, CON.Type_AE, labels=labels)

		self.appID = appID
		""" String. The identifier of the Application. Assigned by the application or the CSE. """
		if not self.appID:
			self.appID = self.resourceName

		self.AEID = AEID
		""" String. The identifier of the Application Entity. Assigned by the application or the CSE. """

		self.requestReachability = requestReachability
		""" Boolean as a String ('true', 'false'). This indicates the reachability of the AE.
			Assigned by the application or the CSE. """

		self.pointOfAccess = []
		""" List of String. The list of addresses for communicating with the registered AE. """

		if instantly:
			if not self.get():
				raise EXC.CSEOperationError('Cannot get or create AE. '  + MCA.lastError)


	def __str__(self):
		result = 'AE:\n'
		result += super().__str__()
		result += UT.strResource('appID', 'api', self.appID)
		result += UT.strResource('AEID', 'aei', self.AEID)
		result += UT.strResource('requestReachability', 'rr', self.requestReachability)
		result += UT.strResource('pointOfAccess', 'poa', self.pointOfAccess)
		return result


	def retrieveFromCSE(self):
		"""
		Retrieve the &lt;AE> resource from the CSE. This object instance is updated accordingly. 

		The method returns *True* or *False*, depending on the success of the operation.

		The `onem2mlib.resources.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		return MCA.retrieveFromCSE(self)


	def deleteFromCSE(self):
		"""
		Delete the &lt;AE> resource and all its sub-resources from the CSE. 

		The method returns *True* or *False*, depending on the success of the operation.'

		The `onem2mlib.resources.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		return MCA.deleteFromCSE(self)


	def createInCSE(self):
		"""
		Create the &lt;AE> resource in the &lt;CSEBase>.

		The method returns *True* or *False*, depending on the success of the operation.'

		The `onem2mlib.resources.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		return MCA.createInCSE(self, CON.Type_AE)


	def updateInCSE(self):
		"""
		Update the existing &lt;AE> resource with new attributes.

		The method returns *True* or *False*, depending on the success of the operation.'

		The `onem2mlib.resources.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		return MCA.updateInCSE(self, CON.Type_AE)


	def get(self):
		"""
		Retrieve the &lt;AE> resource from the CSE, or create it if it doesn't exist.
		This object instance is updated accordingly. 

		The method returns *True* or *False*, depending on the success of the operation.

		The `onem2mlib.resources.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		return _retrieveOrCreateResource(self)


	def containers(self):
		"""
		Return a list of all &lt;container> resources of this &lt;AE>, or an empty list.
		"""
		return _findSubResource(self, CON.Type_Container)


	def flexContainers(self):
		"""
		Return a list of all &lt;flexContainer> resources of this &lt;AE>, or an empty list.
		"""
		return _findSubResource(self, CON.Type_FlexContainer)


	def groups(self):
		"""
		Return a list of all &lt;group> resources of this &lt;AE>, or an empty list.
		"""
		return _findSubResource(self, CON.Type_Group)


	def findGroup(self, resourceName):
		"""
		Find a specific &lt;group> resource by its *resourceName*, or None.
		"""
		res = Group(self, resourceName=resourceName)
		if res.retrieveFromCSE():
			return res
		return None


	def findContainer(self, resourceName):
		"""
		Find a &lt;container> resource by its *resourceName*, or None.
		"""
		res = Container(self, resourceName=resourceName)
		if res.retrieveFromCSE():
			return res
		return None


	def _parseResponse(self, response):
		#print(response.text)
		return self._parseXML(UT.responseToXML(response))


	def _parseXML(self, root):
		super()._parseXML(root)
		self.appID = UT.getElement(root, 'api', self.appID)
		self.AEID = UT.getElement(root, 'aei', self.AEID)
		self.requestReachability = UT.getElement(root, 'rr', self.requestReachability)
		self.pointOfAccess = UT.getElement(root, 'poa', self.pointOfAccess)


	def _createXML(self, isUpdate=False):
		root = UT.createElement('ae', namespace='m2m')
		# add resource attributes
		if self.resourceName and not isUpdate: 	# No RN when updating
			root.attrib['rn'] = self.resourceName
		super()._createXML(root)
		if self.appID and not isUpdate: 	# No api when updating
			UT.addToElement(root, 'api', self.appID)
		UT.addToElement(root, 'rr', self.requestReachability)
		UT.addToElement(root, 'poa', self.pointOfAccess)
		return root


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

	def __init__(self, parent=None, resourceName=None, resourceID=None, maxNrOfInstances=None, maxByteSize=None, maxInstanceAge=None, labels=[], instantly=False):
		"""
		Initialize the &lt;container> resource. 

		Args:

		- *parent*: The parent resource object in which the &lt;container> resource
			will be created.
		- *instantly*: The resource will be instantly retrieved from or created on the CSE. This might raise
			a *CSEOperationError* exception in case of an error.
		- All other arguments initialize the status variables of the same name in the
			&lt;container> instance or `onem2mlib.resources.ResourceBase`.
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
		resource. It is limited by the *maxNrOfInstances* property. R/O."""
		
		self.currentByteSize = None
		""" Integer. Current size in bytes of data(i.e. content attribute of a &lt;contentInstance>
		resource) stored in all direct child <contentInstance> resources of a &lt;container> resource.
		This is the summation of contentSize attribute values of the &lt;contentInstance> resources. 
		It is limited by the *maxByteSize* property. R/O."""

		self.oldest = None
		""" String. The resourceID of the oldest &lt;contentInstance> resource in this &lt:container>
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
		result += UT.strResource('maxNrOfInstances', 'mni', self.maxNrOfInstances)
		result += UT.strResource('maxByteSize', 'mbs', self.maxByteSize)
		result += UT.strResource('maxInstanceAge', 'mia', self.maxInstanceAge)
		result += UT.strResource('currentNrOfInstances', 'cni', self.currentNrOfInstances)
		result += UT.strResource('currentByteSize', 'cbs', self.currentByteSize)
		result += UT.strResource('oldest', 'ol', self.oldest)
		result += UT.strResource('latest', 'la', self.latest)
		return result


	def retrieveFromCSE(self):
		"""
		Retrieve the &lt;container> resource from the CSE. This object instance is updated accordingly. 

		The method returns *True* or *False*, depending on the success of the operation.

		The `onem2mlib.resources.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		return MCA.retrieveFromCSE(self)


	def createInCSE(self):
		"""
		Create the &lt;container> in the &lt;CSEBase>.

		The method returns *True* or *False*, depending on the success of the operation.

		The `onem2mlib.resources.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		return MCA.createInCSE(self, CON.Type_Container)


	def updateInCSE(self):
		"""
		Update the existing &lt;container> resource with new attributes.

		The method returns *True* or *False* depending on the success of the operation.

		The `onem2mlib.resources.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		return MCA.updateInCSE(self, CON.Type_Container)


	def deleteFromCSE(self):
		"""
		Delete the &lt;container> resource and all its sub-resources from the CSE.

		The method returns *True* or *False* depending on the success of the operation.

		The `onem2mlib.resources.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		return MCA.deleteFromCSE(self)


	def get(self):
		"""
		Retrieve the &lt;container> resource from the CSE, or create it if it doesn't exist.
		This object instance is updated accordingly. 

		The method returns *True* or *False*, depending on the success of the operation.

		The `onem2mlib.resources.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		return _retrieveOrCreateResource(self)


	def containers(self):
		"""
		Return all &lt;container> sub-resources from this container, or an empty list.
		"""
		return _findSubResource(self, CON.Type_Container)


	def contentInstances(self):
		"""
		Return all &lt;contentInstance> sub-resources from this container, or an empty list.
		"""
		return _findSubResource(self, CON.Type_ContentInstance)


	def findContainer(self, resourceName):
		"""
		Find a &lt;container> resource by its *resourceName*, or None.
		"""
		res = Container(self, resourceName=resourceName)
		if res.retrieveFromCSE():
			return res
		return None


	def findContentInstance(self, resourceName):
		"""
		Find a &lt;ContentInstance> resource by its *resourceName*, or None.
		"""
		# cins = self.contentInstances()
		# if cins and len(cins)>0:
		# 	for cin in cins:
		# 		if cin.resourceName == resourceName:
		# 			return cin
		# return None
		res = ContentInstance(self, resourceName=resourceName)
		if res.retrieveFromCSE():
			return res
		return None


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


	def _getContentInstance(self, path):
		if not self.session or not self.session.connected or not path: return None
		response = MCA.get(self.session, path)
		if response and response.status_code == 200:
			contentInstance = ContentInstance(self)
			contentInstance._parseResponse(response)
			return contentInstance
		return None


	def _parseResponse(self, response):
		#print(response.text)
		return self._parseXML(UT.responseToXML(response))


	def _parseXML(self, root):
		super()._parseXML(root)
		self.maxNrOfInstances = UT.toInt(UT.getElement(root, 'mni', self.maxNrOfInstances))
		self.maxByteSize = UT.toInt(UT.getElement(root, 'mbs', self.maxByteSize))
		self.maxInstanceAge = UT.toInt(UT.getElement(root, 'mia', self.maxInstanceAge))
		self.currentNrOfInstances = UT.toInt(UT.getElement(root, 'cni', self.currentNrOfInstances))
		self.currentByteSize = UT.toInt(UT.getElement(root, 'cbs', self.currentByteSize))
		self.oldest = UT.getElement(root, 'ol', self.oldest)
		self.latest = UT.getElement(root, 'la', self.latest)


	def _createXML(self, isUpdate=False):
		root = UT.createElement('cnt', namespace='m2m')
		# add resource attributes
		if self.resourceName and not isUpdate:		# No RN when updating
			root.attrib['rn'] = self.resourceName
		super()._createXML(root)
		UT.addToElement(root, 'mni', self.maxNrOfInstances)
		UT.addToElement(root, 'mbs', self.maxByteSize)
		UT.addToElement(root, 'mia', self.maxInstanceAge)
		return root


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
	`onem2mlib.resources.ContentInstance.contentInfo`  state variable. The default is 
	`text/plain:0`. See also the oneM2M specification for further details.

	To retrieve the actual content value of the resource 
	(from `onem2mlib.resources.ContentInstance.content`) one must first check the 
	`onem2mlib.resources.ContentInstance.contentInfo` state variable to determine the
	type of the content and decode it accordingly.
	"""


	def __init__(self, parent=None, resourceName=None, content=None, contentInfo=None, resourceID=None, labels = [], instantly=False):
		"""
		Initialize the &lt;contentInstance> resource. 

		Args:

		- *parent*: The parent resource object in which the &lt;contentInstance> resource
			will be created.
		- *instantly*: The resource will be instantly retrieved from or created on the CSE. This might raise
			a *CSEOperationError* exception in case of an error.
		- All other arguments initialize the status variables of the same name in
			&lt;contentInstance> instance or `onem2mlib.resources.ResourceBase`.
		"""
		super().__init__(parent, resourceName, resourceID, CON.Type_ContentInstance, labels=labels)

		self.contentInfo = contentInfo
		""" String. The type of the data in the `onem2mlib.resources.ContentInstance.content` 
		state variable."""

		self.contentSize = 0
		""" String. The size of the data in the `onem2mlib.resources.ContentInstance.content` 
		state variable. R/O."""

		self.content = content
		""" Usually an encoded String. The actual content of the &lt;contentInstance> resource."""

		if instantly:
			if not self.get():
				raise EXC.CSEOperationError('Cannot get or create ContentInstance. '  + MCA.lastError)


	def __str__(self):
		result = 'ContentInstance:\n'
		result += super().__str__()
		result += UT.strResource('contentInfo', 'cnf', self.contentInfo)
		result += UT.strResource('contentSize', 'cs', self.contentSize)
		result += UT.strResource('content', 'con', self.content)
		return result


	def retrieveFromCSE(self):
		"""
		Retrieve the &lt;contentInstance> from the CSE.	This object instance is updated accordingly. 

		The method returns *True* or *False*, depending on the success of the operation.

		The `onem2mlib.resources.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		return MCA.retrieveFromCSE(self)


	def createInCSE(self):
		"""
		Create the &lt;contentInstance> resource in the CSE.

		The method returns *True* or *False* depending on the success of the operation.

		The `onem2mlib.resources.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		return MCA.createInCSE(self, CON.Type_ContentInstance)


	def deleteFromCSE(self):
		"""
		Delete the &lt;contentInstance> resource from the CSE.

		The method returns *True* or *False* depending on the success of the operation.

		The `onem2mlib.resources.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		return MCA.deleteFromCSE(self)


	def get(self):
		"""
		Retrieve the &lt;contentInstance> resource from the CSE, or create it if it doesn't exist.
		This object instance is updated accordingly. 

		The method returns *True* or *False*, depending on the success of the operation.

		The `onem2mlib.resources.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		return _retrieveOrCreateResource(self)


	def _parseResponse(self, response):
		#print(response.text)
		return self._parseXML(UT.responseToXML(response))


	def _parseXML(self, root):
		super()._parseXML(root)
		self.contentInfo = UT.getElement(root, 'cnf', self.contentInfo)
		self.contentSize = UT.toInt(UT.getElement(root, 'cs', self.contentSize))
		self.content = UT.getElement(root, 'con', self.content)


	def _createXML(self, isUpdate=False):
		root = UT.createElement('cin', namespace='m2m')
		# add resource attributes
		if self.resourceName and not isUpdate:      # No RN when updating
			root.attrib['rn'] = self.resourceName
		super()._createXML(root)
		UT.addToElement(root, 'cnf', self.contentInfo)
		UT.addToElement(root, 'con', self.content)
		return root


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
	*memberIDs* attribute. The &lt;group> resource contains an attribute that represents the members of 
	the group and the &lt;fanOutPoint> virtual resource that enables generic operations to be applied 
	to all the resources represented by those members.
	"""
	def __init__(self, parent=None, resourceName=None, resourceID=None, resources=[], maxNrOfMembers=CON.Grp_def_maxNrOfMembers, consistencyStrategy=CON.Grp_ABANDON_MEMBER, groupName=None, labels = [], instantly=False):
		"""
		Initialize the &lt;group> resource. 

		Args:

		- *parent*: The parent resource object in which the &lt;group> resource
			will be created.
		- *instantly*: The resource will be instantly retrieved from or created on the CSE. This might raise
			a *CSEOperationError* exception in case of an error.
		- All other arguments initialize the status variables of the same name in
			&lt;group> instance or `onem2mlib.resources.ResourceBase`.
		"""		
		super().__init__(parent, resourceName, resourceID, CON.Type_Group, labels=labels)

		self.maxNrOfMembers = maxNrOfMembers
		""" Integer. Maximum number of members in the &lt;group>. """

		self.resources = resources
		""" List of resource instances. The resources in this &lt;group>. """

		self.currentNrOfMembers = len(resources)
		""" Integer. Current number of members in a &lt;group>. It shall not be larger than 
		*maxNrOfMembers*. R/O. """

		self.memberTypeValidated = None
		""" Boolean as a String ('true', 'false'), or None. Denotes if the resource types of all members resources 
		of the &lt;group> has been validated by the Hosting CSE. In the case that the *memberType* 
		attribute of the &lt;group> resource is not 'mixed', then this attribute shall be set. """

		self.consistencyStrategy = consistencyStrategy
		""" Integer. This attribute determines how to deal with the &lt;group> resource if the *memberType*
		validation fails. Its possible values (from the Constants sub-module) are

		- *Grp_ABANDON_MEMBER* : delete the inconsistent member
		- *Grp_ABANDON_GROUP* : delete the group
		- *Grp_SET_MIXED* : set the *memberType* to "mixed"

		The default is *Grp_ABANDON_MEMBER*. """
		
		self.groupName = groupName
		""" String. Human readable name of the &lt;group>. """

		self.fanOutPoint = None
		""" String. The resourceID of the virtial &lt;fanOutPoint> resource. Whenever a request is sent 
		to the &lt;fanOutPoint> resource, the request is fanned out to each of the members of the
		&lt;group> resource indicated by the *membersIDs* attribute of the &lt;group> resource. R/O. """

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
		self.memberIDs = []
		""" List String, member resource IDs. Each memberID should refer to a member resource or a 
		(sub-) &lt;group> resource of the &lt;group>. """

		for res in self.resources:
			self.memberIDs.append(res.resourceID)

		if instantly:
			if not self.get():
				raise EXC.CSEOperationError('Cannot get or create Group. '  + MCA.lastError)


	def __str__(self):
		result = 'Group:\n'
		result += super().__str__()
		result += UT.strResource('maxNrOfMembers', 'mnm', self.maxNrOfMembers)
		result += UT.strResource('memberType', 'mt', self.memberType)
		result += UT.strResource('currentNrOfMembers', 'cnm', self.currentNrOfMembers)
		result += UT.strResource('memberIDs', 'mid', self.memberIDs)
		result += UT.strResource('memberTypeValidated', 'mtv', self.memberTypeValidated)
		result += UT.strResource('consistencyStrategy', 'csy', self.consistencyStrategy)
		result += UT.strResource('groupName', 'gn', self.groupName)
		result += UT.strResource('fanOutPoint', 'fopt', self.fanOutPoint)
		return result


	def createInCSE(self):
		"""
		Create the &lt;group> resource in the CSE. 

		This object instance is updated accordingly. 

		The method returns *True* or *False* depending on the success of the operation.
		"""
		return MCA.createInCSE(self, CON.Type_Group)


	def deleteFromCSE(self):
		"""
		Delete the &lt;group> resource from the CSE. 

		The method returns *True* or *False* depending on the success of the operation.

		The `onem2mlib.resources.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		return MCA.deleteFromCSE(self)


	def retrieveFromCSE(self):
		"""
		Retrieve the &lt;group> from the CSE. This object instance is updated accordingly. 

		The method returns *True* or *False*, depending on the success of the operation.

		The `onem2mlib.resources.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		return MCA.retrieveFromCSE(self)


	def updateInCSE(self):
		"""
		Update the existing &lt;group> resource with new attributes. It returns *True* or *False*.

		The method returns *True* or *False* depending on the success of the operation.

		The `onem2mlib.resources.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		return MCA.updateInCSE(self, CON.Type_Group)


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

		It returns a list of the updated resources, or *None* in case of an error.
		Please note, that in the returned resource instances only the properties are set that have been
		updated either by the update operation or as a side effect by the CSE, such as the
		lastModifiedTime. The order of the instances in the result list is the same as the order of 
		the resource identifiers in *memberIDs*.
		"""
		if not self._isValidFanOutPoint: return None
		body = UT.xmlToString(resource._createXML(isUpdate=True))
		response = MCA.update(self.session, self.fanOutPoint, resource.type, body)
		return self._parseFanOutPointResponse(response)


	def createGroupResources(self, resource):
		"""
		Create/add a resource at all the resources managed by this &lt;group> resource.

		It returns a list of the created resources, or *None* in case of an error.
		"""
		if not self._isValidFanOutPoint: return None
		body = UT.xmlToString(resource._createXML(isUpdate=True))
		response = MCA.create(self.session, self.fanOutPoint, resource.type, body)
		return self._parseFanOutPointResponse(response)


	def get(self):
		"""
		Retrieve the &lt;group> resource from the CSE, or create it if it doesn't exist.
		This object instance is updated accordingly. 

		The method returns *True* or *False*, depending on the success of the operation.

		The `onem2mlib.resources.ResourceBase.resourceID` state variable of the instance
		must be set to a valid value.
		"""
		return _retrieveOrCreateResource(self)


	def _parseResponse(self, response):
		#print(response.text)
		return self._parseXML(UT.responseToXML(response))


	def _parseXML(self, root):
		super()._parseXML(root)
		self.maxNrOfMembers = UT.toInt(UT.getElement(root, 'mnm', self.maxNrOfMembers))
		self.memberType = UT.toInt(UT.getElement(root, 'mt', self.memberType))
		self.currentNrOfMembers = UT.toInt(UT.getElement(root, 'cnm', self.currentNrOfMembers))
		self.memberIDs = UT.getElement(root, 'mid', self.memberIDs)
		self.memberTypeValidated = UT.getElement(root, 'mtv', self.memberTypeValidated)
		self.consistencyStrategy = UT.toInt(UT.getElement(root, 'csy', self.consistencyStrategy))
		self.groupName = UT.getElement(root, 'gn', self.groupName)
		self.fanOutPoint = UT.getElement(root, 'fopt', self.fanOutPoint)


	def _createXML(self, isUpdate=False):
		root = UT.createElement('grp', namespace='m2m')
		# add resource attributes
		if self.resourceName and not isUpdate:      # No RN when updating
			root.attrib['rn'] = self.resourceName
		super()._createXML(root)
		if self.maxNrOfMembers and not isUpdate: 	# No mnm when updating
			UT.addToElement(root, 'mnm', self.maxNrOfMembers)
		UT.addToElement(root, 'mt', self.memberType)
		UT.addToElement(root, 'mid', self.memberIDs, mandatory=True)
		if self.consistencyStrategy and not isUpdate: 	# No csy when updating
			UT.addToElement(root, 'csy', self.consistencyStrategy)
		UT.addToElement(root, 'gn', self.groupName)
		return root


	def _parseFanOutPointResponse(self, response):
		# Get the resources from the answer
		if response and response.status_code == 200:
			rsps = UT.getElements(UT.responseToXML(response), 'pc')	# deep-search the tree for all <pc> elements
			if not rsps or not len(rsps) > 0: return None
			resources = []
			for rsp in rsps: # each <pc>  contains a onem2m resource 

				# The following is a hack to get a stand-alone XML tree. Otherwise the XML parser always only
				# finds the first resource in the whole response tree.
				# Take the XML as a string and parse it again.
				xml = UT.stringToXML(UT.xmlToString(rsp[0]))

				resource = None
				tag = UT.xmlQualifiedName(xml, True)
				# The resources get the group as a parent to pass on the Session.
				# Yes, this is halfway wrong, it will not result in a fully qualified path later.
				# But at least the resources can be used by the application
				if tag == 'cnt': 	resource = Container(self)
				elif tag == 'cin':	resource = ContentInstance(self)
				elif tag == 'ae':	resource = AE(self)
				# Can a group point to groups?
				if resource:
					resource._parseXML(xml)
					resources.append(resource)
			return resources
		return None


	def _isValidFanOutPoint(self):
		return  self.fanOutPoint and len(self.fanOutPoint) > 0 and self.session and self.session.connected


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

#
#	Search
#

# Find a sub-resource
def _findSubResource(resource, type):
	if not resource or not resource.session or not resource.resourceID or not resource.session.connected: return None
	result = []
	response = MCA.discover(resource.session, resource.resourceID, type=type)
	if response and response.status_code == 200:
		root = UT.responseToXML(response)
		list = UT.getElement(root, 'm2m:uril')
		if list and len(list)> 0:
			ris = list.split()

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
					if type == CON.Type_ContentInstance:
						cin = ContentInstance(resource, resourceID=ri)
						cin.retrieveFromCSE()
						result.append(cin)
					elif type == CON.Type_Container:
						cnt = Container(resource, resourceID=ri)
						cnt.retrieveFromCSE()
						result.append(cnt)
					# elif type == CON.Type_FlexContainer:
					# 	fcnt = FlexContainer(resource, resourceID=ri)
					# 	fcnt.retrieveFromCSE()
					# 	result.append(fcnt)
					elif type == CON.Type_AE:
						ae = AE(resource, resourceID=ri)
						ae.retrieveFromCSE()
						result.append(ae)
					elif type == CON.Type_Group:
						grp = Group(resource, resourceID=ri)
						grp.retrieveFromCSE()
						result.append(grp)
					elif type == CON.Type_ACP:
						acp = AccessControlPolicy(resource, resourceID=ri)
						acp.retrieveFromCSE()
						result.append(acp)
			# Still a hack: sort the list by the ct attribute
			result.sort(key=lambda x: x.creationTime)

	return result


# Find a resource from a list by its resource name
def _findResourceInList(resources, resourceName):
	if resources and len(resources)>0:
		for res in resources:
			if res.resourceName == resourceName:
				return res
	return None


# Retrieve of create a resource
def _retrieveOrCreateResource(resource):
		if resource.resourceID:
			return resource.retrieveFromCSE()
		if resource.resourceName:
			if resource.retrieveFromCSE():
				return True
		return resource.createInCSE()

