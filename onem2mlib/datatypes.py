#
#	datatypes.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
""" This module defines the data types used in the onem2mlib module. """

from __future__ import annotations
from typing import Any

import onem2mlib.marshalling as M
import onem2mlib.internal as INT
import onem2mlib.constants as CON

if CON.Support_XML:
	from lxml import etree as ET


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


    def _parseXML(self, root: ET._Element) -> None:
        """ Parse an XML element to populate the EventNotificationCriteria object.
          
			Args:
				root: An XML element representing the EventNotificationCriteria.
		"""
        M._EventNotificationCriteria_parseXML(self, root)

    def _createXML(self, isUpdate: bool = False) -> ET._Element:
        """ Create an XML element from the EventNotificationCriteria object.
          
			Args:
				isUpdate: If True, create an XML element for an update operation.
		"""
        return M._EventNotificationCriteria_createXML(self, isUpdate)

    def _parseJSON(self, jsn: dict) -> None:
        """ Parse a JSON dictionary to populate the EventNotificationCriteria object.
        
			Args:
				jsn: A JSON dictionary representing the EventNotificationCriteria.
		"""
        M._EventNotificationCriteria_parseJSON(self, jsn)

    def _createJSON(self, isUpdate: bool = False) -> dict:
        """ Create a JSON dictionary from the EventNotificationCriteria object.
          
			Args:
				isUpdate: If True, create a JSON dictionary for an update operation.
		"""
        return M._EventNotificationCriteria_createJSON(self, isUpdate)