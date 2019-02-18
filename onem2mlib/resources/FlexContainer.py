#
#	FlexContainer.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module implements the class for the &lt;FlexContainer> resource.
#

import logging
import onem2mlib.marshalling as M
import onem2mlib.constants as CON
from .ResourceBase import ResourceBase

logger = logging.getLogger(__name__)


class FlexContainer(ResourceBase):
	"""
	This class implements the oneM2M &lt;flexContainer> resource. 

	This is only a base class with the basic &lt;flexContainer> functionalities.
	It should be inherited to implement flexContainer specializations.
	"""


	def __init__(self, parent=None, resourceName=None, resourceID=None, namespace=None, resourceSpecialization=None, contentDefinition=None, attributes=None, labels = [], instantly=True):
		"""
		Initialize the &lt;flexContainer> resource. 

		Args:

		- *parent*: The parent resource object in which the &lt;contentInstance> resource
			will be created.
		- *notificationURI*: A list consisting of one or more targets that the Hosting CSE
		shall send notifications to.
		- *instantly*: The resource will be instantly retrieved from or created on the CSE. This might throw
			a `onem2mlib.exceptions.CSEOperationError` exception in case of an error.
		- All other arguments initialize the status variables of the same name in
			&lt;subscription> instance or `onem2mlib.ResourceBase`.

		TODO docu
		"""
	
		ResourceBase.__init__(self, parent, resourceName, resourceID, CON.Type_FlexContainer, resourceSpecialization, labels=labels, namespace=namespace)
		self._marshallers = [M._FlexContainer_parseXML, M._FlexContainer_createXML,
							 M._FlexContainer_parseJSON, M._FlexContainer_createJSON]

		self.contentDefinition = contentDefinition
		self.attributes = attributes # TODO

		if instantly:
			if not self.get():
				logger.error('Cannot get or create FlexContainer specialization. '  + MCA.lastError)
				raise EXC.CSEOperationError('Cannot get or create FlexContainer specialization. '  + MCA.lastError)


	def __str__(self):
		result = 'FlexContainer:\n'
		result += ResourceBase.__str__(self)
		result += INT.strResource('resourceSpecialization', None, self.resourceSpecialization)
		result += INT.strResource('contentDefinition', 'cnd', self.contentDefinition)

		# TODO attributes
		return result


	def _copy(self, resource):
		ResourceBase._copy(self, resource)
		self.resourceSpecialization = resource.resourceSpecialization
		self.contentDefinition = resource.contentDefinition
		# TODO attributes