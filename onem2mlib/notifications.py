#
#	notifications.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
"""	This sub-module defines the end-point and server for notifications as well as support
functions to handle and manage notifications from CSE resources.

Before receiving notifications, one must setup the notification sub-module by calling
the `onem2mlib.notifications.setupNotifications` method. This starts also an http server
that receives notifications from the respective CSE.

One can provide callback functions, either for general handling, or specific for each
subscription. The callback function must have the form ``function(resource)`` where
*resource* is the changed resource from the notification. It is up to this callback function
to determine the correct type by consulting the `onem2mlib.ResourceBase.type` attribute.

A program can now subscribe to resources by calling the `onem2mlib.ResourceBase.subscribe`
method. It is notified through the callback function every time that resource is modified.

The sub-module is shutdown by calling `onem2mlib.notifications.shutdownNotifications`.
This method also automatically shuts down the server when the parent program terminates.
"""

from __future__ import annotations
from typing import Optional, Tuple, Any, Callable, TYPE_CHECKING

import atexit, threading, json, logging

from http.server import BaseHTTPRequestHandler, HTTPServer

from . import exceptions as EXC
from . import constants as CON
from . import internal as INT

if TYPE_CHECKING:
	from .resources.ResourceBase import ResourceBase
	from .resources.Subscription import Subscription


_isEnabled = False
_host = None
_port = -1
_callback = None
_notificationURI = None

logger = logging.getLogger(__name__)

_allowedSubscriptionResources = [
	CON.Type_CSEBase,
	CON.Type_AE,
	CON.Type_ACP,
	CON.Type_Container,
	CON.Type_Group,
	CON.Type_RemoteCSE
]

def setupNotifications(callback: Callable = None, host: str = 'localhost', port: int = 1400) -> bool:
	"""	Setup the notification sub-module. This also starts a http server listening on the
		specified interface and port.

		Args:
			host: The interface on which the http server will listen. Optional, the default is 'localhost'.
			port: The port on which the http server will listen. Optional, the default is 1400.
			callback: A reference to a function that is called whenever a valid notification
				is receiced. This function will receive the notification's resource as the only argument.
				This callback function is only a default and can be overriden by the callback function
				in the `onem2mlib.ResourceBase.subscribe` method.

		Returns:	
			The function returns a Boolean value that indicates whether the notification sub-module
				was successfully started.

		Raises:
			onem2mlib.exceptions.ConfigurationError: If the host or port parameters are missing or invalid.
	"""
	global _host, _port, _callback, _notificationURI

	if _notificationURI:
		return True
	
	if not host:
		logger.critical('enableNotifications(): Missing host.')
		raise EXC.ConfigurationError('enableNotifications(): Missing host.')
	if port == -1:
		logger.critical('enableNotifications(): Missing port.')
		raise EXC.ConfigurationError('enableNotifications(): Missing port.')

	_host = host
	_port = port
	_callback = callback
	_notificationURI = f'http://{_host}:{_port}'
	_startNotificationServer()
	enableNotifications()
	return True

def enableNotifications() -> None:
	"""	Enable the notification handling again, after disabling them with the 
		`onem2mlib.notifications.disableNotifications` method.
	"""
	global _isEnabled
	_isEnabled = True
	
def disableNotifications() -> None:
	"""	Disable the notification handling for a short time. This does **not** shut down the
		http server or removes subscriptions from resources in the CSE. It just stops the 
		processing of notifications and the calling of the callback functions.

		Processing and callback can be re-enabled with the `onem2mlib.notifications.enableNotifications`
		method.
	"""
	global _isEnabled
	_isEnabled = False

@atexit.register
def shutdownNotifications() -> None:
	""" Shutdown the notification sub-module and the http server. It also removes subscriptions
		created through the `onem2mlib.ResourceBase.subscribe` method. After this no more 
		notifications can be received through the sub-module.

		Note:	
			This function is automatically called when the parent program terminates.
	"""
	global _notificationURI
	if not _notificationURI:
		return
	try:
		removeAllSubscriptions()
	except Exception as e:
		logger.warning('Failed to remove subscriptions during shutdown: ' + str(e))
	disableNotifications()
	_notificationURI = None
	_stopNotificationServer()

def isNotificationEnabled() -> bool:
	""" Check whether the notification handling is currently enabled.

		Returns:
			Return the status whether notifications are currently enabled. 
	"""
	return _isEnabled

def getNotificationURI() -> str	:
	""" Return the current notificationURI, or None when notifications are disabled. 

		Returns:
			The notification URI as a string, or None if notifications are not setup.
	"""
	return _notificationURI

###############################################################################
#	Handling temporary subscriptions / notifications

_subscriptions: dict[str, Tuple[ResourceBase, ResourceBase, Callable]] = {}
"""	Internal data structure to hold the subscriptions that are created through 
	the `onem2mlib.ResourceBase.subscribe` method. The keys are the resourceIDs of the 
	subscribed-to resources, and the values are tuples of the form 
	(subscriptionResource, parentResource, callback). """

_subscriptionIDToParentResourceID: dict[str, str] = {}
"""	Internal data structure to map subscription resourceIDs to their parent resourceIDs.
	The keys are the resourceIDs of the subscription resources, and the values are the resourceIDs
	of the parent resources."""

def addSubscription(resource: ResourceBase, 
					callback: Callable = None, 
					originator: str = None, 
					eventNotificationCriteria: Any = None) -> bool:
	"""	Add a subscription to the given resource. This creates a <subscription> resource for
		that resource.

		This method might throw	a `onem2mlib.exceptions.NotSupportedError` exception in case
		the target resource type doesn't support subscriptions.

		Args:
			resource: Resource to add the resource to.
			callback: Optional reference to a callback function. This function is called instead of
				the one provided with the `onem2mlib.notifications.setupNotifications` function.
			originator: when doing a subscription from a different device, you have to specify the 
				X-Origin in order to be able to post.

		Returns:
			The method returns a Boolean indicating whether the subscription was successfully added.
		
		Raises:
			onem2mlib.exceptions.NotSupportedError: If the resource type doesn't support subscriptions.
			onem2mlib.exceptions.CSEOperationError: If the subscription resource cannot be created on the CSE.
	"""
	if resource.resourceID in _subscriptions:
		return True
	if resource.type not in _allowedSubscriptionResources:
		logger.error('Subscription not supported for this resource type: ' + INT.nameAndType(resource))
		raise EXC.NotSupportedError('Subscription not supported for this resource type.')
	
	# Create the Subscription resource with the optional ENC
	from .resources.Subscription import Subscription
	sub = Subscription(
		parent=resource, 
		notificationURI=[_notificationURI], 
		originator=originator, 
		eventNotificationCriteria=eventNotificationCriteria
	)
	
	if not sub:
		return False
	_addSubscription(resource, sub, callback)
	return True

def removeSubscription(resource: ResourceBase) -> bool:
	"""	Remove a subscription added prior by the `onem2mlib.notifications.addSubscription`
		method. After calling this function no notifications for that resource are received
		or processed anymore.

		Args:
			resource: The resource from which the subscription should be removed.

		Returns:
			The method returns a Boolean indicating whether the subscription was successfully removed.
	"""
	if not resource or not resource.resourceID:
		return False
	return _removeSubscriptionByID(resource.resourceID)

def hasSubscription(resource: ResourceBase) -> bool:
	"""	Check whether a resource has a subscription attached, which is managed by the notification sub-service.
	
		Args:
			resource: The resource to check.

		Returns:
			The method returns a Boolean indicating whether the resource is managed and
				has a subscription attached.
	"""
	if not resource or not resource.resourceID:
		return False
	return resource.resourceID in _subscriptions

# Add a subscription to the internal data strucures
def _addSubscription(resource: ResourceBase, sub: Subscription, callback: Callable = None) -> None:
	"""	Add a subscription to the internal data structures.

		Args:
			resource: The resource to which the subscription is attached.
			sub: The subscription resource that is created for the resource.
			callback: Optional reference to a callback function. This function is called instead of
				the one provided with the `onem2mlib.notifications.setupNotifications` function.
	"""
	_subscriptions[resource.resourceID] = (sub, resource, callback)
	_subscriptionIDToParentResourceID[sub.resourceID] = resource.resourceID
	_subscriptionIDToParentResourceID[sub._structuredResourceID(withRIScope=True)] = resource.resourceID

# Remove a subscription from the internal data structures
def _removeSubscriptionByID(resourceID: str) -> bool:
	"""	Remove a subscription by the resourceID of the subscribed-to resource. This is used internally
		to remove subscriptions.

		Args:
			resourceID: The resourceID of the subscribed-to resource.

		Returns:
			A Boolean indicating whether the subscription was successfully removed.
	"""
	if resourceID not in _subscriptions: 
		return False
	(sub, _, _) = _subscriptions.pop(resourceID)
	_subscriptionIDToParentResourceID.pop(sub.resourceID, None)
	_subscriptionIDToParentResourceID.pop(sub._structuredResourceID(withRIScope=True), None)
	return sub.deleteFromCSE()


def removeAllSubscriptions() -> None:
	"""	Remove all the subscriptions that have been added through the 
		`onem2mlib.notifications.addSubscription` function.
	"""
	keys = list(_subscriptions.keys())
	for k in keys:
		_removeSubscriptionByID(k)

###############################################################################
#	Notification callback server
#
#	This is actually a simple HTTP server
#

_server = None
_thread = None


# Start the notification server in a background thread
def _startNotificationServer() -> None:
	global _server, _thread
	if _thread:
		return
	# Start processing requests in a separate thread.
	# Listen on any interface/IP address.
	# TODO: Make this configurable
	_server = HTTPNotificationServer(('', _port), HTTPNotificationHandler)
	_thread = threading.Thread(target=_server.run)
	_thread.daemon = True
	_thread.start()


# Stop the thread/notification server
def _stopNotificationServer() -> None:
	global _server, _thread
	if not _server or not _thread:
		return
	# Shutdown server
	_server.shutdown()
	_thread.join()
	_server = None
	_thread = None



# This class implements the notification server that runs in the background.
class HTTPNotificationServer(HTTPServer):
	def run(self) -> None:
		try:
			self.serve_forever()
		finally:
			self.server_close()


# This class implements the handler that reseives the requests
class HTTPNotificationHandler(BaseHTTPRequestHandler):
	def do_POST(self) -> None:
		# Send response first (oneM2M requires 200 OK fast)
		requestIdentifier = self.headers.get('X-M2M-RI', 'unknown')
		self.send_response(200)
		self.send_header('X-M2M-RSC', '2000')
		self.send_header('X-M2M-RI', requestIdentifier)
		self.end_headers()

		length = int(self.headers.get('Content-Length', 0))
		contentType = self.headers.get('Content-Type', '')
		post_data = self.rfile.read(length)

		if _isEnabled:
			if contentType.lower().startswith('application/json'):
				threading.Thread(target=self._handleJSON, args=(post_data,)).start()
			else:
				raise EXC.NotSupportedError('Unsupported content type for notification: ' + contentType)

	def log_message(self, format: str, *args: Any) -> None:
		return


	def _handleJSON(self, data: bytes) -> None:
		raw_jsn = json.loads(data.decode('utf-8'))
		
		# Verification Request check
		vrq = INT.getALLSubElementsJSON(raw_jsn, 'vrq') or INT.getALLSubElementsJSON(raw_jsn, 'm2m:vrq')
		if vrq and vrq[0] is True: return

		sgn = INT.getElementJSON(raw_jsn, 'm2m:sgn', default={})
		nev = INT.getElementJSON(sgn, 'nev', default={})
		event_type = INT.getElementJSON(nev, 'net')
		
		sur = INT.getElementJSON(sgn, 'sur') or INT.getElementJSON(raw_jsn, 'm2m:sur')
		if isinstance(sur, list) and len(sur) > 0: sur = sur[0]
		if not sur: return

		rep = INT.getALLSubElementsJSON(raw_jsn, 'rep') or INT.getALLSubElementsJSON(raw_jsn, 'm2m:rep')
		resource = None
		if rep:
			res_jsn = rep[0]
			ty_list = INT.getALLSubElementsJSON(res_jsn, 'ty')
			if ty_list:
				resource = INT._newResourceFromType(ty_list[0], None)
				resource._parseJSON(res_jsn)
		
		self._callCallback(resource, sur, event_type, raw_jsn)

	def _callCallback(self, resource: ResourceBase, 
							sur: str, 
							eventType: Optional[str] = None, 
							jsn: Optional[dict] = None) -> None:
		"""	Find the appropriate subscription and prepares the notification context.

			Args:
				resource: The resource that is changed and caused the notification.
				sur: The subscription resourceID from the notification.
				eventType: The event type from the notification, if available.
				jsn: The full JSON from the notification, if available.
		"""
		parentResourceID = None
		if sur in _subscriptionIDToParentResourceID:
			parentResourceID = _subscriptionIDToParentResourceID[sur]
		else:
			for key in _subscriptionIDToParentResourceID.keys():
				if sur.endswith(key) or key.endswith(sur):
					parentResourceID = _subscriptionIDToParentResourceID[key]
					break

		notification_context = {
			'resource': resource,
			'event_type': eventType,
			'jsn': jsn,
			'subscription_id': sur
		}

		# If we don't know the subscription, try the global default
		if not parentResourceID or parentResourceID not in _subscriptions:
			if _callback: 
				self._safe_execute_callback(_callback, **notification_context)
			return

		(_, _, callback) = _subscriptions[parentResourceID]
		target_callback = callback if callback else _callback
		
		if target_callback:
			self._safe_execute_callback(target_callback, **notification_context)

	def _safe_execute_callback(self, func: Callable, **kwargs: Any) -> None:
		"""	Standardized callback executor. 

			A callback function can have different signatures, but the most common one is 
			``function(resource, event_type, jsn, **kwargs)``. However, for simplicity, it 
			can also just have the signature ``function(resource)``.

			Args:
				func: The callback function to execute.
				**kwargs: The context data to pass to the callback function. This can include
					the resource, event type, full JSON, subscription ID, etc.
		"""
		try:
			# Attempt to pass all context data
			return func(**kwargs)
		except TypeError as e:
			# If it failed because of the signature, try passing ONLY the resource
			# Note: We check the error message to ensure we don't swallow 
			# TypeErrors occurring INSIDE the function logic.
			if "unexpected keyword argument" in str(e) or "positional argument" in str(e):
				try:
					return func(kwargs.get('resource'))
				except Exception as inner_e:
					logger.error(f"Error in simplified notification callback: {inner_e}")
			else:
				logger.error(f"Logic error inside notification callback: {e}")
