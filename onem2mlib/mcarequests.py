#
#	mcarequests.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#

""" This module contains helper functions to communicate with an CSE over the Mca interface via HTTP. """

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

import base64
import uuid
import requests
import logging
import onem2mlib.internal
import onem2mlib.constants as CON
import onem2mlib.exceptions as EXC
from .resources.Session import Session

if TYPE_CHECKING:
	from .resources.ResourceBase import ResourceBase



###############################################################################

lastError: str = ''
""" The last error message from any of the functions in this module. This is set to an empty string on success. """

logger = logging.getLogger(__name__)
""" Logger for this module. """

#
#	Communication functions
#

# retrieve a resource either through its resourceID or resourceName
def retrieveFromCSE(resource: ResourceBase, originator: Optional[str] = None) -> bool:
	global lastError
	lastError = ''

	if not _isValidResource(resource):
		lastError = 'Invalid resource'
		logger.error(lastError)
		return False

	# Define the order of IDs we want to try
	# Logic: If we have an RI, try it first (more stable). 
	# Otherwise, use Structured ID.
	ids_to_try = []
	if resource.resourceID:
		ids_to_try.append(("unstructured", resource._unstructuredResourceID(withRIScope=True)))
	
	# Always add structured as a candidate if name is known
	if resource.resourceName:
		ids_to_try.append(("structured", resource._structuredResourceID(withRIScope=True)))

	for id_type, target_id in ids_to_try:
		try:
			logger.debug(f'Attempting retrieval via {id_type} ID: {target_id}')
			response = get(resource.session, target_id, originator=originator)
			
			if response is not None:
				if response.status_code == 200:
					resource._parseResponse(response)
					return True
				
				# If 404, we don't return yet; we try the next ID in the list
				if response.status_code == 404:
					lastError = f"404 - Not Found ({target_id})"
					continue 
				
				# If it's a different error (403, 500, etc.), stop and fail
				lastError = f"{response.status_code} - {response.text}"
				logger.error(f'Retrieve failed: {lastError}')
				return False

		except Exception as e:
			lastError = f"Request failed for {target_id}: {e}"
			logger.debug(lastError)
			continue

	# If we are here, all attempts failed
	logger.debug(f'All retrieval attempts failed. Last error: {lastError}')
	return False


def createInCSE(resource: ResourceBase, type: int, originator: Optional[str] = None) -> bool:
	global lastError
	lastError = ''

	logger.debug('Create resource: ' + str(resource))
	if not _isValidResource(resource) or not resource.parent:
		lastError = 'Invalid resource or missing parent'
		logger.error(lastError)
		return False

	content = resource._createContent(False)
	
	# Collect potential parent IDs to try
	parent_targets = []
	if resource.parent.resourceID:
		parent_targets.append(('unstructured', resource.parent._unstructuredResourceID(withRIScope=True)))
	if resource.parent.resourceName:
		parent_targets.append(('structured', resource.parent._structuredResourceID(withRIScope=True)))

	for id_type, target_id in parent_targets:
		try:
			logger.debug(f'Attempting CREATE under parent ({id_type}): {target_id}')
			response = create(resource.session, target_id, type, content, originator=originator)
			
			if response is not None:
				if response.status_code == 201:
					resource._parseResponse(response)
					return True
				
				# If parent not found on this ID, try the next one
				if response.status_code == 404:
					lastError = f"404 - Parent Not Found ({target_id})"
					continue
				
				# Critical error (e.g. 403, 409) - Fail immediately
				lastError = f"{response.status_code} - {response.text}"
				logger.error(f'Create failed: {lastError}')
				return False
		except Exception as e:
			lastError = f"Create request failed: {e}"
			continue

	return False

def deleteFromCSE(resource: ResourceBase, 
				  originator: Optional[str] = None) -> bool:
	global lastError
	lastError = ''

	logger.debug(f'Delete resource: {resource}')
	if not _isValidResource(resource):
		lastError = 'Invalid resource'
		logger.error(lastError)
		return False

	targets = []
	if resource.resourceID:
		targets.append(('unstructured', resource._unstructuredResourceID(withRIScope=True)))
	if resource.resourceName:
		targets.append(('structured', resource._structuredResourceID(withRIScope=True)))

	for id_type, target_id in targets:
		try:
			logger.debug(f'Attempting DELETE via {id_type} ID: {target_id}')
			response = delete(resource.session, target_id, originator=originator)
			
			if response is not None:
				if response.status_code == 200:
					return True
				
				if response.status_code == 404:
					lastError = f"404 - Not Found ({target_id})"
					continue
				
				lastError = f"{response.status_code} - {response.text}"
				logger.error(f'Delete failed: {lastError}')
				return False
		except Exception as e:
			lastError = f"Delete request failed: {e}"
			continue

	return False

def updateInCSE(resource: ResourceBase, 
				type: int, 
				originator: Optional[str] = None, 
				isAcpiUpdate: bool = False) -> bool:
	global lastError
	lastError = ''

	logger.debug('Update resource: ' + str(resource))
	if not _isValidResource(resource):
		lastError = 'Invalid resource'
		logger.error(lastError)
		return False

	content = resource._createContent(True, isAcpiUpdate)
	
	targets = []
	if resource.resourceID:
		targets.append(('unstructured', resource._unstructuredResourceID(withRIScope=True)))
	if resource.resourceName:
		targets.append(('structured', resource._structuredResourceID(withRIScope=True)))

	for id_type, target_id in targets:
		try:
			logger.debug(f'Attempting UPDATE via {id_type} ID: {target_id}')
			response = update(resource.session, target_id, type, content, originator=originator)
			
			if response is not None:
				if response.status_code == 200:
					resource._parseResponse(response)
					return True
				
				if response.status_code == 404:
					lastError = f"404 - Not Found ({target_id})"
					continue
				
				lastError = f"{response.status_code} - {response.text}"
				logger.error(f'Update failed: {lastError}')
				return False
		except Exception as e:
			lastError = f"Update request failed: {e}"
			continue

	return False


# Find resources under a resource in the CSE
def discoverInCSE(resource: ResourceBase, 
				  filter: Optional[list[tuple[str, str|int|bool]]] = None, 
				  filterOperation: Optional[int] = None, 
				  structuredResult: bool = False, 
				  originator: Optional[str] = None) -> Optional[list[str]]:
	
	global lastError
	lastError = ''

	logger.debug('Discovery on resource: ' + str(resource))
	if not _isValidResource(resource):
		lastError = 'Invalid resource'
		logger.error(lastError)
		return None

	# 1. Build the query parameter string
	# fu=1 is discovery, drt defines the result format (1=structured, 2=unstructured)
	query_params = '?fu=1&drt=' + str(1 if structuredResult else 2)
	
	if filter and isinstance(filter, list):
		for key, val in filter:
			query_params += f'&{key}={val}'
			
	if filterOperation and isinstance(filterOperation, int):
		query_params += f'&fo={filterOperation}'

	# 2. Define the target IDs to try
	targets = []
	if resource.resourceID:
		targets.append(('unstructured', resource._unstructuredResourceID(withRIScope=True)))
	if resource.resourceName:
		targets.append(('structured', resource._structuredResourceID(withRIScope=True)))

	# 3. Iterate through targets with fallback logic
	for id_type, base_path in targets:
		full_path = base_path + query_params
		try:
			logger.debug(f'Attempting DISCOVERY via {id_type} ID: {full_path}')
			response = get(resource.session, full_path, originator=originator)
			
			if response is not None:
				if response.status_code == 200:
					# Success: Parse the URI List (m2m:uril)
					return onem2mlib.internal.getElementJSON(
						response.json(), 
						'm2m:uril', 
						default=[]
					)

				# If 404, the resource wasn't found at this ID; try the next target
				if response.status_code == 404:
					lastError = f"404 - Not Found ({base_path})"
					continue
				
				# If any other error (403, 400, etc.), stop and report it
				lastError = str(response.status_code) + ' - ' + response.text
				logger.error('Discovery failed: ' + lastError)
				return None

		except Exception as e:
			lastError = f"Discovery request failed for {id_type}: {e}"
			logger.debug(lastError)
			continue

	# 4. Final error handling if all attempts fail
	if not lastError:
		lastError = 'No valid IDs available for discovery'
		
	# If the response was None (network failure) and we haven't returned yet
	# we raise an exception as per the original logic's critical error handling
	if targets and lastError.startswith('Discovery request failed'):
		logger.critical('Response from CSE must not be None.')
		raise EXC.CSEOperationError('Response from CSE must not be None.')
		
	return None

def retrieveResourceByID(parent: ResourceBase, targetID: str, originator: Optional[str] = None) -> Optional[ResourceBase]:
	"""
	Retrieve a resource by its *resourceID* from the CSE. Any valid *parent* resource
	instance from that CSE must be given as the first parameter to pass on various internal
	attributes. 
	The type of the resource is determined during retrieval.

	When successful, this method returns the retrieved resource, or None otherwise.
	"""
	global lastError
	lastError = ''

	if not parent.session or not targetID:
		lastError = 'Invalid parent session or target ID'
		return None

	logger.debug(f'Retrieving new resource object via ID: {targetID}')
	
	# Perform the GET request
	response = get(parent.session, targetID, originator=originator)
	
	if response and response.status_code == 200:
		import onem2mlib.internal as INT # Local import to avoid circular dependency
		
		# Determine the type to create the correct Python class instance
		ty = INT.getTypeFromResponse(response)
		resource = INT._newResourceFromRID(ty, targetID, parent, originator=originator)
		
		if resource:
			# Populate the object with the server data
			jsn = response.json()
			resource._parseJSON(jsn)
			return resource
		else:
			lastError = f'Could not instantiate resource type: {ty}'
			logger.error(lastError)
	
	if response:
		lastError = f'{response.status_code} - {response.text}'
		logger.error(f'RetrieveByID failed: {lastError}')
	
	return None


###############################################################################

#
#	Basic functions
#


# Get a resource from the CSE
def get(session: Session, path: str, originator: Optional[str] = None) -> Optional[requests.Response]:
	try:
		realPath = _getPath(session, path)
		headers = _getHeaders(session, originator=originator)
		_logRequest(realPath, headers)
		return _logResponse(requests.get(realPath, headers=headers, timeout=CON.NETWORK_REQUEST_TIMEOUT))
	except Exception as e:
		logger.critical(e)
		return None

# Delete an existing resource on the CSE
def delete(session: Session, path: str, originator: Optional[str] = None) -> Optional[requests.Response]:
	try:
		realPath = _getPath(session, path)
		headers = _getHeaders(session, originator=originator)
		_logRequest(realPath, headers, 'DELETE')
		return _logResponse(requests.delete(realPath, headers=headers, timeout=CON.NETWORK_REQUEST_TIMEOUT))
	except Exception as e:
		logger.critical(e)
		return None

# Create a new resource on the CSE
def create(session: Session, path: str, type: int, body: str, originator: Optional[str] = None) -> Optional[requests.Response]:
	try:
		realPath = _getPath(session, path)
		headers = _getHeaders(session, type, originator=originator)
		_logRequest(realPath, headers, 'POST', body)
		return _logResponse(requests.post(realPath, headers=headers, data=body, timeout=CON.NETWORK_REQUEST_TIMEOUT))
	except Exception as e:
		logger.critical(e)
		return None

# Update an existing resource on the CSE
def update(session: Session, 
		   path: str, 
		   type: Optional[int], 
		   body: str, 
		   originator: Optional[str] = None) -> Optional[requests.Response]:
	try:
		realPath = _getPath(session, path)
		headers = _getHeaders(session, originator=originator)
		_logRequest(realPath, headers, 'PUT', body)
		return _logResponse(requests.put(realPath, headers=headers, data=body, timeout=CON.NETWORK_REQUEST_TIMEOUT))
	except Exception as e:
		logger.critical(e)
		return None


# Helper: log a request
def _logRequest(path: str, headers: dict, ty: str = 'GET', body: Optional[str] = None) -> None:
	logger.debug(ty + ' path: ' + path)
	logger.debug(ty + ' headers: ' + str(headers))
	if body is not None:
		logger.debug(ty + ' body: ' + str(body))


# Helper: log a response and return it
def _logResponse(response: requests.Response) -> Optional[requests.Response]:
	logger.debug('Response status code: ' + str(response.status_code))
	logger.debug('Response header: ' + str(response.headers))
	if response.text is not None and len(response.text) > 0:
		logger.debug('Response body: ' + response.text)
	return response


###############################################################################

#
#	Internal helpers
#

def _getHeaders(session: Session, type: Optional[int] = None, originator: Optional[str] = None) -> dict:
	headers = dict()
	headers['X-M2M-Origin'] = originator if originator is not None else session.originator
	headers['X-M2M-RI'] = str(uuid.uuid4())
	headers['X-M2M-RVI'] = session.releaseVersion or '3'

	# Handle Encoding
	encoding = 'application/json'

	if type:
		headers['Content-Type'] = f'{encoding};ty={type}'
		headers['Accept'] = encoding
	else:
		headers['Content-Type'] = encoding
		headers['Accept'] = encoding

	# Authentication Header Logic
	if session.username:
		if session.password is not None:
			# Basic Auth: Authorization: Basic <base64(user:pass)>
			auth_str = f"{session.username}:{session.password}"
			encoded_auth = base64.b64encode(auth_str.encode('ascii')).decode('ascii')
			headers['Authorization'] = f"Basic {encoded_auth}"
		else:
			# Bearer Token: Authorization: Bearer <token>
			headers['Authorization'] = f"Bearer {session.username}"

	return headers


def _getPath(session: Session, path: str) -> str:
	""" Construct the full URL for the request based on the session's address and the provided path.
	
		The path can be:
		- Absolute (starting with '//'): appended directly to the base address with '/_/' prefix
		- Root-relative (starting with '/'): appended to the base address with '/~' prefix
		- Relative: appended directly to the base address
	 
	  Args:
		  session: The Session object containing the base address.
		  path: The path to be appended to the base address.
	  Returns:
		  The full URL as a string.
	"""
	# logger.debug('session.address: ' + session.address)
	# logger.debug('path: ' + path)
	if not path:
		return session.address

	if path.startswith('//'):
		return f"{session.address}/_/{path[2:]}"

	if path.startswith('/'):
		return f"{session.address}/~{path}"

	return f"{session.address}/{path}"


def _isValidResource(resource: ResourceBase) -> bool:
	"""	Check if the given resource is valid for retrieval/creation/update/deletion in the CSE.
	
		A resource is considered valid if it has an associated session and either a resourceID or resourceName.
		  
	  Args:
			resource: The ResourceBase instance to check.
			   
	  Returns:
			True if the resource is valid, False otherwise.
	"""
	return	(resource.type == CON.Type_CSEBase and resource.session is not None) or \
			(resource.session is not None and ( \
				#(resource.parent is not None and resource.parent.resourceName is not None)\
				(resource.parent is not None and resource.parent.resourceID is not None)\
			) )




