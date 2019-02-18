#
#	Subscription.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module implements the class for the &lt;Subscription> resource.
#

import logging
import onem2mlib.marshalling as M
from .ResourceBase import *

logger = logging.getLogger(__name__)


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
	
		ResourceBase.__init__(self, parent, resourceName, resourceID, CON.Type_Subscription, CON.Type_Subscription_SN, labels=labels)
		self._marshallers = [M._Subscription_parseXML, M._Subscription_createXML,
							 M._Subscription_parseJSON, M._Subscription_createJSON]

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
				logger.error('Cannot get or create Subscription. '  + MCA.lastError)
				raise EXC.CSEOperationError('Cannot get or create Subscription. '  + MCA.lastError)


	def __str__(self):
		result = 'Subscription:\n'
		result += ResourceBase.__str__(self)
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


	def _copy(self, resource):
		ResourceBase._copy(self, resource)
		self.notificationURI = resource.notificationURI
		self.notificationContentType = resource.notificationContentType
		self.expirationCounter = resource.expirationCounter
		self.latestNotify = resource.latestNotify
		self.groupID = resource.groupID
		self.notificationForwardingURI = resource.notificationForwardingURI
		self.subscriberURI = resource.self.subscriberURI

