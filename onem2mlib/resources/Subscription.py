#
#	Subscription.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module implements the class for the <subscription> resource.
#

import logging
import onem2mlib.marshalling as M
import onem2mlib.constants as CON
import onem2mlib.internal as INT
import onem2mlib.mcarequests as MCA
import onem2mlib.exceptions as EXC
import onem2mlib.datatypes as DTY
from .ResourceBase import ResourceBase

logger = logging.getLogger(__name__)

class Subscription(ResourceBase):
	"""
	This class implements the oneM2M <subscription> resource. 

	It is used to manage targets for notifications sent whenever a subscribed-to resource
	is changed.
	"""

	def __init__(self,
                 notificationURI: list[str] | None = None,
                 eventNotificationCriteria: DTY.EventNotificationCriteria | None = None,
                 instantly: bool = True,
                 **kwargs):
		"""
		Initialize the <subscription> resource. 

		Args:
			notificationURI: List of targets for notifications.
			eventNotificationCriteria: Criteria for triggering notifications.
			instantly: If True, the resource is immediately synced with the CSE.
			**kwargs: Inherited attributes (parent, resourceName, labels, originator, etc.)
		"""
		# 1. Initialize Base Class
		super().__init__(type=CON.Type_Subscription, typeShortName=CON.Type_Subscription_SN, **kwargs)
		
		# 2. Set Marshallers
		self._marshallers = [M._Subscription_parseXML, M._Subscription_createXML,
							 M._Subscription_parseJSON, M._Subscription_createJSON]

		# 3. Set Subscription-Specific Attributes
		self.notificationURI = notificationURI if notificationURI is not None else []
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

		self.eventNotificationCriteria = eventNotificationCriteria
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


	def __str__(self):
		result = 'Subscription:\n'
		result += super().__str__()
		result += INT.strResource('notificationURI', 'nu', self.notificationURI)
		result += INT.strResource('notificationContentType', 'nct', self.notificationContentType)
		
		if self.expirationCounter != -1:
			result += INT.strResource('expirationCounter', 'exc', self.expirationCounter)
		if self.latestNotify is not None:
			result += INT.strResource('latestNotify', 'ln', self.latestNotify)
		if self.groupID:
			result += INT.strResource('groupID', 'gpi', self.groupID)
		if self.notificationForwardingURI:
			result += INT.strResource('notificationForwardingURI', 'nfu', self.notificationForwardingURI)
		if self.eventNotificationCriteria:
			result += INT.strResource('eventNotificationCriteria', 'enc', str(self.eventNotificationCriteria))
		if self.subscriberURI:
			result += INT.strResource('subscriberURI', 'su', self.subscriberURI)
		return result


	def _copy(self, resource: 'Subscription'):
		"""
		Copy attributes from another Subscription resource instance.
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