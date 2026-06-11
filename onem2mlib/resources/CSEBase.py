#
#	CSEBase.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
""" This module implements the class for the <CSEBase> resource. """

from __future__ import annotations
from typing import Optional, Any, cast, override, TYPE_CHECKING

import logging

from .. import marshalling as M
from .. import constants as CON
from .. import internal as INT
from .. import mcarequests as MCA
from .. import exceptions as EXC
from .ResourceBase import ResourceBase
from .AE import AE
from .Container import Container
from .FlexContainer import FlexContainer
from .Group import Group

if TYPE_CHECKING:
	from .RemoteCSE import RemoteCSE
	from .Session import Session
	from .AccessControlPolicy import AccessControlPolicy

logger = logging.getLogger(__name__)

class CSEBase(ResourceBase):
	"""	CSEBase holds the attributes of a CSE and gives access to resources under it.
	
		When created and initialized correctly, it is automatically retrieved from the
		CSE immediatly.
	"""

	def __init__(self, 
				 session: Session = None, 
				 cseID: Optional[str] = None, 
				 instantly: bool = True, 
				 **kwargs: Any) -> None:
		"""
		Initialize a CSEBase object.

		Args:
			session: A Session object holding connection info.
			cseID: The CSE-ID of the CSE (assigned to resourceID).
			instantly: If True, the resource is immediately retrieved from the CSE.
			**kwargs: Inherited attributes (resourceName, originator, etc.)
		"""
		super().__init__(
			parent=None, 
			resourceID=cseID, 
			type=CON.Type_CSEBase, 
			typeShortName=CON.Type_CSEBase_SN, 
			**kwargs
		)

		self._marshallers = [M._CSEBase_parseXML, None, M._CSEBase_parseJSON, None]
		
		self.session = session
		self.cseType: int | None = None
		""" Integer. The type of the CSE. See also the type constants in `onem2mlib.constants`.
			Assigned by the CSE. R/O."""
		
		self.supportedResourceTypes: list[int] = []
		""" list of supported resource types of this CSE. Assigned by the CSE. R/O. """
		
		self.pointOfAccess: list[str] = []
		""" A list of physical addresses to be used by remote CSEs to connect to this CSE. Assigned by the CSE. R/O. """

		if instantly:
			if not self.retrieveFromCSE():
				logger.critical(f'Cannot get CSEBase. {MCA.lastError}')
				raise EXC.CSEOperationError(f'Cannot get CSEBase. {MCA.lastError}')


	def __str__(self) -> str:
		"""	Return a string representation of the CSEBase resource, including its attributes and child resources.
		
			Returns:
				A string representation of the CSEBase resource, including its attributes and child resources.
		"""
		return	'CSEBase:\n' + \
				super().__str__() + \
			    INT.strResource('cseType', 'cst', self.cseType) + \
			    INT.strResource('supportedResourceTypes', 'srt', self.supportedResourceTypes) + \
			    INT.strResource('pointOfAccess', 'poa', self.pointOfAccess)



	# --- Convenience Methods for Child Resources ---

	def addAE(self, 
			  resourceName: Optional[str] = None, 
			  appID: Optional[str] = None, 
			  AEID: Optional[str] = None, 
			  requestReachability: bool = True, 
			  instantly: bool = True, 
			  **kwargs: Any
		) -> AE:
		"""
		Convenience function to create a new <AE> in the <CSEBase>.
		"""
		return AE(parent=self,
				  resourceName=resourceName,
				  appID=appID,
				  AEID=AEID,
				  requestReachability=requestReachability,
				  instantly=instantly,
				  **kwargs
		)


	def addContainer(self, 
					 resourceName: Optional[str] = None, 
					 maxNrOfInstances: Optional[int] = None, 
					 maxByteSize: Optional[int] = None, 
					 maxInstanceAge: Optional[int] = None, 
					 instantly: bool = True, 
					 **kwargs: Any) -> Container:
		"""
		Convenience function to create a new <container> in the <CSEBase>.
		"""
		return Container(parent=self,
						 resourceName=resourceName,
						 maxNrOfInstances=maxNrOfInstances,
						 maxByteSize=maxByteSize,
						 maxInstanceAge=maxInstanceAge,
						 instantly=instantly,
						 **kwargs
		)


	def addGroup(self, 
				 resourceName: Optional[str] = None, 
				 resources: Optional[list] = None, 
				 maxNrOfMembers: int = CON.Grp_def_maxNrOfMembers, 
				 consistencyStrategy: int = CON.Grp_ABANDON_MEMBER, 
				 groupName: Optional[str] = None, 
				 instantly: bool = True, 
				 **kwargs: Any) -> Group:
		"""
		Convenience function to create a new <group> in the <CSEBase>.
		"""
		return Group(parent=self,
					 resourceName=resourceName,
					 resources=resources,
					 maxNrOfMembers=maxNrOfMembers,
					 consistencyStrategy=consistencyStrategy,
					 groupName=groupName,
					 instantly=instantly,
					 **kwargs
		)

	def addFlexContainer(self, 
						 resourceSpecialization: Optional[str] = None, 
						 contentDefinition: Optional[str] = None, 
						 attributes: Optional[dict] = None, 
						 instantly: bool = True, 
						 **kwargs: Any) -> FlexContainer:
		"""
		Convenience function to create a new <flexContainer> in the <CSEBase>.
		"""
		return FlexContainer(parent=self,
							 resourceSpecialization=resourceSpecialization,
							 contentDefinition=contentDefinition,
							 attributes=attributes,
							 instantly=instantly,
							 **kwargs
		)


	# --- Resource Discovery Helpers ---

	def accessControlPolicies(self, filter: Optional[list[tuple[str, str|int|bool]]] = None) -> list[AccessControlPolicy]:
		"""	Return a list of <accessControlPolicy> resources from this CSE, or an empty list.

			Args:
				filter: Optional list of tuples (attribute, value) to filter the access control policies.

			Returns:
				A list of <accessControlPolicy> resources that are child-resources of this <CSEBase> resource, or an empty list if there are none.
		"""
		return INT._findSubResource(self, CON.Type_ACP, filter=filter) # type: ignore[return-value]


	def aes(self, filter: Optional[list[tuple[str, str|int|bool]]] = None) -> list[AE]:
		"""	Return a list of <AE> resources from this CSE, or an empty list.

			Args:
				filter: Optional list of tuples (attribute, value) to filter the AEs.

			Returns:
				A list of <AE> resources that are child-resources of this <CSEBase> resource, or an empty list if there are none.
		"""
		return INT._findSubResource(self, CON.Type_AE, filter=filter) # type: ignore[return-value]


	def containers(self, filter: Optional[list[tuple[str, str|int|bool]]] = None) -> list[Container]:
		"""	Return a list of <container> resources from this CSE, or an empty list.

			Args:
				filter: Optional list of tuples (attribute, value) to filter the containers.

			Returns:
				A list of <container> resources that are child-resources of this <CSEBase> resource, or an empty list if there are none.
		"""
		return INT._findSubResource(self, CON.Type_Container, filter=filter) # type: ignore[return-value]


	def groups(self, filter: Optional[list[tuple[str, str|int|bool]]] = None) -> list[Group]:
		"""	Return a list of <group> resources from this CSE, or an empty list.

			Args:
				filter: Optional list of tuples (attribute, value) to filter the groups.

			Returns:
				A list of <group> resources that are child-resources of this <CSEBase> resource, or an empty list if there are none.
		"""
		return INT._findSubResource(self, CON.Type_Group, filter=filter) # type: ignore[return-value]


	def remoteCSEs(self, filter: Optional[list[tuple[str, str|int|bool]]] = None) -> list[RemoteCSE]:
		"""	Return a list of <remoteCSE> resources from this CSE, or an empty list.

			Args:
				filter: Optional list of tuples (attribute, value) to filter the remote CSEs.

			Returns:
				A list of <remoteCSE> resources that are child-resources of this <CSEBase> resource, or an empty list if there are none.
		"""
		return INT._findSubResource(self, CON.Type_RemoteCSE, filter=filter)	# type: ignore[return-value]


	@override
	def _copy(self, resource: CSEBase) -> None:	# type: ignore[override]
		super()._copy(resource)
		self.cseType = resource.cseType
		self.supportedResourceTypes = resource.supportedResourceTypes
		self.pointOfAccess = resource.pointOfAccess