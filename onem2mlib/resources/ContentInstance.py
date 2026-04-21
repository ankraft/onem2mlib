#
#	ContentInstance.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module implements the class for the <ContentInstance> resource.
#

import logging
import onem2mlib.marshalling as M
import onem2mlib.constants as CON
import onem2mlib.internal as INT
import onem2mlib.mcarequests as MCA
import onem2mlib.exceptions as EXC
from .ResourceBase import ResourceBase

logger = logging.getLogger(__name__)

class ContentInstance(ResourceBase):
	"""
	This class implements the oneM2M &lt;contentInstance> resource. This type of resource can
	only be created or deleted, but not updated.

	It is usually a sub-resource of the &lt;container> resource.

	To publish data in a <contentInstance> resource, one must first encode the data so 
	that it can be transferred as a string value and must then set the encoding type in the 
	`contentInfo` attribute. The default is `text/plain:0`.
	"""

	def __init__(self, content: str | None= None, contentInfo: str |None = None, instantly: bool = True, **kwargs):
		"""
		Initialize the &lt;contentInstance> resource. 

		Args:
			content: The actual data payload.
			contentInfo: Metadata about the content (e.g., encoding).
			instantly: If True, the resource is immediately created in the CSE.
			**kwargs: Inherited attributes (parent, resourceName, labels, originator, etc.)
		"""
		super().__init__(type=CON.Type_ContentInstance, typeShortName=CON.Type_ContentInstance_SN, **kwargs)

		self._marshallers = [M._ContentInstance_parseXML, M._ContentInstance_createXML,
							 M._ContentInstance_parseJSON, M._ContentInstance_createJSON]

		self.contentInfo = contentInfo
		""" String. The type of the data in the `onem2mlib.ContentInstance.content` 
		state variable."""

		self.contentSize = 0
		""" String. The size of the data in the `onem2mlib.ContentInstance.content` 
		state variable. R/O."""

		self.content = content
		""" Usually an encoded String. The actual content of the &lt;contentInstance> resource."""

		if instantly:
			if not self.get():
				logger.critical(f'Cannot get or create ContentInstance. {MCA.lastError}')
				raise EXC.CSEOperationError(f'Cannot get or create ContentInstance. {MCA.lastError}')


	def __str__(self):
		result = 'ContentInstance:\n'
		result += super().__str__()
		result += INT.strResource('contentInfo', 'cnf', self.contentInfo)
		result += INT.strResource('contentSize', 'cs', self.contentSize)
		result += INT.strResource('content', 'con', self.content)
		return result


	def _copy(self, resource: 'ContentInstance'):
		super()._copy(resource)
		self.contentInfo = resource.contentInfo
		self.contentSize = resource.contentSize
		self.content = resource.content