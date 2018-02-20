#
#	mcarequests.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module contains helper functions to communicate with an CSE over the Mca interface via HTTP.
#

import requests
import onem2mlib.internal
import onem2mlib.constants as CON
import onem2mlib.exceptions as EXC


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
		#print(response)
		resource._parseResponse(response)
		return True
	if response:
		lastError = str(response.status_code) + ' - ' + response.text
		#print(str(response.status_code) + ' - ' + response.text)
	return False


def createInCSE(resource, type):
	global lastError
	lastError = ''

	if not _isValidResource(resource):
		lastError = 'Invalid resource'
		return False
	content = resource._createContent(False)
	#print(content)
	response =  create(resource.session, resource.parent.resourceID, type, content)
	if response and response.status_code == 201:
		#print(response)
		resource._parseResponse(response)	# update own fields with response
		return True
	if response:
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
	if response:
		lastError = str(response.status_code) + ' - ' + response.text
		#print(response.status_code)
	return False


def updateInCSE(resource, type):
	global lastError
	lastError = ''

	if not _isValidResource(resource):
		lastError = 'Invalid resource'
		return False
	content = resource._createContent(True)
	#print(content)
	response = update(resource.session, resource.resourceID, type, content)
	if response and response.status_code == 200:
		#print(response)
		resource._parseResponse(response)	# update own fields with response
		return True
	if response:
		#print(response)
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
		if resource.session.encoding == CON.Encoding_XML:
			return onem2mlib.internal.getElement(onem2mlib.internal.responseToXML(response), 'm2m:uril', default=[])	# setting default because: Make sure that the result is a list
		elif resource.session.encoding == CON.Encoding_JSON:
			return onem2mlib.internal.getElementJSON(response.json(), 'm2m:uril', default=[])
		raise EXC.NotSupportedError('Encoding not supported: ' + str(self.session.encoding))

	if response:
		lastError = str(response.status_code) + ' - ' + response.text
	else:
		raise EXC.CSEOperationError('Response from CSE must not be None.')
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
	if session.encoding == CON.Encoding_XML:
		encoding = 'application/xml'
	else:
		encoding = 'application/json'

	if type:
		headers['Content-Type'] = encoding + ';ty=' + str(type)
		headers['Accept'] = encoding
	else:
		headers['Content-Type'] = encoding
		headers['Accept'] = encoding

	headers['Accept'] = encoding
	return headers


def _getPath(session, path):
	if path and path[0] == '/':
		return session.address+'/~' + path
	else:
		return session.address+'/~/' + path

def _isValidResource(resource):
	return	(resource.type == CON.Type_CSEBase and resource.session) or \
			(resource.session is not None and ( \
				(resource.parent is not None and resource.parent.resourceID is not None)\
			) )




