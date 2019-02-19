#
#	ResourceBase.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module implements the base class for resources.
#

import logging, json
import onem2mlib.constants as CON
import onem2mlib.mcarequests as MCA
import onem2mlib.internal as INT
import onem2mlib.exceptions as EXC
import onem2mlib.notifications as NOT
import onem2mlib.utilities as UT


logger = logging.getLogger(__name__)

class ResourceBase:
	"""
	The ResourceBase is the base class for most of resource classes. It handles the common
	resource attributes.
	"""

	def __init__(self, parent, resourceName, resourceID, type, typeShortName, namespace='m2m', labels=[]):
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

		self.typeShortName = typeShortName
		""" String. The resource type as a shortname. """
		
		self.resourceID	= resourceID
		""" String. The resource ID of the resource. Assigned by the CSE.
			For a &lt;CSEBase> this is the *cseID*.2"""
		
		self.resourceName = resourceName
		""" String. The resource name of the resource. Assigned by the application or the CSE. 
			For a &lt;CSEBase> this is the *cseName*."""

		self.namespace = namespace
		""" String. The namespace of the resource. """
		
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

		# Internal list of per-class marshalling methods
		# [ parseXML, createXML, parseJSON, createJSON ]
		self._marshallers = [ None, None, None, None ]
		# TODO for all classes
		# TODO move methods to resourceBase


	def __str__(self):
		result = ''
		result += INT.strResource('type', 'ty', str(self.type) + ' (' + self.namespace + ':' + self.typeShortName + ')')
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

		from .ContentInstance import ContentInstance

		if isinstance(self, ContentInstance):
			logger.error('Resource does not support AccessControlPolicies: ' + INT.nameAndType(self))
			raise EXC.NotSupportedError('Resource does not support AccessControlPolicies: ' + INT.nameAndType(self))

		if acps is not None:
			if not isinstance(acps, list):
				if acps.resourceID is not None:
					self.accessControlPolicyIDs.append(acps.resourceID)
			else:
				for acp in acps:
					if acps.resourceID is not None:
						self.accessControlPolicyIDs.append(acps.resourceID)


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
			logger.error('Resource doesn''t support deleting: ' + INT.nameAndType(self))
			raise EXC.NotSupportedError('Resource doesn''t support deleting: ' + INT.nameAndType(self))
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
			logger.error('Resource doesn''t support creating: ' + INT.nameAndType(self))
			raise EXC.NotSupportedError('Resource doesn''t support creating: ' + INT.nameAndType(self))
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
			logger.error('Resource doesn''t support updating: ' + INT.nameAndType(self))
			raise EXC.NotSupportedError('Resource doesn''t support updating: ' + INT.nameAndType(self))
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
		import onem2mlib.utilities

		rids = MCA.discoverInCSE(self, filter=filter, filterOperation=filterOperation)
		if rids is None:
			return []
		return [ UT.retrieveResourceFromCSE(self, id) for id in rids ]


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
			logger.error('Subscription not supported for this resource type: ' + INT.nameAndType(self))
			raise EXC.NotSupportedError('Subscription not supported for this resource type: ' + INT.nameAndType(self))
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
			logger.error('Subscription not supported for this resource type: ' + INT.nameAndType(self))
			raise EXC.NotSupportedError('Subscription not supported for this resource type: ' + INT.nameAndType(self))
		return NOT.removeSubscription(self)


	def subscriptions(self):
		"""
		Return a list of &lt;subscription> resources of a rersource, or an empty list.

		This method might throw	a `onem2mlib.exceptions.NotSupportedError` exception in case
		the target resource type doesn't support subscriptions.
		"""
		if self.type not in NOT._allowedSubscriptionResources:
			logger.error('Subscription not supported for this resource type: ' + INT.nameAndType(self))
			raise EXC.NotSupportedError('Subscription not supported for this resource type')
		return INT._findSubResource(self, CON.Type_Subscription)


	def findAccessControlPolicy(self, resourceName):
		"""
		Find a specific &lt;accessControlPolicy> resource by its *resourceName*, or None.

		*resourceName* could point to a direct sub-resource, or it can be a relative path
		pointing to a resource deeper down the resource tree. In that case the path
		elements are separated by '/' characters.
		"""
		return INT._getResourceFromCSEByResourceName(CON.Type_ACP, resourceName, self)


	def findAE(self, resourceName):
		"""
		Find a specific &lt;AE> resource by its *resourceName*, or None otherwise.

		*resourceName* could point to a direct sub-resource, or it can be a relative path
		pointing to a resource deeper down the resource tree. In that case the path
		elements are separated by '/' characters.
		"""
		return INT._getResourceFromCSEByResourceName(CON.Type_AE, resourceName, self)


	def findContainer(self, resourceName):
		"""
		Find a &lt;container> resource by its *resourceName*, or None.

		*resourceName* could point to a direct sub-resource, or it can be a relative path
		pointing to a resource deeper down the resource tree. In that case the path
		elements are separated by '/' characters.
		"""
		return INT._getResourceFromCSEByResourceName(CON.Type_Container, resourceName, self)


	def findContentInstance(self, resourceName):
		"""
		Find a &lt;ContentInstance> resource by its *resourceName*, or None.

		*resourceName* could point to a direct sub-resource, or it can be a relative path
		pointing to a resource deeper down the resource tree. In that case the path
		elements are separated by '/' characters.
		"""
		return INT._getResourceFromCSEByResourceName(CON.Type_ContentInstance, resourceName, self)


	def findGroup(self, resourceName):
		"""
		Find a specific &lt;group> resource by its *resourceName*, or None.

		*resourceName* could point to a direct sub-resource, or it can be a relative path
		pointing to a resource deeper down the resource tree. In that case the path
		elements are separated by '/' characters.
		"""
		return INT._getResourceFromCSEByResourceName(CON.Type_Group, resourceName, self)


	def findRemoteCSE(self, resourceName):
		"""
		Find a specific &lt;remoteCSE> resource by its *resourceName*, or None.

		*resourceName* could point to a direct sub-resource, or it can be a relative path
		pointing to a resource deeper down the resource tree. In that case the path
		elements are separated by '/' characters.
		"""
		return INT._getResourceFromCSEByResourceName(CON.Type_RemoteCSE, resourceName, self)


	def findSubscription(self, resourceName):
		"""
		Find a specific &lt;subscription> resource by its *resourceName*, or None otherwise.

		*resourceName* could point to a direct sub-resource, or it can be a relative path
		pointing to a resource deeper down the resource tree. In that case the path
		elements are separated by '/' characters.
		"""
		return INT._getResourceFromCSEByResourceName(CON.Type_Subscription, resourceName, self)



	# Recursivly construct a structured resourceName
	def _structuredResourceID(self):
		logger.debug('ResourceID: ' + str(self.resourceID))
		if self.type == CON.Type_CSEBase:		# CSEBase means end of recursion
			if self.resourceID.startswith('/'):	# special handling for CSE ID's that start with a /
				return self.resourceID + '/' + self.resourceName
			return '/' + self.resourceID + '/' + self.resourceName
			#return '/'  + self.resourceName
		return self.parent._structuredResourceID() + '/' + self.resourceName


	def _parseResponse(self, response):
		if self.session.encoding == CON.Encoding_XML:
			return self._parseXML(INT.responseToXML(response))
		elif self.session.encoding == CON.Encoding_JSON:
			return self._parseJSON(response.json())
		logger.error('Encoding not supported: ' + str(self.session.encoding))
		raise EXC.NotSupportedError('Encoding not supported: ' + str(self.session.encoding))


	def _createContent(self, isUpdate=False):
		if self.session.encoding == CON.Encoding_XML:
			return INT.xmlToString(self._createXML(isUpdate))
		elif self.session.encoding == CON.Encoding_JSON:
			return json.dumps(self._createJSON(isUpdate))
		logger.error('Encoding not supported: ' + str(self.session.encoding))
		raise EXC.NotSupportedError('Encoding not supported: ' + str(self.session.encoding))


	# Marschalling calls
	def _parseXML(self, root):
		if self._marshallers[0] is not None:
			self._marshallers[0](self, root)


	def _createXML(self, isUpdate=False):
		if self._marshallers[1] is not None:
			return self._marshallers[1](self, isUpdate)
		return None


	def _parseJSON(self, jsn):
		if self._marshallers[2] is not None:
			self._marshallers[2](self, jsn)


	def _createJSON(self, isUpdate=False):
		if self._marshallers[3] is not None:
			return self._marshallers[3](self, isUpdate)
		return None


	def _copy(self, resource):
		self.resourceName = resource.resourceName
		self.namespace = resource.namespace
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


