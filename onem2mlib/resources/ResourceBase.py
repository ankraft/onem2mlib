#
#	ResourceBase.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
""" This module implements the base class for resources. """

from __future__ import annotations
from typing import Optional, Any, cast, Callable, TYPE_CHECKING

import logging, json
from unicodedata import name

from .. import constants as CON
from .. import mcarequests as MCA
from .. import internal as INT
from .. import exceptions as EXC
from .. import notifications as NOT


if TYPE_CHECKING:
	from ..datatypes import EventNotificationCriteria
	from ..resources.AccessControlPolicy import AccessControlPolicy
	from ..resources.Session import Session
	from ..resources.AE import AE
	from ..resources.Container import Container
	from ..resources.ContentInstance import ContentInstance
	from ..resources.Group import Group
	from ..resources.RemoteCSE import RemoteCSE
	from ..resources.Subscription import Subscription

	from requests import Response

logger = logging.getLogger(__name__)
""" Logger for this module. """

class ResourceBase:
	""" The ResourceBase is the base class for most of resource classes. It handles the common
		resource attributes.
	"""
	def __init__(self, **kwargs: Any) -> None:
		""" Initialize a ResourceBase instance.

			Note:
				All keyword arguments initialize the status variables of the same name in the `ResourceBase` instance.
		"""	

		self.parent: Optional[ResourceBase] = kwargs.pop('parent', None)
		""" The parent resource of this resource. """

		self.session: Optional[Session] = kwargs.pop('session', None)
		""" The Session object of the parent. """
		if self.parent and not self.session:
			self.session = self.parent.session   
		

		self.type: int = kwargs.pop('type', None)
		""" The type of the resource. """

		self.typeShortName: Optional[str] = kwargs.pop('typeShortName', None)
		""" The resource type as a shortname. """

		self.resourceID: Optional[str] = kwargs.pop('resourceID', None)
		""" The resource ID of the resource. Assigned by the CSE.
			For a <CSEBase> this is the *cseID*."""

		self.resourceName: Optional[str] = kwargs.pop('resourceName', None)
		""" The resource name of the resource. Assigned by the application or the CSE. 
			For a <CSEBase> this is the *cseName*."""

		self.originator: Optional[str] = kwargs.pop('originator', None)
		""" The originator of the resource. Assigned by the application or the CSE. 
			For a <CSEBase> this is the *x-origin*."""

		self.namespace: str = kwargs.pop('namespace', 'm2m')
		""" The namespace of the resource. """
  
		self.labels: list[str] = kwargs.pop('labels', [])
		""" A list of labels of the resource. This might be an empty list. """
  
		accessControlPolicies = kwargs.pop('accessControlPolicies', None)
		self.accessControlPolicyIDs: list[str] = []
		""" A list of ACP resources. This might be an empty list."""
		if accessControlPolicies:
			self.setAccessControlPolicies(accessControlPolicies)

		self.parentID: Optional[str] = None
		""" The resource ID of the parent resource. Assigned by the CSE. """
		
		self.creationTime: Optional[str] = None
		""" The time of creation of the resource in the CSE. Assigned by the CSE. R/O. """
		
		self.lastModifiedTime: Optional[str] = None
		""" The time of the last modification of the resource. Assigned by the CSE. R/O. """
		self.expirationTime: Optional[str] = None
		""" The expiration time of the resource, or None. Assigned by the CSE. R/O. """
		
		self.stateTag: int = 0
		""" An incremental counter of modification on the resource. Assigned by the CSE. R/O. """
		
		self.dynamicAuthorizationConsultationIDs: list[str] = []
		""" A list of dynamic authorization consultation IDs. This might be an empty list. """
		
		self.announceTo: list[str] = []
		""" A list of URLs that point to the CSE(s) to which this resource is announced to,
			or an empty list. """
		
		self.announcedAttribute: list[str] = []
		""" A list of the announced attribute names of an original resource, 
			or an empty list. """

		super().__init__()


	def __str__(self) -> str:
		""" Return a string representation of the resource. 
		
			Returns:
				A string representation of the resource.
		"""
		return	INT.strResource('type', 'ty', str(self.type) + ' (' + self.namespace + ':' + self.typeShortName + ')') +\
				INT.strResource('resourceName', 'rn', self.resourceName) +\
				INT.strResource('resourceID', 'ri', self.resourceID) +\
				INT.strResource('parentID', 'pi', self.parentID) +\
				INT.strResource('originator', 'org', self.originator) + \
				INT.strResource('creationTime', 'ct', self.creationTime) + \
				INT.strResource('lastModifiedTime', 'lt', self.lastModifiedTime) + \
				INT.strResource('stateTag', 'st', self.stateTag) + \
				INT.strResource('labels', 'lbl', self.labels) + \
				INT.strResource('accessControlPolicyIDs', 'acpi', self.accessControlPolicyIDs) + \
				INT.strResource('expirationTime', 'et', self.expirationTime) + \
				INT.strResource('dynamicAuthorizationConsultationIDs', 'daci', self.dynamicAuthorizationConsultationIDs) + \
				INT.strResource('announceTo', 'at', self.announceTo) + \
				INT.strResource('announcedAttribute', 'aa', self.announcedAttribute)



	def setAccessControlPolicies(self, acps: Optional[AccessControlPolicy|list[AccessControlPolicy]] = None, 
							  		   overwrite: bool = True) -> None:
		"""	Set the &lt;ccessControlPolicy> resource ID(s) for a resource (if the resource type supports 
			AccessControlPolicies). 

			Args:
				acps: This could either be a single *AccessControlPolicies* object or a list of
					`AccessControlPolicy` objects. If *acps* is *None*, then the accessControlPolicies
					of this resource are set to an empty list.
				overwrite: If *True*, the existing accessControlPolicies are replaced. If *False*, the new
					accessControlPolicies are added to the existing ones.

			Raises:
				onem2mlib.exceptions.NotSupportedError: If the resource type doesn't support accessControlPolicies.
		"""
		if overwrite:
			self.accessControlPolicyIDs = []

		from .ContentInstance import ContentInstance

		if isinstance(self, ContentInstance):
			logger.error('Resource does not support AccessControlPolicies: ' + INT.nameAndType(self))
			raise EXC.NotSupportedError('Resource does not support AccessControlPolicies: ' + INT.nameAndType(self))

		if acps is not None:
			if not isinstance(acps, list):
				acps = [acps]
			else:
				for acp in acps:
					if acp.resourceID is not None:
						self.accessControlPolicyIDs.append(acp.resourceID)


	def addAccessControlPolicy(self, 
							   acps: Optional[AccessControlPolicy|list[AccessControlPolicy]] = None, 
							   overwrite: bool = True) -> None:
		"""	Update a ResourceBase's AccessControlPolicy.

			Args:
				acps: This could either be a single *AccessControlPolicies* object or a list of
					`AccessControlPolicy` objects. If *acps* is *None*, then the accessControlPolicies
					of this resource are set to an empty list.
				overwrite: If *True*, the existing accessControlPolicies are replaced. If *False*, the new
					accessControlPolicies are added to the existing ones.
		"""
		self.setAccessControlPolicies(acps, overwrite)
		self.updateAcpiInCSE()


	def retrieveFromCSE(self) -> bool:
		"""	Retrieve the resource from the &lt;CSEBase>. This object instance is updated accordingly. 

			Note:
				The `onem2mlib.ResourceBase.resourceID` state variable of the instance must be set to a valid value.

			Returns:
				The method returns *True* or *False*, depending on the success of the operation.
		"""
		try:
			return MCA.retrieveFromCSE(self, originator=self.originator)
		except EXC.CSEOperationError as e:
			return False


	def deleteFromCSE(self) -> bool:
		"""	Delete the resource and all its child-resources from the &lt;CSEBase>. 

			Returns:
				The method returns *True* or *False*, depending on the success of the operation.

			Raises:
				It may throw a `onem2mlib.exceptions.NotSupportedError` exception when the 
					operation is not supported by the resource type.
			Note:
				The `onem2mlib.ResourceBase.resourceID` state variable of the instance must be set to a valid value.
		"""
		if self.type in [CON.Type_CSEBase, CON.Type_RemoteCSE]: # not allowed
			logger.error(f"Resource doesn''t support deleting: {INT.nameAndType(self)}")
			raise EXC.NotSupportedError(f"Resource doesn''t support deleting: {INT.nameAndType(self)}")
		result = MCA.deleteFromCSE(self, originator=self.originator)
		if result and self.type == CON.Type_AE:
			# If an AE is deleted, we also clear the session's originator (if it is the same) 
			if self.session:
				if self.session.originator == self.originator:
					self.session.originator = None
				self.session = None
		return result


	def createInCSE(self) -> bool:
		"""	Create the resource in the <CSEBase>.

			Returns:
				The method returns *True* or *False*, depending on the success of the operation.
			
			Raises:
				It may throw a `onem2mlib.exceptions.NotSupportedError` exception when the operation is not supported by the resource type.

			Note:
				The `onem2mlib.ResourceBase.resourceID` state variable of the instance must be set to a valid value.
		"""
		
		# Add a default originator if this is an AE being created there is no
		# originator set for it.
		if self.type == CON.Type_AE and not self.originator:
			self.originator = 'C'

		if self.type in [CON.Type_CSEBase, CON.Type_RemoteCSE]: # not allowed
			logger.error(f"Resource doesn''t support creating: {INT.nameAndType(self)}")
			raise EXC.NotSupportedError(f"Resource doesn''t support creating: {INT.nameAndType(self)}")
		result = MCA.createInCSE(self, self.type, originator=self.originator)

		# The following is a special handling for the case when an AE is created directly under CSEBase 
		# with an incomplete session and an unknown originator. "incomplete session" means that the session 
		# doesn't have a valid originator and/or doesn't have a reference to the CSEBase.
		# After the AE has been created, we can update the session with the correct originator and CSEBase
		# and set the parent of the AE to the CSEBase. 
		if result and  self.type == CON.Type_AE:
			if self.session and not self.session.originator:
				self.session.originator = self.originator
			self.parent = self.session.getCSEBase()
		return result



	def updateInCSE(self, isAcpiUpdate: bool = False) -> bool:
		"""	Update the existing resource with new attributes.

			The method returns *True* or *False*, depending on the success of the operation.
			It may throw a `onem2mlib.exceptions.NotSupportedError` exception when the operation is not supported
			by the resource type.

			Args:
				isAcpiUpdate: If *True*, the update is for AccessControlPolicyIDs. This is needed to handle
					the special case of updating AccessControlPolicyIDs for a resource.

			Raises:
				onem2mlib.exceptions.NotSupportedError: If the resource type doesn't support updating.
				onem2mlib.exceptions.CSEOperationError: If the resource cannot be updated on the CSE.

			Note:
				The `onem2mlib.ResourceBase.resourceID` state variable of the instance must be set to a valid value.
		"""
		if self.type in [CON.Type_ContentInstance, CON.Type_CSEBase, CON.Type_RemoteCSE]: # not allowed
			logger.error(f"Resource doesn't support updating: {INT.nameAndType(self)}")
			raise EXC.NotSupportedError(f"Resource doesn't support updating: {INT.nameAndType(self)}")
		return MCA.updateInCSE(self, self.type, originator=self.originator, isAcpiUpdate=isAcpiUpdate)

	def updateAcpiInCSE(self) -> bool:
		"""	Update the existing resource with new attributes for AccessControlPolicyId.

			The method returns *True* or *False*, depending on the success of the operation.
			It may throw a `onem2mlib.exceptions.NotSupportedError` exception when the operation is not supported
			by the resource type.

			Returns:
				The method returns *True* or *False*, depending on the success of the operation.

			Note:
				The `onem2mlib.ResourceBase.resourceID` state variable of the instance must be set to a valid value.
		"""
		return self.updateInCSE(True)


	def get(self) -> bool:
		"""	Retrieve the resource from the &lt;CSEBase>, or create it if it doesn't exist.
			This object instance is updated accordingly. 

			Returns:
				The method returns *True* or *False*, depending on the success of the operation.

			Notes:
				The `onem2mlib.ResourceBase.resourceID` state variable of the instance must be set to a valid value.
		"""
		if self.resourceID:
			return self.retrieveFromCSE()
		if self.resourceName:
			if self.retrieveFromCSE():
				return True
		return self.createInCSE()


	def discover(self, filter: list[tuple[str, str|int|bool]], filterOperation: int = CON.Dsc_AND) -> list[ResourceBase]:
		"""	Discover a rsource on the CSE, starting with the resource as a root for discovery.

			Args:
				filter: These filter critera can be constructed using one of the
					*onem2mlib.utilties.new...FilterCriteria* functions.
				filterOperation: A boolean value that Indicates the logical operation (AND/OR) 
					to be used for different condition tags. The default value is logical AND.

			Returns:
				The method returns a list of found resources, or an empty list.

			Notes:
				Currently, only *label* and *resoureType* are supported in filters.
		"""

		# 1. Get the list of IDs (URIs) from the CSE
		rids = MCA.discoverInCSE(self, filter=filter, filterOperation=filterOperation)
		if rids is None:
			return []

		# 2. Convert each ID string into a real Python Resource object
		results = []
		for rid in rids:
			res = MCA.retrieveResourceByID(self, rid)
			if res:
				results.append(res)
		
		return results


	def subscribe(self, originator: Optional[str] = None, 
			   			callback: Optional[Callable] = None, 
						eventNotificationCriteria: Optional[EventNotificationCriteria] = None) -> bool:
		""" Create a <subscription> to resource and receive notifications. For this, the notification
			sub-module must be enabled, ie. `onem2mlib.notifications.setupNotifications` must have
			been called sucessfully. To stop notification from the resource and to remove the
			subscription, the `onem2mlib.ResourceBase.unsubscribe` method must be called.

			Args:
				originator: when doing a subscription from a different device, you have to specify the 
					X-Origin in order to be able to post.
				callback: An optional reference to a callback functions that is called when a
					notification is received for the subscription. If this argument is ommitted then the
					default callback function, provided with `onem2mlib.notifications.setupNotifications`,
					is called instead.
				eventNotificationCriteria: An optional `onem2mlib.datatypes.EventNotificationCriteria` 
					object to specify which events (create, update, delete, etc.) should trigger a notification.

			Returns:
				The method returns a Boolean indicating whether the subscription was successfull.

			Raises:
				onem2mlib.exceptions.NotSupportedError: If the resource type doesn't support subscriptions.
			
			Note:
				The <subsription> resource created with this method is only valid for the
				runtime of the calling program. The scubscription will be removed at least when the
				program terminates, or when `onem2mlib.notifications.shutdownNotifications` is called.
		"""
		if self.type not in NOT._allowedSubscriptionResources:
			logger.error('Subscription not supported for this resource type: ' + INT.nameAndType(self))
			raise EXC.NotSupportedError('Subscription not supported for this resource type: ' + INT.nameAndType(self))
		
		if not NOT.isNotificationEnabled():
			logger.warning('Notification module is not enabled. Call setupNotifications() first.')
			return False

		# Pass the eventNotificationCriteria through to the notifications module
		return NOT.addSubscription(
			self, 
			callback, 
			originator=originator, 
			eventNotificationCriteria=eventNotificationCriteria
		)

	def unsubscribe(self) -> bool:
		"""	Unsubscripte from the notifications of a resource. The subscription must have
			been created before with the `onem2mlib.ResourceBase.subscribe` method.

			Returns:
				The method returns a Boolean indicating whether the subscription was successfull.

			Raises:
				This method may throw a `onem2mlib.exceptions.NotSupportedError` exception in case
					the target resource type doesn't support subscriptions.

		"""
		if self.type not in NOT._allowedSubscriptionResources:
			logger.error('Subscription not supported for this resource type: ' + INT.nameAndType(self))
			raise EXC.NotSupportedError('Subscription not supported for this resource type: ' + INT.nameAndType(self))
		return NOT.removeSubscription(self)


	def subscriptions(self, filter: Optional[list[tuple[str, str|int|bool]]] = None) -> list[ResourceBase]:
		"""
		Return a list of &lt;subscription> resources of a rersource, or an empty list.

		This method might throw	a `onem2mlib.exceptions.NotSupportedError` exception in case
		the target resource type doesn't support subscriptions.
		"""
		if self.type not in NOT._allowedSubscriptionResources:
			logger.error('Subscription not supported for this resource type: ' + INT.nameAndType(self))
			raise EXC.NotSupportedError('Subscription not supported for this resource type')
		return INT._findSubResource(self, CON.Type_Subscription, filter=filter)


	def findAccessControlPolicy(self, resourceName: str) -> Optional[AccessControlPolicy]:
		"""	Find a specific <accessControlPolicy> resource by its *resourceName*, or None.

			Args:
				resourceName: The name of the resource to find. It could point to a 
					direct child-resource, or it can be a relative path pointing to a resource
					deeper down the resource tree. In that case the path elements are separated
					by '/' characters.
			
			Returns:
				The method returns the found `AccessControlPolicy` resource, or None if not found.
		"""
		return INT._getResourceFromCSEByResourceName(CON.Type_ACP, resourceName, self)	# type: ignore[return-value]


	def findAE(self, resourceName: str) -> Optional[AE]:
		"""	Find a specific <AE> resource by its *resourceName*, or None otherwise.

			Args:
				resourceName: The name of the resource to find. It could point to a 
					direct child-resource, or it can be a relative path pointing to a resource
					deeper down the resource tree. In that case the path elements are separated
					by '/' characters.
			
			Returns:
				The method returns the found `AE` resource, or None if not found.
		"""
		return INT._getResourceFromCSEByResourceName(CON.Type_AE, resourceName, self)	# type: ignore[return-value]


	def findContainer(self, resourceName: str) -> Optional[Container]:
		"""	Find a <container> resource by its *resourceName*, or None.

			Args:
				resourceName: The name of the resource to find. It could point to a 
					direct child-resource, or it can be a relative path pointing to a resource
					deeper down the resource tree. In that case the path elements are separated
					by '/' characters.
			
			Returns:
				The method returns the found `Container` resource, or None if not found.
		"""
		return INT._getResourceFromCSEByResourceName(CON.Type_Container, resourceName, self)	# type: ignore[return-value]


	def findContentInstance(self, resourceName: str) -> Optional[ContentInstance]:
		"""	Find a <ContentInstance> resource by its *resourceName*, or None.

			Args:
				resourceName: The name of the resource to find. It could point to a 
					direct child-resource, or it can be a relative path pointing to a resource
					deeper down the resource tree. In that case the path elements are separated
					by '/' characters.

			Returns:
				The method returns the found `ContentInstance` resource, or None if not found.
		"""
		return INT._getResourceFromCSEByResourceName(CON.Type_ContentInstance, resourceName, self)	# type: ignore[return-value]


	def findGroup(self, resourceName: str) -> Optional[Group]:
		"""	Find a specific <group> resource by its *resourceName*, or None.

			Args:
				resourceName: The name of the resource to find. It could point to a 
					direct child-resource, or it can be a relative path pointing to a resource
					deeper down the resource tree. In that case the path elements are separated
					by '/' characters.
			
			Returns:
				The method returns the found `Group` resource, or None if not found.
		"""
		return INT._getResourceFromCSEByResourceName(CON.Type_Group, resourceName, self)	# type: ignore[return-value]


	def findRemoteCSE(self, resourceName: str) -> Optional[RemoteCSE]:
		"""	Find a specific <remoteCSE> resource by its *resourceName*, or None.

			Args:
				resourceName: The name of the resource to find. It could point to a 
					direct child-resource, or it can be a relative path pointing to a resource
					deeper down the resource tree. In that case the path elements are separated
					by '/' characters.
			
			Returns:
				The method returns the found `RemoteCSE` resource, or None if not found.
		"""
		return INT._getResourceFromCSEByResourceName(CON.Type_RemoteCSE, resourceName, self)	# type: ignore[return-value]


	def findSubscription(self, resourceName: str) -> Optional[Subscription]:
		"""	Find a specific <subscription> resource by its *resourceName*, or None otherwise.

			Args:
				resourceName: The name of the resource to find. It could point to a 
					direct child-resource, or it can be a relative path pointing to a resource
					deeper down the resource tree. In that case the path elements are separated
					by '/' characters.
			
			Returns:
				The method returns the found `Subscription` resource, or None if not found.
		"""
		return INT._getResourceFromCSEByResourceName(CON.Type_Subscription, resourceName, self)	# type: ignore[return-value]



	def _prefixResourceIDAbsolute(self) -> str:
		""" Returns the absolute prefix of the CSE-ID, or None if not available. 
		
			Returns:
				The absolute prefix of the CSE-ID, or None if not available.
		"""
		# returns absolute prefix or None
		if hasattr(self, 'cseID') and self.cseID:
			return f"//{self.cseID.lstrip('/')}"
		return None

	def _prefixResourceIDSPRelative(self) -> str:
		# returns SP relative prefix or None
		if self.resourceID:
			return f"/{self.resourceID.lstrip('/')}"
		return None

	def _prefixResourceIDCSERelative(self) -> str:
		# returns CSE relative path (empty string)
		return ''

	def _unstructuredResourceID(self, withRIScope: bool = False) -> str:
		ri = self.resourceID.lstrip('/')
		
		if not withRIScope:
			return ri

		# Find the root 
		root = self
		while hasattr(root, 'parent') and root.parent is not None:
			root = root.parent
		
		# Determine base prefix based on root type
		if root.type == CON.Type_RemoteCSE:
			base = root._prefixResourceIDAbsolute()
		elif root.type == CON.Type_CSEBase:
			base = root._prefixResourceIDSPRelative() or root._prefixResourceIDCSERelative()
		else:
			base = ''
			
		prefix = (base or '').rstrip('/')
		return f"{prefix}/{ri}"

	def _structuredResourceID(self, withRIScope: bool = False) -> str:
		# Handle RemoteCSE case
		if self.type == CON.Type_RemoteCSE:
			if not withRIScope:
				return self.resourceName
			prefix = self._prefixResourceIDAbsolute()
			return f"{(prefix or '')}/{self.resourceName}"
			
		# Handle CSEBase case
		if self.type == CON.Type_CSEBase:
			if not withRIScope:
				return self.resourceName
			prefix = self._prefixResourceIDSPRelative() or self._prefixResourceIDCSERelative()
			return f"{(prefix or '')}/{self.resourceName}"
				
		return f"{self.parent._structuredResourceID(withRIScope)}/{self.resourceName}"

	def _createContent(self, isUpdate: bool = False, isAcpiUpdate: bool = False) -> Optional[str]:
		return json.dumps(self._toCSE(isUpdate, isAcpiUpdate))


	def _copy(self, resource: ResourceBase) -> None:
		""" Copy the common attributes of a resource to this instance.
		
			Args:
				resource: The resource from which to copy the attributes.
		"""
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


	def _fromCSE(self, jsn: dict) -> dict:
		""" Update the state variables of this instance from a JSON representation of the resource, as returned by the CSE.

			Args:
				jsn: The JSON representation of the resource as a dictionary.

			Returns:
				The method returns the JSON representation of the resource as a dictionary, but only the resopurce part, i.e. the part under the resource type key. 
		"""
		name = self.namespace + ':' + self.typeShortName
		if name not in jsn:
			logger.error('Wrong encoding: ' + str(jsn))
			raise EXC.EncodingError('Wrong encoding: ' + str(jsn))
		_jsn = jsn[name]
		self.resourceName = INT.getElementJSON(_jsn, 'rn', self.resourceName)
		self.type = INT.getElementJSON(_jsn, 'ty', self.type)
		self.stateTag = INT.toInt(INT.getElementJSON(_jsn, 'st', self.stateTag))
		self.labels = INT.getElementJSON(_jsn, 'lbl', self.labels)
		self.resourceID = INT.getElementJSON(_jsn, 'ri', self.resourceID)
		self.parentID = INT.getElementJSON(_jsn, 'pi', self.parentID)
		self.creationTime = INT.getElementJSON(_jsn, 'ct', self.creationTime)
		self.lastModifiedTime = INT.getElementJSON(_jsn, 'lt', self.lastModifiedTime)
		self.accessControlPolicyIDs = INT.getElementJSON(_jsn, 'acpi', self.accessControlPolicyIDs)
		self.expirationTime = INT.getElementJSON(_jsn, 'et', self.expirationTime)
		self.announceTo = INT.getElementJSON(_jsn, 'at', self.announceTo)
		self.announcedAttribute = INT.getElementJSON(_jsn, 'aa', self.announcedAttribute)
		return _jsn


	def _toCSE(self, isUpdate: bool = False, isAcpiUpdate: bool = False) -> dict:
		""" Create a JSON representation of the resource for creating or updating the resource in the CSE.

			Args:
				isUpdate: If *True*, the JSON representation is created for an update operation. 
				isAcpiUpdate: If *True*, the JSON representation is created for an update operation for
					AccessControlPolicyIDs. This is needed to handle the special case of updating
					AccessControlPolicyIDs for a resource.

			Returns:
				The method returns the JSON representation of the resource as a dictionary.
		"""
		jsn: dict = {}
		if isUpdate and isAcpiUpdate:
			INT.addToElementJSON(jsn, 'acpi', self.accessControlPolicyIDs)
			return jsn
		if self.resourceName and not isUpdate: 	# No RN when updating
			INT.addToElementJSON(jsn, 'rn', self.resourceName)
		INT.addToElementJSON(jsn, 'lbl', self.labels)
		INT.addToElementJSON(jsn, 'aa', self.announcedAttribute)
		INT.addToElementJSON(jsn, 'at', self.announceTo)
		INT.addToElementJSON(jsn, 'acpi', self.accessControlPolicyIDs)
		return jsn

