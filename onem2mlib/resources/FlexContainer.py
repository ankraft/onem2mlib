#
#	FlexContainer.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module implements the class for the <FlexContainer> resource.
#

import logging
import onem2mlib.marshalling as M
import onem2mlib.constants as CON
import onem2mlib.internal as INT
import onem2mlib.mcarequests as MCA
import onem2mlib.exceptions as EXC
from .ResourceBase import ResourceBase

logger = logging.getLogger(__name__)

class FlexContainer(ResourceBase):
	"""
	This class implements the oneM2M &lt;flexContainer> resource. 

	This is only a base class with the basic &lt;flexContainer> functionalities.
	It should be inherited to implement flexContainer specializations.
	"""

	def __init__(self, 
				 resourceSpecialization: str | None = None, 
				 contentDefinition: str | None = None, 
				 attributes: dict | None = None, 
				 instantly: bool = True, 
				 **kwargs):
		"""
		Initialize the &lt;flexContainer> resource. 

		Args:
			resourceSpecialization: The specialization name (used as typeShortName, e.g., 'cod:light').
			contentDefinition: The URI defining the content of this specialization.
			attributes: A dictionary of custom attributes for this specialization.
			instantly: If True, the resource is immediately synced with the CSE.
			**kwargs: Inherited attributes (parent, resourceName, labels, originator, etc.)
		"""
		super().__init__(
			type=CON.Type_FlexContainer, 
			typeShortName=resourceSpecialization, 
			**kwargs
		)

		self._marshallers = [M._FlexContainer_parseXML, M._FlexContainer_createXML,
							 M._FlexContainer_parseJSON, M._FlexContainer_createJSON]

		self.resourceSpecialization = resourceSpecialization
		self.contentDefinition = contentDefinition
		self.attributes = attributes # TODO

		if instantly:
			if not self.get():
				logger.error(f'Cannot get or create FlexContainer specialization. {MCA.lastError}')
				raise EXC.CSEOperationError(f'Cannot get or create FlexContainer specialization. {MCA.lastError}')


	def __str__(self):
		result = 'FlexContainer:\n'
		result += super().__str__()
		result += INT.strResource('resourceSpecialization', None, self.resourceSpecialization)
		result += INT.strResource('contentDefinition', 'cnd', self.contentDefinition)

		# TODO attributes
		return result


	def _copy(self, resource: 'FlexContainer'):
		super()._copy(resource)
		self.resourceSpecialization = resource.resourceSpecialization
		self.contentDefinition = resource.contentDefinition
		# TODO attributes