#
#	AE.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
""" This module implements the class for the <AE> resource. """

from __future__ import annotations
from typing import Optional, Any, cast, override, TYPE_CHECKING

import logging
from .. import constants as CON
from .. import exceptions as EXC
from .. import mcarequests as MCA
from .. import internal as INT
from .Group import Group
from .ResourceBase import ResourceBase
from .Container import Container


if TYPE_CHECKING:
	from .Session import Session


logger = logging.getLogger(__name__)
""" Logger for this module. """

class AE(ResourceBase):
	"""	This class implements the oneM2M <AE> resource. 

		It is always a child-resource of the <CSEBase> resource, and it represents an 
		application and the sub-structure of resources beneath it.
	"""

	def __init__(self,
              	 appID: Optional[str] = None,
              	 AEID: Optional[str] = None,
                 requestReachability: bool = True, 
				 nodeLink: Optional[str] = None,
     			 instantly: bool = True,
         		 **kwargs: Any) -> None:
		"""	Initialize the <AE> resource. 

			Args:
				appID: Identifier of the Application. Defaults to resourceName if not provided.
				AEID: Identifier of the Application Entity.
				requestReachability: Reachability status of the AE.
				nodeLink: Resource ID of the associated node resource.
				instantly: If True, the resource is immediately synced with the CSE.
				**kwargs: Inherited attributes (parent, resourceName, labels, originator, etc.)
			
			Raises:
				onem2mlib.exceptions.ParameterError: If the parent resource is not a <CSEBase>.
		"""
		if not appID:
			appID = kwargs.get('resourceName')
		
		# For non-registered entities, the appID has to start with an 'N'
		if appID and not appID.startswith('N'):
			appID = 'N' + appID

		super().__init__(type=CON.Type_AE, typeShortName=CON.Type_AE_SN, **kwargs)

		if self.parent is not None and self.parent.type not in [CON.Type_CSEBase]:
			logger.error('Parent of <AE> must be <CSEBase>')
			raise EXC.ParameterError('Parent must be <CSEBase>.')


		# Set AE-Specific Attributes
		self.appID: Optional[str] = appID
		""" String. The identifier of the Application. Assigned by the application or the CSE. """

		self.AEID: Optional[str] = AEID
		""" String. The identifier of the Application Entity. Assigned by the application or the CSE. """

		self.requestReachability: bool = requestReachability
		""" Boolean. This indicates the reachability of the AE.	Assigned by the application or the CSE. """

		self.pointOfAccess: list[str] = []
		""" List of String. The list of addresses for communicating with the registered AE. """

		self.nodeLink: Optional[str] = nodeLink
		""" The resource identifier of a <node> resource that stores the node specific information
			of the node on which the AE represented by this <AE> resource resides.
		"""

		self.supportedReleaseVersions: list[str] = ['3']
		""" List of String. The list of supported release versions. """

		if instantly:
			if not self.get():
				raise EXC.CSEOperationError(f'Cannot get or create AE. {MCA.lastError}')


	def __str__(self) -> str:
		"""	Return a string representation of the AE resource, including its attributes.

			Returns:
				A string representation of the AE resource, including its attributes.
		"""

		return	'AE:\n' + \
				super().__str__() + \
			    INT.strResource('appID', 'api', self.appID) + \
			    INT.strResource('AEID', 'aei', self.AEID) + \
			    INT.strResource('requestReachability', 'rr', self.requestReachability) + \
			    INT.strResource('pointOfAccess', 'poa', self.pointOfAccess) + \
			    INT.strResource('nodeLink', 'nl', self.nodeLink) + \
			    INT.strResource('supportedReleaseVersions', 'srv', self.supportedReleaseVersions)


	def containers(self, filter: Optional[list[tuple[str, str|int|bool]]] = None) -> list[Container]:
		"""	Return a list of all <container> resources of this <AE>, or an empty list.

			Args:
				filter: Optional list of tuples (attribute, value) to filter the containers.
			
			Returns:
				A list of <container> resources that are child-resources of this 
					<AE> resource, or an empty list if there are none.
		"""
		return cast(list[Container], INT._findSubResource(self, CON.Type_Container, filter=filter))


	def addContainer(self, 
					 resourceName: Optional[str] = None, 
					 maxNrOfInstances: Optional[int] = None, 
					 maxByteSize: Optional[int] = None, 
					 maxInstanceAge: Optional[int] = None, 
					 instantly: bool = True, 
					 **kwargs: Any) -> Container:
		"""
		Add a new <container> child-resource. 

		Args:
			resourceName: Name of the new container.
			maxNrOfInstances: Max number of contentInstances allowed.
			maxByteSize: Max total byte size allowed.
			maxInstanceAge: Max age of instances in seconds.
			instantly: If True, immediately sync with the CSE.
			**kwargs: Optional attributes like labels, originator, etc.
		"""
		return Container(parent=self, 
						 resourceName=resourceName, 
						 maxNrOfInstances=maxNrOfInstances, 
						 maxByteSize=maxByteSize, 
						 maxInstanceAge=maxInstanceAge, 
						 instantly=instantly, 
						 **kwargs
		)


	def groups(self, filter: Optional[list[tuple[str, str|int|bool]]] = None) -> list[Group]:
		"""	Return a list of all <group> resources of this <AE>, or an empty list.

			Args:
				filter: Optional list of tuples (attribute, value) to filter the groups.
			
			Returns:
				A list of <group> resources that are child-resources of this 
					<AE> resource, or an empty list if there are none.
		"""
		return cast(list[Group], INT._findSubResource(self, CON.Type_Group, filter=filter))


	def addGroup(self, 
				 resourceName: Optional[str] = None, 
				 resources: Optional[list] = None, 
				 maxNrOfMembers: int = CON.Grp_def_maxNrOfMembers, 
				 consistencyStrategy: int = CON.Grp_ABANDON_MEMBER, 
				 groupName: Optional[str] = None, 
				 instantly: bool = True, 
				 **kwargs: Any) -> Group:
		"""
		Add a new <group> child-resource.

		Args:
			resourceName: Name of the group resource.
			resources: List of member resource objects.
			maxNrOfMembers: Max members allowed in the group.
			consistencyStrategy: Strategy for member type validation.
			groupName: Human-readable name for the group.
			instantly: If True, immediately sync with the CSE.
			**kwargs: Optional attributes like labels, originator, etc.
		"""
		from .Group import Group
		return Group(parent=self, 
					 resourceName=resourceName, 
					 resources=resources, 
					 maxNrOfMembers=maxNrOfMembers, 
					 consistencyStrategy=consistencyStrategy, 
					 groupName=groupName, 
					 instantly=instantly, 
					 **kwargs
		)


	@override
	def _copy(self, resource: AE) -> None:	# type: ignore[override]
		super()._copy(resource)
		self.appID = resource.appID
		self.AEID = resource.AEID
		self.requestReachability = resource.requestReachability
		self.pointOfAccess = resource.pointOfAccess
		self.nodeLink = resource.nodeLink


	def _fromCSE(self, jsn: dict) -> None:
		""" Update the attributes of this AE resource from a JSON representation.

				Args:
					jsn: The JSON representation of the resource as a dictionary.
		"""
		_jsn = super()._fromCSE(jsn)
		self.appID = INT.getElementJSON(_jsn, 'api', self.appID)
		self.AEID = INT.getElementJSON(_jsn, 'aei', self.AEID)
		self.requestReachability = INT.getElementJSON(_jsn, 'rr', self.requestReachability)
		self.pointOfAccess = INT.getElementJSON(_jsn, 'poa', self.pointOfAccess)	
		self.nodeLink = INT.getElementJSON(_jsn, 'nl', self.nodeLink)

		# override originator
		self.originator = self.AEID


	def _toCSE(self, isUpdate: bool = False, isAcpiUpdate: bool = False) -> dict:
		""" Return a JSON representation of this AE resource as a dictionary, to be sent to the CSE.

			Args:
				isUpdate: If True, this JSON is for an update operation.
				isAcpiUpdate: If True, this JSON is for an ACP update operation.
				
			Returns:
				A JSON representation of this AE resource as a dictionary, to be sent to the CSE.
		"""
		jsn = super()._toCSE(isUpdate, isAcpiUpdate)

		if isUpdate and isAcpiUpdate:
			return INT.wrapJSON(self, jsn)
		if self.appID and not isUpdate: 		# No api when updating
			INT.addToElementJSON(jsn, 'api', self.appID)
		if self.AEID and not isUpdate:	# No api when updating
			INT.addToElementJSON(jsn, 'aei', self.AEID)
		INT.addToElementJSON(jsn, 'rr', self.requestReachability)
		INT.addToElementJSON(jsn, 'poa', self.pointOfAccess)
		INT.addToElementJSON(jsn, 'nl', self.nodeLink)
		INT.addToElementJSON(jsn, 'srv', self.supportedReleaseVersions)
		return INT.wrapJSON(self, jsn)
