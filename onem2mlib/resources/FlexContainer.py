#
#	FlexContainer.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
""" This module implements the class for the <FlexContainer> resource. """

from __future__ import annotations
from typing import Optional, Any, cast, override

import logging
import onem2mlib.constants as CON
import onem2mlib.internal as INT
import onem2mlib.mcarequests as MCA
import onem2mlib.exceptions as EXC
from .ResourceBase import ResourceBase

logger = logging.getLogger(__name__)
""" Logger for this module. """

class FlexContainer(ResourceBase):
	"""	This class implements the oneM2M <flexContainer> resource. 

		This is only a base class with the basic <flexContainer> functionalities.
		It should be inherited to implement <flexContainer> specializations.
	"""

	def __init__(self, 
				 resourceSpecialization: Optional[str] = None, 
				 contentDefinition: Optional[str] = None, 
				 attributes: Optional[dict] = None, 
				 instantly: bool = True, 
				 **kwargs: Any) -> None:
		"""	Initialize the <flexContainer> resource. 

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

		self.resourceSpecialization = resourceSpecialization
		self.contentDefinition = contentDefinition
		self.attributes = attributes # TODO

		if instantly:
			if not self.get():
				logger.error(f'Cannot get or create FlexContainer specialization. {MCA.lastError}')
				raise EXC.CSEOperationError(f'Cannot get or create FlexContainer specialization. {MCA.lastError}')


	def __str__(self) -> str:
		return	'FlexContainer:\n' + \
				super().__str__() + \
				INT.strResource('resourceSpecialization', None, self.resourceSpecialization) + \
				INT.strResource('contentDefinition', 'cnd', self.contentDefinition)
		# TODO attributes


	@override
	def _copy(self, resource: FlexContainer) -> None:	# type: ignore[override]
		super()._copy(resource)
		self.resourceSpecialization = resource.resourceSpecialization
		self.contentDefinition = resource.contentDefinition
		# TODO attributes

	def _fromCSE(self, jsn: dict) -> None:
		""" Update the attributes of this Group resource from a JSON representation.

				Args:
					jsn: The JSON representation of the resource as a dictionary.
		"""
		_jsn = super()._fromCSE(jsn)
		self.contentDefinition = INT.getElementJSON(jsn, 'cnd', self.contentDefinition)
		# TODO Attributes


	def _toCSE(self, isUpdate: bool = False, isAcpiUpdate: bool = False) -> dict:
		""" Return a JSON representation of this Group resource as a dictionary, to be sent to the CSE.

			Args:
				isUpdate: If True, this JSON is for an update operation.
				isAcpiUpdate: If True, this JSON is for an ACP update operation.
				
			Returns:
				A JSON representation of this Group resource as a dictionary, to be sent to the CSE.
		"""
		jsn = super()._toCSE(isUpdate, isAcpiUpdate)
		if isUpdate and isAcpiUpdate:
			return INT.wrapJSON(self, jsn)
		INT.addToElementJSON(jsn, 'cnd', self.contentDefinition)
		# >TODO attribues
		return INT.wrapJSON(self, jsn)

