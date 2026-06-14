#
#	datatypes.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
""" This module defines the data types used in the onem2mlib module. """

from __future__ import annotations
from typing import Any

import onem2mlib.internal as INT

class EventNotificationCriteria:
	"""	Indicates the conditions that shall be met to trigger a notification.
	"""
	def __init__(self, **kwargs: Any) -> None:
		self.createdBefore = kwargs.get('createdBefore')
		self.createdAfter = kwargs.get('createdAfter')
		self.modifiedSince = kwargs.get('modifiedSince')
		self.unmodifiedSince = kwargs.get('unmodifiedSince')
		self.stateTagSmaller = kwargs.get('stateTagSmaller')
		self.stateTagBigger = kwargs.get('stateTagBigger')
		self.expireBefore = kwargs.get('expireBefore')
		self.expireAfter = kwargs.get('expireAfter')
		self.sizeAbove = kwargs.get('sizeAbove')
		self.sizeBelow = kwargs.get('sizeBelow')
		self.notificationEventType = kwargs.get('notificationEventType', [])
		self.operationMonitor = kwargs.get('operationMonitor')
		self.attribute = kwargs.get('attribute')
		self.childResourceType = kwargs.get('childResourceType')
		self.missingData = kwargs.get('missingData')
		self.filterOperation = kwargs.get('filterOperation')

	def __str__(self) -> str:
		""" String representation of the EventNotificationCriteria object. 
		
			Returns:
				A string representation of the EventNotificationCriteria object.
		"""
		return 	INT.strResource('createdBefore', 'crb', self.createdBefore) + \
				INT.strResource('createdAfter', 'cra', self.createdAfter) + \
				INT.strResource('modifiedSince', 'ms', self.modifiedSince) + \
				INT.strResource('unmodifiedSince', 'us', self.unmodifiedSince) + \
				INT.strResource('stateTagSmaller', 'sts', self.stateTagSmaller) + \
				INT.strResource('stateTagBigger', 'stb', self.stateTagBigger) + \
				INT.strResource('expireBefore', 'exb', self.expireBefore) + \
				INT.strResource('expireAfter', 'exa', self.expireAfter) + \
				INT.strResource('sizeAbove', 'sza', self.sizeAbove) + \
				INT.strResource('sizeBelow', 'szb', self.sizeBelow) + \
				INT.strResource('notificationEventType', 'net', self.notificationEventType) + \
				INT.strResource('operationMonitor', 'om', self.operationMonitor) + \
				INT.strResource('attribute', 'atr', self.attribute) + \
				INT.strResource('childResourceType', 'chty', self.childResourceType) + \
				INT.strResource('missingData', 'md', self.missingData) + \
				INT.strResource('filterOperation', 'fo', self.filterOperation)

	
	def _fromCSE(self, jsn: dict) -> None:
		""" Parse a JSON dictionary to populate the EventNotificationCriteria object.
		
			Args:
				jsn: A JSON dictionary representing the EventNotificationCriteria.
		"""
		if jsn is None: return
		self.createdBefore = INT.getElementJSON(jsn, 'crb', self.createdBefore)
		self.createdAfter = INT.getElementJSON(jsn, 'cra', self.createdAfter)
		self.modifiedSince = INT.getElementJSON(jsn, 'ms', self.modifiedSince)
		self.unmodifiedSince = INT.getElementJSON(jsn, 'us', self.unmodifiedSince)
		self.stateTagSmaller = INT.getElementJSON(jsn, 'sts', self.stateTagSmaller)
		self.stateTagBigger = INT.getElementJSON(jsn, 'stb', self.stateTagBigger)
		self.expireBefore = INT.getElementJSON(jsn, 'exb', self.expireBefore)
		self.expireAfter = INT.getElementJSON(jsn, 'exa', self.expireAfter)
		self.sizeAbove = INT.getElementJSON(jsn, 'sza', self.sizeAbove)
		self.sizeBelow = INT.getElementJSON(jsn, 'szb', self.sizeBelow)
		self.notificationEventType = INT.getElementJSON(jsn, 'net', self.notificationEventType)
		self.operationMonitor = INT.getElementJSON(jsn, 'om', self.operationMonitor)
		self.attribute = INT.getElementJSON(jsn, 'atr', self.attribute)
		self.childResourceType = INT.getElementJSON(jsn, 'chty', self.childResourceType)
		self.missingData = INT.getElementJSON(jsn, 'md', self.missingData)
		self.filterOperation = INT.getElementJSON(jsn, 'fo', self.filterOperation)


	def _toCSE(self, isUpdate: bool = False, isAcpiUpdate: bool = False) -> dict:
		""" Create a JSON dictionary from the EventNotificationCriteria object.
		  
			Args:
				isUpdate: If True, create a JSON dictionary for an update operation.
				isAcpiUpdate: If True, create a JSON dictionary for an ACP update operation.

			Returns:
				A JSON representation of this EventNotificationCriteria object as a dictionary, to be sent to the CSE.
		"""
		jsn: dict = {}
		INT.addToElementJSON(jsn, 'crb', self.createdBefore)
		INT.addToElementJSON(jsn, 'cra', self.createdAfter)
		INT.addToElementJSON(jsn, 'ms', self.modifiedSince)
		INT.addToElementJSON(jsn, 'us', self.unmodifiedSince)
		INT.addToElementJSON(jsn, 'sts', self.stateTagSmaller)
		INT.addToElementJSON(jsn, 'stb', self.stateTagBigger)
		INT.addToElementJSON(jsn, 'exb', self.expireBefore)
		INT.addToElementJSON(jsn, 'exa', self.expireAfter)
		INT.addToElementJSON(jsn, 'sza', self.sizeAbove)
		INT.addToElementJSON(jsn, 'szb', self.sizeBelow)
		INT.addToElementJSON(jsn, 'net', self.notificationEventType)
		INT.addToElementJSON(jsn, 'om', self.operationMonitor)
		INT.addToElementJSON(jsn, 'atr', self.attribute)
		INT.addToElementJSON(jsn, 'chty', self.childResourceType)
		INT.addToElementJSON(jsn, 'md', self.missingData)
		INT.addToElementJSON(jsn, 'fo', self.filterOperation)
		return jsn
