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

import atexit, threading, json
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

import onem2mlib
import onem2mlib.exceptions as EXC
import onem2mlib.constants as CON
import onem2mlib.internal as INT

_isEnabled = False
_host = None
_port = -1
_callback = None
_notificationURI = None


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
	
	# Initialize configuration, possible a new configuration

	if not host:
		raise EXC.ConfigurationError('enableNotifications(): Missing host.')
	if port == -1:
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
	if _isEnabled:
		return
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
	if not _isEnabled:
		return
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
	removeAllSubscriptions()
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
#
#	Handling temporary subscriptions / notifications
#
#

_subscriptions = {}
_subscriptionIDToParentResourceID = {}

def addSubscription(resource, callback=None):
	"""
	Add a subscription to the given resource. This creates a &lt;subscription> resource for
	that resource.

	This method might throw	a `onem2mlib.exceptions.NotSupportedError` exception in case
	the target resource type doesn't support subscriptions.

	Args:

	- *resource*: Resource to add the resource to.
	- *callback*: Optional reference to a callback function. This function is called instead of
	the one provided with the `onem2mlib.notifications.setupNotifications`() function.

	The method returns a Boolean indicating whether the subscription was successfully added.
	"""

	if resource.resourceID in _subscriptions:
		return True
	if resource.type not in _allowedSubscriptionResources:
		raise EXC.NotSupportedError('Subscription not supported for this resource type')
	sub = onem2mlib.Subscription(resource, notificationURI=[_notificationURI])
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
	return resource.resourceID in _subscriptions.keys()


# Add a subscription to the internal data strucures
def _addSubscription(resource, sub, callback):
	_subscriptions[resource.resourceID] = (sub, resource, callback)
	_subscriptionIDToParentResourceID[sub.resourceID] = resource.resourceID
	_subscriptionIDToParentResourceID[sub._structuredResourceID()] = resource.resourceID


# Remove a subscription from the internal data structures
def _removeSubscriptionByID(resourceID):
	(sub, _, _) = _subscriptions.pop(resourceID)
	_subscriptionIDToParentResourceID.pop(sub.resourceID)
	_subscriptionIDToParentResourceID.pop(sub._structuredResourceID())
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
#
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
			# Clean-up server (close socket, etc.)
			self.server_close()


# This class implements the handler that reseives the requests
class HTTPNotificationHandler(BaseHTTPRequestHandler):

	# Handle incoming notifications (POST requests)
	def do_POST(self):
			# Construct return header
			self.send_response(200)
			self.send_header('X-M2M-RSC', '2000')
			self.end_headers()

			# Get headers and content data
			length = int(self.headers['Content-Length'])
			contentType = self.headers['Content-Type']
			post_data = self.rfile.read(length)
			#print(post_data)

			if _isEnabled:
				# Handle notification in the background when enabled
				if contentType.lower().startswith('application/xml'):
					threading.Thread(target=self._handleXML(post_data), args=(post_data)).start()
				elif contentType.lower().startswith('application/json'):
					threading.Thread(target=self._handleJSON(post_data), args=(post_data)).start()
			

	# Catch and ignore all log messages
	def log_message(self, format, *args):
		return


	# Handle XML notifications 
	def _handleXML(self, data):
		tree = INT.stringToXML(data)
		
		# check verification request
		vrq = INT.getElement(tree, 'vrq')
		if vrq:
			return 	# do nothing

		# get resource
		rep = INT.getElements(tree, 'rep')
		if rep and len(rep) > 0:
			tree = rep[0][0]
			type = INT.toInt(INT.getElement(tree, 'ty'))
			resource = INT._newResourceFromType(type, None)
			resource._parseXML(tree)
		
		# get the sur first
		sur = INT.getElement(tree, 'sur')
		if not sur:
			return 	# must have a subscription ID

		# get and call callback
		self._callCallback(resource, sur)
	

	# Handle JSON notifications 
	def _handleJSON(self, data):
		jsn =  json.loads(data.decode('utf-8'))
		#print(jsn)

		# check verification request
		vrq = INT.getALLSubElementsJSON(jsn, 'vrq')
		if len(vrq) == 0:										# TODO remove later when om2m corrects this
			vrq = INT.getALLSubElementsJSON(jsn, 'm2m:vrq')
		if len(vrq) > 0 and vrq[0] == True:
			return 	# do nothing

		# get the sur first
		sur = INT.getALLSubElementsJSON(jsn, 'sur')
		if len(sur) == 0:										# TODO remove later when om2m corrects this
			sur = INT.getALLSubElementsJSON(jsn, 'm2m:sur')
		if len(sur) > 0:
			sur = sur[0]
		else:
			return 	# must have a subscription ID

		# get resource
		rep = INT.getALLSubElementsJSON(jsn, 'rep')
		if len(rep) == 0:										# TODO remove later when om2m corrects this
			rep = INT.getALLSubElementsJSON(jsn, 'm2m:rep')
		if len(rep) > 0:
			jsn = rep[0]
			type = INT.getALLSubElementsJSON(jsn, 'ty')
			if type and len(type) > 0:
				resource = INT._newResourceFromType(type[0], None)
				resource._parseJSON(jsn)
				self._callCallback(resource, sur)


	def _callCallback(self, resource, sur):
		# get and call callback
		if sur not in _subscriptionIDToParentResourceID:
			return
		parentResourceID = _subscriptionIDToParentResourceID[sur]
		if not parentResourceID:
			return
		(_, _, callback) = _subscriptions[parentResourceID]
		if not callback:
			callback = _callback
		callback(resource)


###############################################################################


__pdoc__                                     = {}
__pdoc__['HTTPNotificationServer']			 = None
__pdoc__['HTTPNotificationHandler']			 = None
__pdoc__['startNotificationServer']			 = None
__pdoc__['stopNotificationServer']			 = None
