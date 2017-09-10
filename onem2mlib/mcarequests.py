#
#	mcarequests.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module contains helper functions to communicate with an CSE over the Mca interface via HTTP.
#

import requests
import onem2mlib.internal as INT
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

	if not _isValidResource(resource):
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
	#print(str(response.status_code) + ' - ' + response.text)
	return False


def createInCSE(resource, type):
	global lastError
	lastError = ''

	if not _isValidResource(resource):
		lastError = 'Invalid resource'
		return False
	root = resource._createXML()
	#print(INT.xmlToString(root))
	response =  create(resource.session, resource.parent.resourceID, type, INT.xmlToString(root))
	if response and response.status_code == 201:
		resource._parseResponse(response)	# update own fields with response
		return True
	lastError = str(response.status_code) + ' - ' + response.text
	#print(str(response.status_code) + ' - ' + response.text)
	return False


def deleteFromCSE(resource):
	global lastError
	lastError = ''

	if not _isValidResource(resource) or not resource.resourceID :
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

	if not _isValidResource(resource):
		lastError = 'Invalid resource'
		return False
	root = resource._createXML(True)
	#print(INT.xmlToString(root))
	response = update(resource.session, resource.resourceID, type, INT.xmlToString(root))
	if response and response.status_code == 200:
		resource._parseResponse(response)	# update own fields with response
		return True
	lastError = str(response.status_code) + ' - ' + response.text
	#print(response.status_code)
	return False


# Find resources under a resource in the CSE
def discoverInCSE(resource, filter=None, filterOperation=None, structuredResult=False):
	global lastError
	lastError = ''

	path = resource.resourceID + '?fu=1&drt='+str(1 if structuredResult else 2)
	if filter and isinstance(filter, list):						# Construct the filter parameters
		for key,val in filter:
			path += '&' + key + '=' + val
	if filterOperation and isinstance(filterOperation, int):	# Add filter operation
		path += '&fo=' + str(filterOperation)
	#print(path)
	response = get(resource.session, path)
	if response and response.status_code == 200:
		#print(response.text)
		root = INT.responseToXML(response)
		lst = INT.getElement(root, 'm2m:uril', default=[])	# setting default because: Make sure that the result is a list
		return lst
	lastError = str(response.status_code) + ' - ' + response.text
	return None


###############################################################################

#
#	Basic functions
#


# Get a resource from the CSE
def get(session, path):
	try:
		#print(_getPath(session, path))
		return requests.get(_getPath(session, path), headers=_getHeaders(session), timeout=CON.NETWORK_REQUEST_TIMEOUT)
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

def _isValidResource(resource):
	return	(resource.type == CON.Type_CSEBase and resource.session) or \
			(resource.parent is not None and resource.parent.resourceID is not None and \
				resource.session is not None and resource.session.connected is not None)




