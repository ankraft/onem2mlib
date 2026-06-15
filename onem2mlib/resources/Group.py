#
#	Group.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module implements the class for the <Group> resource.
#

from __future__ import annotations
from typing import Optional, Any, override, TYPE_CHECKING

import logging
import onem2mlib.constants as CON
import onem2mlib.internal as INT
import onem2mlib.mcarequests as MCA
import onem2mlib.exceptions as EXC
from .ResourceBase import ResourceBase

if TYPE_CHECKING:
	from requests import Response

logger = logging.getLogger(__name__)

class Group(ResourceBase):
	"""
	This class implements the oneM2M <group> resource. 

	The <group> resource represents a group of resources of the same or mixed types. 
	The <group> resource can be used to do bulk manipulations on the resources represented by the
	`onem2mlib.Group.memberIDs` attribute. The <group> resource contains an attribute that represents the members of 
	the group and the <fanOutPoint> virtual resource that enables generic operations to be applied 
	to all the resources represented by those members.
	"""

	def __init__(self, 
			  	 resources: Optional[list[ResourceBase]] = None, 
			  	 maxNrOfMembers: int = CON.Grp_def_maxNrOfMembers, 
				 consistencyStrategy: int = CON.Grp_ABANDON_MEMBER, 
			 	 groupName: Optional[str] = None, 
				 instantly: bool = True, 
				 **kwargs: Any) -> None:
		"""
		Initialize the <group> resource. 

		Args:
			resources: A list of resource instances to be members of the group.
			maxNrOfMembers: Maximum number of members allowed.
			consistencyStrategy: How to handle type inconsistencies.
			groupName: Human readable name of the group.
			instantly: If True, the resource is immediately synced with the CSE.
			**kwargs: Inherited attributes (parent, resourceName, labels, originator, etc.)
		"""
		super().__init__(type=CON.Type_Group, typeShortName=CON.Type_Group_SN, **kwargs)

		self.maxNrOfMembers: int = maxNrOfMembers
		""" Maximum number of members in the <group>. """

		self.resources : Optional[list[ResourceBase]] = resources
		""" List of resource instances. The resources in this <group>. """
		
		self.currentNrOfMembers: int = len(resources) if resources else 0
		""" Current number of members in a <group>. It shall not be larger than `onem2mlib.Group.maxNrOfMembers`. R/O. """
		
		self.memberTypeValidated: Optional[bool] = None
		""" Denotes if the resource types of all members resources 
			of the <group> has been validated by the Hosting CSE. In the case that the `onem2mlib.Group.memberType` 
			attribute of the <group> resource is not 'mixed', then this attribute shall be set. """

		self.consistencyStrategy: int = consistencyStrategy
		""" This attribute determines how to deal with the <group> resource if the `onem2mlib.Group.memberType`
			validation fails. Its possible values (from the `onem2mlib.constants` sub-module) are

			- *Grp_ABANDON_MEMBER* : delete the inconsistent member
			- *Grp_ABANDON_GROUP* : delete the group
			- *Grp_SET_MIXED* : set the *memberType* to "mixed"

			The default is *Grp_ABANDON_MEMBER*. """
		
		self.groupName: Optional[str] = groupName
		""" Human readable name of the <group>. """

		self.fanOutPoint: Optional[str] = None
		""" The resourceID of the virtual <fanOutPoint> resource. Whenever a request is sent 
			to the <fanOutPoint> resource, the request is fanned out to each of the members of the
			<group> resource indicated by the `onem2mlib.Group.memberIDs` attribute of the <group> resource. R/O. """

		self.memberType: int = self._determineMemberType()
		""" This is the resource type of the member resources of the group, if all member
			resources (including the member resources in any sub-groups) are of the same type.
			Otherwise, it is of type 'mixed'. W/O. """

		# assign the resource ids
		self.memberIDs: list[str] = [ res.resourceID for res in self.resources ]
		""" List of member resource IDs. Each memberID should refer to a member resource or a 
			(sub-) <group> resource of the <group>. """

		if instantly:
			if not self.get():
				logger.critical(f'Cannot get or create Group. {MCA.lastError}')
				raise EXC.CSEOperationError(f'Cannot get or create Group. {MCA.lastError}')


	def _determineMemberType(self) -> int:
		""" Internal helper to determine if the group is of a specific type or 'Mixed'. """
		if not self.resources:
			return CON.Type_Mixed
		
		first_type = self.resources[0].type
		for res in self.resources:
			if res.type != first_type:
				return CON.Type_Mixed
		return first_type


	def __str__(self) -> str:
		return	'Group:\n' + \
				super().__str__() + \
				INT.strResource('maxNrOfMembers', 'mnm', self.maxNrOfMembers) + \
				INT.strResource('memberType', 'mt', self.memberType) + \
				INT.strResource('currentNrOfMembers', 'cnm', self.currentNrOfMembers) + \
				INT.strResource('memberIDs', 'mid', self.memberIDs) + \
				INT.strResource('memberTypeValidated', 'mtv', self.memberTypeValidated) + \
				INT.strResource('consistencyStrategy', 'csy', self.consistencyStrategy) + \
				INT.strResource('groupName', 'gn', self.groupName) + \
				INT.strResource('fanOutPoint', 'fopt', self.fanOutPoint)


	def getGroupResources(self) -> Optional[list[ResourceBase]]:
		"""	Return the resources that are managed by this <group> resource. 
		
			Returns:
				A list of the group resources, or *None* if there was an error.
		"""
		if not self._isValidFanOutPoint(): return None
		response = MCA.get(self.session, self.fanOutPoint, originator=self.originator)
		return self._parseFanOutPointResponse(response)


	def deleteGroupResources(self) -> bool:
		"""	Delete the resources that are managed by this <group> resource. 
			It returns *True* or *False* respectively.

			Note:
				Note, that the <group> itself is not deleted or altered. It must be deleted separately, if necessary.

			Returns:
				*True* if the deletion was successful, *False* otherwise.
		"""
		if not self._isValidFanOutPoint():
			return False
		response = MCA.delete(self.session, self.fanOutPoint, originator=self.originator)
		return response is not None and response.status_code == 200


	def updateGroupResources(self, resource: Group) -> Optional[list[ResourceBase]]:
		""" Update the resources that are managed by this <group> resource.

			Args:
				resource: A `Group` object that acts as a template to update the group resources.

			Returns:
				A list of the updated resources, or *None* in case of an error.
			
			Note:
				In the returned resource instances only the properties are set that have been
					updated either by the update operation or as a side effect by the CSE, such as the
					`onem2mlib.ResourceBase.lastModifiedTime`. The order of the instances in the result list is the same as the order of 
					the resource identifiers in `onem2mlib.Group.memberIDs`.
		"""
		if not self._isValidFanOutPoint(): return None
		
		# Use internal helper to generate body based on encoding
		body = resource._createContent(isUpdate=True)
		response = MCA.update(self.session, self.fanOutPoint, resource.type, body, originator=self.originator)
		return self._parseFanOutPointResponse(response)


	def createGroupResources(self, resource: ResourceBase) -> Optional[list[ResourceBase]]:
		""" Create/add a resource at all the resources managed by this <group> resource.

			Args:
				resource: A `ResourceBase` object that acts as a template to create/add the resource at the group resources. 
					The type of the resource must be the same as the type of the group members, or 'mixed'.

			Returns:
				A list of the created resources, or *None* in case of an error.
		"""
		if not resource.session:
			resource.session = self.session
		if not self._isValidFanOutPoint(): return None
		body = resource._createContent(isUpdate=True)
		response = MCA.create(self.session, self.fanOutPoint, resource.type, body, originator=self.originator)
		return self._parseFanOutPointResponse(response)


	def _parseFanOutPointResponse(self, response: Response) -> Optional[list[ResourceBase]]:
		# Get the resources from the answer
		if response and response.status_code == 200:
			elements = INT.getALLSubElementsJSON(response.json(), 'm2m:pc')
			resources = []
			for elem in elements:
				keyWithoutPrefix = list(elem.keys())[0].replace('m2m:','')		# TODO check this for other domains, eg. hd
				resource = INT._newResourceFromTypeString(keyWithoutPrefix, self)
				if resource:
					resource._fromCSE(elem)
					resources.append(resource)
			return resources
		return None


	def _isValidFanOutPoint(self) -> bool:
		return self.fanOutPoint is not None and len(self.fanOutPoint) > 0 and self.session is not None


	@override
	def _copy(self, resource: Group) -> None:	# type: ignore[override]
		super()._copy(resource)
		self.maxNrOfMembers = resource.maxNrOfMembers
		self.memberType = resource.memberType
		self.currentNrOfMembers = resource.currentNrOfMembers
		self.memberIDs = resource.memberIDs
		self.memberTypeValidated = resource.memberTypeValidated
		self.consistencyStrategy = resource.consistencyStrategy
		self.groupName = resource.groupName
		self.fanOutPoint = resource.fanOutPoint


	def _fromCSE(self, jsn: dict) -> None:
		""" Update the attributes of this Group resource from a JSON representation.

				Args:
					jsn: The JSON representation of the resource as a dictionary.
		"""
		_jsn = super()._fromCSE(jsn)
		self.maxNrOfMembers = INT.getElementJSON(_jsn, 'mnm', self.maxNrOfMembers)
		self.memberType = INT.getElementJSON(_jsn, 'mt', self.memberType)
		self.currentNrOfMembers = INT.getElementJSON(_jsn, 'cnm', self.currentNrOfMembers)
		self.memberIDs = INT.getElementJSON(_jsn, 'mid', self.memberIDs)
		self.memberTypeValidated = INT.getElementJSON(_jsn, 'mtv', self.memberTypeValidated)
		self.consistencyStrategy = INT.getElementJSON(_jsn, 'csy', self.consistencyStrategy)
		self.groupName = INT.getElementJSON(_jsn, 'gn', self.groupName)
		self.fanOutPoint = f'{self._structuredResourceID()}/fopt'


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
		if self.maxNrOfMembers and not isUpdate: 	# No mnm when updating
			INT.addToElementJSON(jsn, 'mnm', self.maxNrOfMembers)
		INT.addToElementJSON(jsn, 'mt', self.memberType)
		INT.addToElementJSON(jsn, 'mid', self.memberIDs, mandatory=True)
		if self.consistencyStrategy and not isUpdate: 	# No csy when updating
			INT.addToElementJSON(jsn, 'csy', self.consistencyStrategy)
		INT.addToElementJSON(jsn, 'gn', self.groupName)
		return INT.wrapJSON(self, jsn)


