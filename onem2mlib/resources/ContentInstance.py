#
#	ContentInstance.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
""" This module implements the class for the <ContentInstance> resource. """

from __future__ import annotations
from typing import Optional, Any, override

import logging
import onem2mlib.constants as CON
import onem2mlib.internal as INT
import onem2mlib.mcarequests as MCA
import onem2mlib.exceptions as EXC
from .ResourceBase import ResourceBase

logger = logging.getLogger(__name__)

class ContentInstance(ResourceBase):
	"""	This class implements the oneM2M <contentInstance> resource. This type of resource can
		only be created or deleted, but not updated.

		It is a child-resource of the <container> resource.

		To publish data in a <contentInstance> resource, one must first encode the data so 
		that it can be transferred as a string value and must then set the encoding type in the 
		`contentInfo` attribute. The default is ``text/plain:0``.
	"""

	def __init__(self, content: Optional[str] = None, 
			  		   contentInfo: Optional[str] = None, 
					   instantly: bool = True, 
					   **kwargs: Any) -> None:
		"""
		Initialize the <contentInstance> resource. 

		Args:
			content: The actual data payload.
			contentInfo: Metadata about the content (e.g., encoding).
			instantly: If True, the resource is immediately created in the CSE.
			**kwargs: Inherited attributes (parent, resourceName, labels, originator, etc.)
		"""
		super().__init__(type=CON.Type_ContentInstance, typeShortName=CON.Type_ContentInstance_SN, **kwargs)

		self.contentInfo = contentInfo
		""" String. The type of the data in the `onem2mlib.ContentInstance.content` 
		state variable."""

		self.contentSize = 0
		""" String. The size of the data in the `onem2mlib.ContentInstance.content` 
		state variable. R/O."""

		self.content = content
		""" Usually an encoded String. The actual content of the <contentInstance> resource."""

		if instantly:
			if not self.get():
				logger.critical(f'Cannot get or create ContentInstance. {MCA.lastError}')
				raise EXC.CSEOperationError(f'Cannot get or create ContentInstance. {MCA.lastError}')


	def __str__(self) -> str:
		return	'ContentInstance:\n' + \
				super().__str__() + \
				INT.strResource('contentInfo', 'cnf', self.contentInfo) + \
				INT.strResource('contentSize', 'cs', self.contentSize) + \
				INT.strResource('content', 'con', self.content)

	@override
	def _copy(self, resource: ContentInstance) -> None:	# type: ignore[override]
		super()._copy(resource)
		self.contentInfo = resource.contentInfo
		self.contentSize = resource.contentSize
		self.content = resource.content

	def _fromCSE(self, jsn: dict) -> None:
		""" Update the attributes of this AE resource from a JSON representation.

				Args:
					jsn: The JSON representation of the resource as a dictionary.
		"""
		_jsn = super()._fromCSE(jsn)
		self.contentInfo = INT.getElementJSON(_jsn, 'cnf', self.contentInfo)
		self.contentSize = INT.getElementJSON(_jsn, 'cs', self.contentSize)
		self.content = INT.getElementJSON(_jsn, 'con', self.content)


	def _toCSE(self, isUpdate: bool = False, isAcpiUpdate: bool = False) -> dict:
		""" Return a JSON representation of this AE resource as a dictionary, to be sent to the CSE.

			Args:
				isUpdate: If True, this JSON is for an update operation.
				isAcpiUpdate: If True, this JSON is for an ACP update operation.

			Returns:
				A JSON representation of this AE resource as a dictionary, to be sent to the CSE.
		"""
		jsn = super()._toCSE(isUpdate, isAcpiUpdate)
		INT.addToElementJSON(jsn, 'cnf', self.contentInfo)
		INT.addToElementJSON(jsn, 'con', self.content)
		return INT.wrapJSON(self, jsn)


