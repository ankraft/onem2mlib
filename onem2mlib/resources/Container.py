#
#	Container.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
""" This module implements the class for the <Container> resource. """

from __future__ import annotations
from typing import Optional, Any, cast, override

import logging
import onem2mlib.marshalling as M
import onem2mlib.constants as CON
import onem2mlib.internal as INT
import onem2mlib.mcarequests as MCA
import onem2mlib.exceptions as EXC

from .ResourceBase import ResourceBase
from .ContentInstance import ContentInstance


logger = logging.getLogger(__name__)

class Container(ResourceBase):
	"""	This class implements the oneM2M <container> resource. 

		It is usually a child-resource of the <AE> or other resources.
	"""

	def __init__(self,
                 maxNrOfInstances: Optional[int] = None,
                 maxByteSize: Optional[int] = None, 
				 maxInstanceAge: Optional[int] = None,
     			 instantly: bool = True,
        		 **kwargs: Any) -> None:
		"""	Initialize the <container> resource. 

			Args:
				maxNrOfInstances: Maximum number of direct child <contentInstance> resources.
				maxByteSize: Maximum size in bytes of data allocated for the container.
				maxInstanceAge: Maximum age (seconds) of a child <contentInstance>.
				instantly: If True, the resource is immediately synced with the CSE.
				**kwargs: Inherited attributes (parent, resourceName, resourceID, labels, originator, etc.)
		"""
		super().__init__(type=CON.Type_Container, typeShortName=CON.Type_Container_SN, **kwargs)

		self._marshallers = [M._Container_parseXML, M._Container_createXML,
							 M._Container_parseJSON, M._Container_createJSON]

		self.maxNrOfInstances = maxNrOfInstances
		""" Integer. Maximum number of direct child <contentInstance> resources in the 
		<container> resource."""

		self.maxByteSize = maxByteSize
		""" Integer. Maximum size in bytes of data (i.e. content attribute of a <contentInstance>
		resource) that is allocated for the <container> resource for all direct child 
		<contentInstance> resources in the <container> resource."""

		self.maxInstanceAge = maxInstanceAge
		""" Integer.Maximum age of a direct child <contentInstance> resource in the <container>
		resource. The value is expressed in seconds. R/O."""

		self.currentNrOfInstances: Optional[int] = None
		""" Integer. Current number of direct child <contentInstance> resource in the <container> 
		resource. It is limited by the `onem2mlib.Container.maxNrOfInstances` property. R/O."""
		
		self.currentByteSize: Optional[int] = None
		""" Integer. Current size in bytes of data (i.e. content attribute of a <contentInstance>
		resource) stored in all direct child <contentInstance> resources of a <container> resource.
		This is the summation of contentSize attribute values of the <contentInstance> resources. 
		It is limited by the `onem2mlib.Container.maxByteSize` property. R/O."""

		self.oldest = None
		""" String. The resourceID of the oldest <contentInstance> resource in this <container>
		resource. R/O. """

		self.latest = None
		""" String. The resourceID of the latest (newest) <contentInstance> resource in this 
		<container>. R/O. """

		if instantly:
			if not self.get():
				logger.critical(f'Cannot get or create Container. {MCA.lastError}')
				raise EXC.CSEOperationError(f'Cannot get or create Container. {MCA.lastError}')


	def __str__(self) -> str:
		""" Return a string representation of the Container resource.
		
			Returns:
				A string representation of the Container resource.
		"""
		return	'Container:\n' + \
				super().__str__() + \
				INT.strResource('maxNrOfInstances', 'mni', self.maxNrOfInstances) + \
				INT.strResource('maxByteSize', 'mbs', self.maxByteSize) + \
				INT.strResource('maxInstanceAge', 'mia', self.maxInstanceAge) + \
				INT.strResource('currentNrOfInstances', 'cni', self.currentNrOfInstances) + \
				INT.strResource('currentByteSize', 'cbs', self.currentByteSize) + \
				INT.strResource('oldest', 'ol', self.oldest) + \
				INT.strResource('latest', 'la', self.latest)


	def containers(self, filter: list[tuple[str, str|int|bool]] = None) -> list[Container]:
		""" Return all <container> child-resources from this container, or an empty list.

			Args:
				filter: Optional list of tuples (attribute, value) to filter the containers.

			Returns:
				A list of <container> resources that are child-resources of this <container> resource, 
					or an empty list if there are none.
		"""
		return cast(list[Container], INT._findSubResource(self, CON.Type_Container, filter=filter))


	def addContainer(self,
                     resourceName: Optional[str] = None,
                     maxNrOfInstances: Optional[int] = None, 
                 	 maxByteSize: Optional[int] = None,
                     maxInstanceAge: Optional[int] = None,
                     **kwargs: Any) -> Container:
		"""	Add a new <container> child-resource. 

			Args:
				resourceName: The name of the new container.
				maxNrOfInstances: Maximum number of child contentInstances.
				maxByteSize: Maximum byte size of all child contentInstances.
				maxInstanceAge: Maximum age of child contentInstances (seconds).
				**kwargs: Optional base attributes (labels, originator, accessControlPolicies, etc.)
		
			Returns:
				The new Container object.
		"""

		return Container(
			parent=self,
			resourceName=resourceName,
			maxNrOfInstances=maxNrOfInstances,
			maxByteSize=maxByteSize,
			maxInstanceAge=maxInstanceAge,
			**kwargs
		)


	def contentInstances(self, filter: Optional[list[tuple[str, str|int|bool]]] = None) -> list[ContentInstance]:
		"""	Return all <contentInstance> child-resources from this container, or an empty list.

			Args:
				filter: Optional list of tuples (attribute, value) to filter the contentInstances.

			Returns:
				A list of <contentInstance> resources that are child-resources of this <container> resource, or an empty list if there are none.

		"""
		return cast(list[ContentInstance], INT._findSubResource(self, CON.Type_ContentInstance, filter=filter))


	def contents(self, filter: Optional[list[tuple[str, str|int|bool]]] = None) -> list[str]:
		"""	Return all content from all <contentInstance>'s in list, or an empty list.

			Args:
				filter: Optional list of tuples (attribute, value) to filter the contentInstances.

			Returns:
				A list of content values from all <contentInstance> resources that are child-resources of this <container> resource, or an empty list if there are none.
		"""
		return [cin.content for cin in self.contentInstances(filter=filter)]


	def addContent(self,
                   value: str | int | float | bool,
                   contentInfo: Optional[str] = None,
                   **kwargs: Any) -> ContentInstance:
		"""	Add a new value to a container as a <contentInstance>.
		
			Args:
				value: The content to be added (converted to str if necessary).
				contentInfo: Optional metadata (e.g., 'text/plain:0').
				**kwargs: Optional attributes common to all resources (resourceName, labels, originator).

			Returns:
				The new <contentInstance> resource that was created to hold the content value.
		"""
		if value is not None and not isinstance(value, str):
			value = str(value)
			
		return ContentInstance(
			parent=self, 
			content=value, 
			contentInfo=contentInfo, 
			**kwargs
		)


	def latestContentInstance(self) -> Optional[ContentInstance]:
		"""	Return the latest (newest) <contentInstance> child-resource from this container, or None.

			Returns:
				The latest <contentInstance> resource that is a childresource of this 
					<container> resource or None if there are no <contentInstances>.
		"""
		return self._getContentInstance(f'{self._structuredResourceID()}/la')


	def oldestContentInstance(self) -> Optional[ContentInstance]:
		"""
		Return the oldest <contentInstance> child-resource from this container, or None.

			Returns:
				The oldest <contentInstance> resource that is a childresource of this 
					<container> resource or None if there are no <contentInstances>.
		"""
		return self._getContentInstance(f'{self._structuredResourceID()}/ol')


	def latestContent(self) -> Optional[str]:
		"""	Return the value of the latest (newest) <contentInstance> child-resource from this container, or None.
			
			This is a convenience function to access content values. It actually retrieves the latest <contentInstance>
			resource from a CSE.

			Returns:
				The content value of the latest <contentInstance> resource that is a childresource of this 
					<container> resource, or None if there are no <contentInstances>.	
		"""
		cin = self.latestContentInstance()
		if cin:
			return cin.content
		return None


	def oldestContent(self) -> Optional[str]:
		""" Return the value of the oldest <contentInstance> child-resource from this container, or None.
		
			This is a convenience function to access content values. It actually retrieves the oldest <contentInstance>
			resource from a CSE.

			Returns:
				The content value of the oldest <contentInstance> resource that is a childresource of this 
					<container> resource, or None if there are no <contentInstances>.
		"""
		cin = self.oldestContentInstance()
		if cin:
			return cin.content
		return None


	def _getContentInstance(self, path: str) -> Optional[ContentInstance]:
		""" Internal helper to retrieve a child resource by its path (URI). 

			Args:
				path: The path (URI) of the child resource to retrieve.

			Returns:
				The retrieved <contentInstance> resource, or None if it cannot be retrieved.
		"""
		if not self.session or not path: 
			return None
		response = MCA.get(self.session, path, originator=self.originator)
		if response and response.status_code == 200:
			contentInstance = ContentInstance(
				parent=self, 
				instantly=False
			)
			contentInstance._parseResponse(response)
			return contentInstance
		return None


	@override
	def _copy(self, resource: Container) -> None:	# type: ignore[override]
		""" Internal helper to copy attributes from another Container resource.

			Args:
				resource: The Container resource to copy attributes from.
		"""
		super()._copy(resource)
		self.maxNrOfInstances = resource.maxNrOfInstances
		self.maxByteSize = resource.maxByteSize
		self.maxInstanceAge = resource.maxInstanceAge
		self.currentNrOfInstances = resource.currentNrOfInstances
		self.currentByteSize = resource.currentByteSize
		self.oldest = resource.oldest
		self.latest = resource.latest