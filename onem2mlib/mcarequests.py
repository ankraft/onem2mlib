#
#	mcarequests.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module contains helper functions to communicate with an CSE over the Mca interface via HTTP.
#

import requests
import onem2mlib.utilities as UT
import onem2mlib.constants as CON


###############################################################################

lastError = ''

#
#	Communication functions
#

# retrieve a resource either through its resourceID or resourceName
def retrieveFromCSE(resource):
	global lastError
	lastError = ''

	if _isInvalidResource(resource):
		lastError = 'Invalid resource'
		return False
	if resource.resourceName:
		response = get(resource.session, resource._structuredResourceID())
	else:
		response = get(resource.session, resource.resourceID)
	if response and response.status_code == 200:
		resource._parseResponse(response)
		return True
	lastError = str(response.status_code) + ' - ' + response.text
	return False


def createInCSE(resource, type):
	global lastError
	lastError = ''

	if _isInvalidResource(resource):
		lastError = 'Invalid resource'
		return False
	root = resource._createXML()
	#print(UT.xmlToString(root))
	response =  create(resource.session, resource.parent.resourceID, type, UT.xmlToString(root))
	if response and response.status_code == 201:
		resource._parseResponse(response)	# update own fields with response
		return True
	lastError = str(response.status_code) + ' - ' + response.text
	#print(str(response.status_code) + ' - ' + response.text)
	return False


def deleteFromCSE(resource):
	global lastError
	lastError = ''

	if _isInvalidResource(resource) or not resource.resourceID :
		lastError = 'Invalid resource'
		return False
	response = delete(resource.session, resource.resourceID)
	if response and response.status_code == 200:
		return True
	lastError = str(response.status_code) + ' - ' + response.text
	#print(response.status_code)
	return False


def updateInCSE(resource, type):
	global lastError
	lastError = ''

	if _isInvalidResource(resource):
		lastError = 'Invalid resource'
		return False
	root = resource._createXML(True)
	#print(UT.xmlToString(root))
	response = update(resource.session, resource.resourceID, type, UT.xmlToString(root))
	if response and response.status_code == 200:
		resource._parseResponse(response)	# update own fields with response
		return True
	lastError = str(response.status_code) + ' - ' + response.text
	#print(response.status_code)
	return False

###############################################################################

#
#	Basic functions
#


# Get a resource from the CSE
def get(session, path):
	try:
		return requests.get(_getPath(session, path), headers=_getHeaders(session), timeout=CON.NETWORK_REQUEST_TIMEOUT)
	except Exception as e:
		return None


# Find / discover a resource on the CSE
def discover(session, path, type=None):
	path = _getPath(session, path) + '?fu=1&drt=1'	# structured result type
	if type:
		path = path + '&ty='+str(type)
	try:
		return requests.get(path, headers=_getHeaders(session), timeout=CON.NETWORK_REQUEST_TIMEOUT)
	except Exception as e:
		return None


# Delete an existing resource on the CSE
def delete(session, path):
	try:
		return requests.delete(_getPath(session, path), headers=_getHeaders(session), timeout=CON.NETWORK_REQUEST_TIMEOUT)
	except Exception as e:
		return None

# Create a new resource on the CSE
def create(session, path, type, body):
	try:
		return requests.post(_getPath(session, path), headers=_getHeaders(session, type), data=body, timeout=CON.NETWORK_REQUEST_TIMEOUT)
	except Exception as e:
		return None

# Update an existing resource on the CSE
def update(session, path, type, body):
	try:
		return requests.put(_getPath(session, path), headers=_getHeaders(session, type), data=body, timeout=CON.NETWORK_REQUEST_TIMEOUT)
	except Exception as e:
		return None


###############################################################################

#
#	Internal helpers
#

def _getHeaders(session, type=None):
	headers = dict()
	headers['X-M2M-Origin'] = session.originator
	if type:
		headers['Content-Type'] = 'application/xml;ty=' + str(type)
	else:
		headers['Content-Type'] = 'application/xml'
	headers['Accept'] = 'application/xml'
	return headers


def _getPath(session, path):
	if path and path[0] == '/':
		return session.address+'/~' + path
	else:
		return session.address+'/~/' + path

def _isInvalidResource(resource):
	return 	not resource.parent or not resource.parent.resourceID or \
		 	not resource.session or not resource.session.connected




