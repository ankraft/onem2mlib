#
#	Subscription.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
""" This module implements the class for the <subscription> resource. """

from __future__ import annotations
from typing import Optional, Any, override

import logging

from .. import constants as CON
from .. import internal as INT
from .. import mcarequests as MCA
from .. import exceptions as EXC
from .. import datatypes as DTY
from .ResourceBase import ResourceBase

logger = logging.getLogger(__name__)
""" Logger for this module. """

class Subscription(ResourceBase):
	"""	This class implements the oneM2M <subscription> resource. 
		
		It is used to manage targets for notifications sent whenever a subscribed-to resource
		is changed.
	"""

	def __init__(self,
                 notificationURI: Optional[list[str]] = None,
                 eventNotificationCriteria: Optional[DTY.EventNotificationCriteria] = None,
                 instantly: bool = True,
                 **kwargs: Any) -> None:
		"""	Initialize the <subscription> resource. 

			Args:
				notificationURI: List of targets for notifications.
				eventNotificationCriteria: Criteria for triggering notifications.
				instantly: If True, the resource is immediately synced with the CSE.
				**kwargs: Inherited attributes (parent, resourceName, labels, originator, etc.)
		"""
		# Initialize Base Class
		super().__init__(type=CON.Type_Subscription, typeShortName=CON.Type_Subscription_SN, **kwargs)
		
		# Set Subscription-Specific Attributes
		self.notificationURI = notificationURI if notificationURI is not None else []
		"""	A list consisting of one or more targets that the Hosting CSE shall send notifications to. 
			A target is either a oneM2M compliant Resource-ID (either structured or unstructured),
			or as a URL with one of oneM2M supported protocol binding, e.g. http.
		"""

		self.notificationContentType = CON.Sub_AllAttributes
		"""	This attribute indicates a notification content type that shall be contained in
			notifications. The allowed values are one of the following constants:

			- Sub_AllAttributes (the default)
			- Sub_ModefiedAttributes
			- Sub_ResourceID 
		"""

		self.expirationCounter = -1
		"""	This attribute indicates that the life of this subscription is set to a limit of a
			maximum number of notifications. After thix maximum number is reached, the subscription
			is deleted.
		"""

		self.latestNotify = None
		"""	This attribute indicates if the subscriber wants only the latest notification. 
			If multiple notifications of this subscription are buffered, and if the value of
			this attribute is set to true, then only the last notification shall be sent and 
			it shall have the Event Category value set to "latest".
		"""

		self.groupID = None
		"""	This attribute indicates the ID of a <group> resource in case the subscription is made through a group.	"""
	
		self.notificationForwardingURI = None
		"""	This attribute is a forwarding attribute that is present only for group related 
			subscriptions. It represents the resource subscriber notificationtarget. 
		"""

		self.subscriberURI = None
		"""	This attribute is configured with the target of the subscriber. The target is used by the
			CSE to determine where to send a notification when the subscription is deleted. 
			A target is either a oneM2M compliant Resource-ID (either structured or unstructured),
			or as a URL with one of oneM2M supported protocol binding, e.g. http.
		"""

		self.eventNotificationCriteria: DTY.EventNotificationCriteria = eventNotificationCriteria
		"""	This attribute represents the criteria for triggering notifications. """
		if not self.eventNotificationCriteria:
			self.eventNotificationCriteria = DTY.EventNotificationCriteria()
			self.eventNotificationCriteria.notificationEventType = [1, 2, 3, 4]

		# TODO: determine NotificationURi automatically
		#if not self.notificationURI or len(self.notificationURI) == 0:
		#	self.notificationURI = [ 'http://localhost:1400' + '?ri=' + parent.resourceID + '&nonce=' + str(uuid.uuid4().hex) ]

		if instantly:
			if not self.get():
				logger.error(f'Cannot get or create Subscription. {MCA.lastError}')
				raise EXC.CSEOperationError(f'Cannot get or create Subscription. {MCA.lastError}')


	def __str__(self) -> str:
		return	'Subscription:\n' + \
				super().__str__() + \
			    INT.strResource('notificationURI', 'nu', self.notificationURI) + \
			    INT.strResource('notificationContentType', 'nct', self.notificationContentType) + \
			    f"{INT.strResource('expirationCounter', 'exc', self.expirationCounter) if self.expirationCounter != -1 else ''}" + \
			    f"{INT.strResource('latestNotify', 'ln', self.latestNotify) if self.latestNotify is not None else ''}" + \
			    f"{INT.strResource('groupID', 'gpi', self.groupID) if self.groupID else ''}" + \
			    f"{INT.strResource('notificationForwardingURI', 'nfu', self.notificationForwardingURI) if self.notificationForwardingURI else ''}" + \
			    f"{INT.strResource('eventNotificationCriteria', 'enc', str(self.eventNotificationCriteria)) if self.eventNotificationCriteria else ''}" + \
			    f"{INT.strResource('subscriberURI', 'su', self.subscriberURI) if self.subscriberURI else ''}"


	@override
	def _copy(self, resource: Subscription) -> None:	# type: ignore[override]
		"""	Copy attributes from another Subscription resource instance.

			Args:
				resource: The Subscription resource instance to copy from.
		"""
		super()._copy(resource)
		self.notificationURI = resource.notificationURI.copy() if resource.notificationURI else []
		self.notificationContentType = resource.notificationContentType
		self.expirationCounter = resource.expirationCounter
		self.latestNotify = resource.latestNotify
		self.groupID = resource.groupID
		self.notificationForwardingURI = resource.notificationForwardingURI
		self.subscriberURI = resource.subscriberURI
		self.eventNotificationCriteria = resource.eventNotificationCriteria


	def _fromCSE(self, jsn: dict) -> None:
		""" Update the attributes of this Subscription resource from a JSON representation.

				Args:
					jsn: The JSON representation of the resource as a dictionary.
		"""
		_jsn = super()._fromCSE(jsn)
		self.notificationURI = INT.getElementJSON(_jsn, 'nu', self.notificationURI)
		self.notificationContentType = INT.getElementJSON(_jsn, 'nct', self.notificationContentType)
		self.expirationCounter = INT.getElementJSON(_jsn, 'exc', self.expirationCounter)
		self.latestNotify = INT.getElementJSON(_jsn, 'ln', self.latestNotify)
		self.groupID = INT.getElementJSON(_jsn, 'gpi', self.groupID)
		self.notificationForwardingURI = INT.getElementJSON(_jsn, 'nfu', self.notificationForwardingURI)
		self.subscriberURI = INT.getElementJSON(_jsn, 'su', self.subscriberURI)
		enc_jsn = INT.getElementJSON(_jsn, 'enc')
		if enc_jsn and self.eventNotificationCriteria:
			self.eventNotificationCriteria._fromCSE(enc_jsn)


	def _toCSE(self, isUpdate: bool = False, isAcpiUpdate: bool = False) -> dict:
		""" Return a JSON representation of this Group resource as a dictionary, to be sent to the CSE.

			Args:
				isUpdate: If True, this JSON is for an update operation.
				isAcpiUpdate: If True, this JSON is for an ACP update operation.
				
			Returns:
				A JSON representation of this Group resource as a dictionary, to be sent to the CSE.
		"""
		jsn = super()._toCSE(isUpdate, isAcpiUpdate)
		if isUpdate and isAcpiUpdate:
			return INT.wrapJSON(self, jsn)
		INT.addToElementJSON(jsn, 'nu', self.notificationURI)
		INT.addToElementJSON(jsn, 'nct', self.notificationContentType)
		if self.expirationCounter != -1:
			INT.addToElementJSON(jsn, 'exc', self.expirationCounter)
		if self.latestNotify:
			INT.addToElementJSON(jsn, 'ln', self.latestNotify)
		if self.groupID:
			INT.addToElementJSON(jsn, 'gpi', self.groupID)
		if self.notificationForwardingURI:
			INT.addToElementJSON(jsn, 'nfu', self.notificationForwardingURI)
		if self.subscriberURI:
			INT.addToElementJSON(jsn, 'su', self.subscriberURI)
		if self.eventNotificationCriteria:
			jsn['enc'] = self.eventNotificationCriteria._toCSE(isUpdate)
		return INT.wrapJSON(self, jsn)
