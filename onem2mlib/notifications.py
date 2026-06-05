#
#	notifications.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This sub-module defines the end-point and server for notifications as well
#	support functions.
#

"""
This sub-module defines the end-point and server for notifications as well as support
functions to handle and manage notifications from CSE resources.

Before receiving notifications, one must setup the notification sub-module by calling
the `onem2mlib.notifications.setupNotifications`() method. This starts also an http server
that receives notifications from the respective CSE.

One can provide callback functions, either for general handling, or specific for each
subscription. The callback function must have the form ``function(resource)`` where
*resource* is the changed resource from the notification. It is up to this callback function
to determine the correct type by consulting the `onem2mlib.ResourceBase.type` attribute.

A program can now subscribe to resources by calling the `onem2mlib.ResourceBase.subscribe`()
method. It is notified through the callback function every time that resource is modified.

The sub-module is shutdown by calling `onem2mlib.notifications.shutdownNotifications`().
This method also automatically shuts down the server when the parent program terminates.
"""

import atexit, threading, json, logging

try:
	from http.server import BaseHTTPRequestHandler, HTTPServer
except ImportError:
	from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

import onem2mlib
import onem2mlib.exceptions as EXC
import onem2mlib.constants as CON
import onem2mlib.internal as INT

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

def setupNotifications(callback=None, host='localhost', port=1400):
	"""
	Setup the notification sub-module. This also starts a http server listening on the
	specified interface and port.

	Args:

	- *host*: String. The interface on which the http server will listen. Optional, the
	default is 'localhost'.
	- *port*: Integer. The port on which the http server will listen. Optional, the
	default is 1400.
	- *callback*: A reference to a function that is called whenever a valid notification
	is receiced. This function will receive the notification's resource as the only argument.
	This callback function is only a default and can be overriden by the callback function
	in the `onem2mlib.ResourceBase.subscribe`() method.

	The function returns a Boolean value that indicates whether the notification sub-module
	was successfully started.
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
	_notificationURI = 'http://' + _host + ':' + str(_port)
	_startNotificationServer()
	enableNotifications()
	return True

def enableNotifications():
	"""
	Enable the notification handling again, after disabling them with the
	`onem2mlib.notifications.disableNotifications`() method.
	"""
	global _isEnabled
	_isEnabled = True
	
def disableNotifications():
	"""
	Disable the notification handling for a short time. This does **not** shut down the
	http server or removes subscriptions from resources in the CSE. It just stops the 
	processing of notifications and the calling of the callback functions.

	Processing and callback can be re-enabled with the `onem2mlib.notifications.enableNotifications`()
	method.
	"""
	global _isEnabled
	_isEnabled = False

@atexit.register
def shutdownNotifications():
	""" 
	Shutdown the notification sub-module and the http server. It also removes subscriptions
	created through the `onem2mlib.ResourceBase.subscribe`() method. After this no more 
	notifications can be received through the sub-module.

	**Note**

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

def isNotificationEnabled():
	""" Boolean. Return the status whether notifications are currently enabled. """
	return _isEnabled

def getNotificationURI():
	""" String. Return the current notificationURI, or None when notifications are disabled. """
	return _notificationURI

###############################################################################
#	Handling temporary subscriptions / notifications

_subscriptions = {}
_subscriptionIDToParentResourceID = {}

def addSubscription(resource, callback=None, originator=None, eventNotificationCriteria=None):
	"""
	Add a subscription to the given resource. This creates a &lt;subscription> resource for
	that resource.

	This method might throw	a `onem2mlib.exceptions.NotSupportedError` exception in case
	the target resource type doesn't support subscriptions.

	Args:

	- *resource*: Resource to add the resource to.
	- *callback*: Optional reference to a callback function. This function is called instead of
	the one provided with the `onem2mlib.notifications.setupNotifications`() function.
 
 	- *orignator*: when doing a subscription from a different device, you have to specify the 
		X-Origin in order to be able to post.

	The method returns a Boolean indicating whether the subscription was successfully added.
	"""
	if resource.resourceID in _subscriptions:
		return True
	if resource.type not in _allowedSubscriptionResources:
		logger.error('Subscription not supported for this resource type: ' + INT.nameAndType(resource))
		raise EXC.NotSupportedError('Subscription not supported for this resource type.')
	
	# Create the Subscription resource with the optional ENC
	sub = onem2mlib.Subscription(
		parent=resource, 
		notificationURI=[_notificationURI], 
		originator=originator, 
		eventNotificationCriteria=eventNotificationCriteria
	)
	
	if not sub:
		return False
	_addSubscription(resource, sub, callback)
	return True

def removeSubscription(resource):
	"""
	Remove a subscription added prior by the `onem2mlib.notifications.addSubscription`()
	method. After calling this function no notifications for that resource are received
	or processed anymore.

	Args:

	- *resource*: The resource from which the subscription should be removed.

	The method returns a Boolean indicating whether the subscription was successfully removed.
	"""
	if not resource or not resource.resourceID:
		return False
	return _removeSubscriptionByID(resource.resourceID)

def hasSubscription(resource):
	"""
	Check whether a resource has a subscription attached, which is managed by the
	notification sub-service.

	Args:

	- *resource*: the resource to check.

	The method returns a Boolean indicating whether the resource is managed and
	has a subscription attached.
	"""
	if not resource or not resource.resourceID:
		return False
	return resource.resourceID in _subscriptions

# Add a subscription to the internal data strucures
def _addSubscription(resource, sub, callback):
	_subscriptions[resource.resourceID] = (sub, resource, callback)
	_subscriptionIDToParentResourceID[sub.resourceID] = resource.resourceID
	_subscriptionIDToParentResourceID[sub._structuredResourceID(withRIScope=True)] = resource.resourceID

# Remove a subscription from the internal data structures
def _removeSubscriptionByID(resourceID):
	if resourceID not in _subscriptions: 
		return False
	(sub, _, _) = _subscriptions.pop(resourceID)
	_subscriptionIDToParentResourceID.pop(sub.resourceID, None)
	_subscriptionIDToParentResourceID.pop(sub._structuredResourceID(withRIScope=True), None)
	return sub.deleteFromCSE()

# Remove all subscriptions from internal data structures
def removeAllSubscriptions():
	"""
	Remove all the subscriptions that have been added through the 
	`onem2mlib.notifications.addSubscription`() function.
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
def _startNotificationServer():
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
def _stopNotificationServer():
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
	def run(self):
		try:
			self.serve_forever()
		finally:
			self.server_close()


# This class implements the handler that reseives the requests
class HTTPNotificationHandler(BaseHTTPRequestHandler):
	def do_POST(self):
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
			if contentType.lower().startswith('application/xml'):
				threading.Thread(target=self._handleXML, args=(post_data,)).start()
			elif contentType.lower().startswith('application/json'):
				threading.Thread(target=self._handleJSON, args=(post_data,)).start()

	def log_message(self, format, *args):
		return

	def _handleXML(self, data):
		tree = INT.stringToXML(data)
		if INT.getElement(tree, 'vrq'): 
			return 

		rep = INT.getElements(tree, 'rep')
		resource = None
		if rep:
			res_tree = rep[0][0]
			ty = INT.toInt(INT.getElement(res_tree, 'ty'))
			resource = INT._newResourceFromType(ty, None)
			resource._parseXML(res_tree)
		
		sur = INT.getElement(tree, 'sur')
		if sur:
			self._callCallback(resource, sur)

	def _handleJSON(self, data):
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

	def _callCallback(self, resource, sur, event_type=None, jsn=None):
		"""
		Finds the appropriate subscription and prepares the notification context.
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
			'event_type': event_type,
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

	def _safe_execute_callback(self, func, **kwargs):
		"""
		Standardized callback executor. Supports:
		1. def cb(resource, event_type, jsn, **kwargs)
		2. def cb(resource) [via fallback]
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
###############################################################################


__pdoc__                                     = {}
__pdoc__['HTTPNotificationServer']			 = None
__pdoc__['HTTPNotificationHandler']			 = None
__pdoc__['startNotificationServer']			 = None
__pdoc__['stopNotificationServer']			 = None
