#
#	utilities.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module defines various utilitiy classes and functions
#

"""
This sub-module defines the various utility classes and function for the onem2mlib module.

"""
import logging
import onem2mlib.exceptions as EXC
import onem2mlib.constants as CON

logger = logging.getLogger(__name__)

#
#	Filter
#

def newLabelFilterCriteria(label):
	"""
	Create a new label filter criteria.

	Args:

	- *label*: String. The label to filter for. The format of a label is "key/value".

	This function may throw a *ParameterError* exception when called with an empty or wrong label format.
	"""
	if label is None:
		logger.error('label must not be empty.')
		raise EXC.ParameterError('label must not be empty.')
	if label.count('/') < 1:
		logger.error('Wrong format: label format is "key/value": ' + label)
		raise EXC.ParameterError('Wrong format: label format is "key/value": ' + label)
	return ('lbl', label)


def newTypeFilterCriteria(type):
	"""
	Create a new resource type filter criteria.

	Args:

	- *label*: Integer. The resource type to filter for. It must be one of the valid oneM2M resource types.

	This function may throw a *ParameterError* exception when called with a wrong resource type.
	"""
	if type not in [CON.Type_Mixed, CON.Type_ACP, CON.Type_AE, CON.Type_Container, \
					CON.Type_ContentInstance, CON.Type_CSEBase, CON.Type_Group, CON.Type_RemoteCSE, \
					CON.Type_Subscription, \
					CON.Type_FlexContainer]:
		logger.error('Wrong or unsupported type: ' + str(type))
		raise EXC.ParameterError('Wrong or unsupported type: ' + str(type))
	return ('ty', str(type))

#
##
###	TBD: More filter criteria when supported by om2m
##
#



###############################################################################
#
#	Retrieval functions
#

def retrieveResourceFromCSE(parent, resourceID):
	"""
	Retrieve a resource by its *resourceID* from the CSE. Any valid *parent* resource
	instance from that CSE must be given as the first parameter to pass on various internal
	attributes. 
	The type of the resource is determined during retrieval.

	When successful, this method returns the retrieved resource, or None otherwise.
	"""
	import onem2mlib.mcarequests
	import onem2mlib.internal

	if not parent.session or not resourceID or not len(resourceID):
		return False
	result = None
	response = onem2mlib.mcarequests.get(parent.session, resourceID)
	if response and response.status_code == 200:
		ty = onem2mlib.internal.getTypeFromResponse(response, parent.session.encoding)
		if parent.session.encoding == CON.Encoding_XML:
			root = onem2mlib.internal.responseToXML(response)
			result = onem2mlib.internal._newResourceFromRID(ty, resourceID, parent)
			if result:
				result._parseXML(root)
		elif parent.session.encoding == CON.Encoding_JSON:
			jsn = response.json()
			result = onem2mlib.internal._newResourceFromRID(ty, resourceID, parent)
			if result:
				result._parseJSON(jsn)
	return result



