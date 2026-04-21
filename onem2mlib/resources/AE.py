#
#	AE.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module implements the class for the <AE> resource.
#

import logging
import onem2mlib.marshalling as M
import onem2mlib.constants as CON
import onem2mlib.exceptions as EXC
import onem2mlib.mcarequests as MCA
import onem2mlib.internal as INT
from .ResourceBase import ResourceBase


logger = logging.getLogger(__name__)

class AE(ResourceBase):
	"""
	This class implements the oneM2M <AE> resource. 

	It is usually a sub-resource of the <CSEBase> resource, and it represents an 
	application and the sub-structure of resources beneath it.
	"""

	def __init__(self,
              	 appID: str | None = None,
              	 AEID: str | None = None,
                 requestReachability: bool = True, 
				 nodeLink: str | None = None,
     			 instantly: bool = True,
         		 **kwargs):
		"""
		Initialize the &lt;AE> resource. 

		Args:
			appID: Identifier of the Application. Defaults to resourceName if not provided.
			AEID: Identifier of the Application Entity.
			requestReachability: Reachability status of the AE.
			nodeLink: Resource ID of the associated node resource.
			instantly: If True, the resource is immediately synced with the CSE.
			**kwargs: Inherited attributes (parent, resourceName, labels, originator, etc.)
		"""
		if not appID:
			appID = kwargs.get('resourceName')
		
		# For non-registered entities, the appID has to start with an 'N'
		if appID and not appID.startswith('N'):
			appID = 'N' + appID

		super().__init__(type=CON.Type_AE, typeShortName=CON.Type_AE_SN, **kwargs)

		# 3. Set Marshallers
		self._marshallers = [M._AE_parseXML, M._AE_createXML,
							 M._AE_parseJSON, M._AE_createJSON]

		# 4. Set AE-Specific Attributes
		self.appID = appID
		""" String. The identifier of the Application. Assigned by the application or the CSE. """
		self.AEID = AEID
		""" String. The identifier of the Application Entity. Assigned by the application or the CSE. """

		self.requestReachability = requestReachability
		""" Boolean. This indicates the reachability of the AE.	Assigned by the application or the CSE. """

		self.pointOfAccess = []
		""" List of String. The list of addresses for communicating with the registered AE. """

		self.nodeLink = nodeLink
		"""
		The resource identifier of a &lt;node> resource that stores the node specific information
		of the node on which the AE represented by this &lt;AE> resource resides.
		"""

		self.supportedReleaseVersions = ['3']
		""" List of String. The list of supported release versions. """

		if instantly:
			if not self.get():
				raise EXC.CSEOperationError(f'Cannot get or create AE. {MCA.lastError}')


	def __str__(self):
		result = 'AE:\n'
		result += super().__str__()
		result += INT.strResource('appID', 'api', self.appID)
		result += INT.strResource('AEID', 'aei', self.AEID)
		result += INT.strResource('requestReachability', 'rr', self.requestReachability)
		result += INT.strResource('pointOfAccess', 'poa', self.pointOfAccess)
		result += INT.strResource('nodeLink', 'nl', self.nodeLink)
		result += INT.strResource('supportedReleaseVersions', 'srv', self.supportedReleaseVersions)
		return result


	def containers(self, filter=None):
		"""
		Return a list of all &lt;container> resources of this &lt;AE>, or an empty list.
		"""
		return INT._findSubResource(self, CON.Type_Container, filter=filter)


	def addContainer(self, 
					 resourceName: str | None = None, 
					 maxNrOfInstances: int | None = None, 
					 maxByteSize: int | None = None, 
					 maxInstanceAge: int | None = None, 
					 instantly: bool = True, 
					 **kwargs):
		"""
		Add a new <container> sub-resource. 

		Args:
			resourceName: Name of the new container.
			maxNrOfInstances: Max number of contentInstances allowed.
			maxByteSize: Max total byte size allowed.
			maxInstanceAge: Max age of instances in seconds.
			instantly: If True, immediately sync with the CSE.
			**kwargs: Optional attributes like labels, originator, etc.
		"""
		from .Container import Container
		return Container(
			parent=self, 
			resourceName=resourceName, 
			maxNrOfInstances=maxNrOfInstances, 
			maxByteSize=maxByteSize, 
			maxInstanceAge=maxInstanceAge, 
			instantly=instantly, 
			**kwargs
		)


	def groups(self, filter=None):
		"""
		Return a list of all <group> resources of this <AE>, or an empty list.
		"""
		return INT._findSubResource(self, CON.Type_Group, filter=filter)


	def addGroup(self, 
				 resourceName: str | None = None, 
				 resources: list | None = None, 
				 maxNrOfMembers: int = CON.Grp_def_maxNrOfMembers, 
				 consistencyStrategy: int = CON.Grp_ABANDON_MEMBER, 
				 groupName: str | None = None, 
				 instantly: bool = True, 
				 **kwargs):
		"""
		Add a new <group> sub-resource.

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
		return Group(
			parent=self, 
			resourceName=resourceName, 
			resources=resources, 
			maxNrOfMembers=maxNrOfMembers, 
			consistencyStrategy=consistencyStrategy, 
			groupName=groupName, 
			instantly=instantly, 
			**kwargs
		)


	def _copy(self, resource: 'AE'):
		super()._copy(resource)
		self.appID = resource.appID
		self.AEID = resource.AEID
		self.requestReachability = resource.requestReachability
		self.pointOfAccess = resource.pointOfAccess
		self.nodeLink = resource.nodeLink