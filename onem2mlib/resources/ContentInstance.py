#
#	ContentInstance.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module implements the class for the &lt;ContentInstance> resource.
#

import logging
import onem2mlib.marshalling as M
import onem2mlib.constants as CON
import onem2mlib.internal as INT
from .ResourceBase import ResourceBase

logger = logging.getLogger(__name__)


class ContentInstance(ResourceBase):
	"""
	This class implements the oneM2M &lt;contentInstance> resource. This type of resource can
	only be created or deleted, but not updated.

	It is usually a sub-resource of the &lt;container> resource.

	To publish data in a &lt;contentInstance> resource, one must first encode the data so 
	that it	can be transfered as a string value and must then  set the encoding type in the 
	`onem2mlib.ContentInstance.contentInfo` state variable. The default is 
	`text/plain:0`. See also the oneM2M specification for further details.

	To retrieve the actual content value of the resource 
	(from `onem2mlib.ContentInstance.content`) one must first check the 
	`onem2mlib.ContentInstance.contentInfo` state variable to determine the
	type of the content and decode it accordingly.
	"""


	def __init__(self, parent=None, resourceName=None, content=None, contentInfo=None, resourceID=None, labels = [], instantly=True):
		"""
		Initialize the &lt;contentInstance> resource. 

		Args:

		- *parent*: The parent resource object in which the &lt;contentInstance> resource
			will be created.
		- *instantly*: The resource will be instantly retrieved from or created on the CSE. This might throw
			a `onem2mlib.exceptions.CSEOperationError` exception in case of an error.
		- All other arguments initialize the status variables of the same name in
			&lt;contentInstance> instance or `onem2mlib.ResourceBase`.
		"""
		ResourceBase.__init__(self, parent, resourceName, resourceID, CON.Type_ContentInstance, CON.Type_ContentInstance_SN, labels=labels)
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
				logger.critical('Cannot get or create ContentInstance. '  + MCA.lastError)
				raise EXC.CSEOperationError('Cannot get or create ContentInstance. '  + MCA.lastError)


	def __str__(self):
		result = 'ContentInstance:\n'
		result += ResourceBase.__str__(self)
		result += INT.strResource('contentInfo', 'cnf', self.contentInfo)
		result += INT.strResource('contentSize', 'cs', self.contentSize)
		result += INT.strResource('content', 'con', self.content)
		return result


	def _copy(self, resource):
		ResourceBase._copy(self, resource)
		self.contentInfo = resource.contentInfo
		self.contentSize = resource.contentSize
		self.content = resource.content
