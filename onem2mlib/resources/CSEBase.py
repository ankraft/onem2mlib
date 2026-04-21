#
#	CSEBase.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module implements the class for the <CSEBase> resource.
#

import logging
import onem2mlib.marshalling as M
import onem2mlib.constants as CON
import onem2mlib.internal as INT
import onem2mlib.mcarequests as MCA
import onem2mlib.exceptions as EXC
from .ResourceBase import ResourceBase

logger = logging.getLogger(__name__)

class CSEBase(ResourceBase):
	"""
	CSEBase holds the attributes of a CSE and gives access to resources under it.

	When created and initialized correctly, it is automatically retrieved from the
	CSE immediatly.
	"""

	def __init__(self, 
				 session=None, 
				 cseID: str | None = None, 
				 instantly: bool = True, 
				 **kwargs):
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
		""" Integer. The type of the CSE. See also the `Constants.CSE_Type_*` constants.
			Assigned by the CSE. R/O."""
		
		self.supportedResourceTypes = []
		""" List of String. A list of supported resource types of this CSE.	Assigned by the CSE. R/O. """
		
		self.pointOfAccess = []
		""" List of String. A list of physical addresses to be used by remote CSEs to connect to this CSE.
			Assigned by the CSE. R/O. """

		if instantly:
			if not self.retrieveFromCSE():
				logger.critical(f'Cannot get CSEBase. {MCA.lastError}')
				raise EXC.CSEOperationError(f'Cannot get CSEBase. {MCA.lastError}')


	def __str__(self):
		result = 'CSEBase:\n'
		result += super().__str__()
		result += INT.strResource('cseType', 'cst', self.cseType)
		result += INT.strResource('supportedResourceTypes', 'srt', self.supportedResourceTypes)
		result += INT.strResource('pointOfAccess', 'poa', self.pointOfAccess)
		return result


	# --- Convenience Methods for Child Resources ---

	def addAE(self, 
			  resourceName: str | None = None, 
			  appID: str | None = None, 
			  AEID: str | None = None, 
			  requestReachability: bool = True, 
			  instantly: bool = True, 
			  **kwargs):
		"""
		Convenience function to create a new <AE> in the <CSEBase>.
		"""
		from .AE import AE
		return AE(
			parent=self,
			resourceName=resourceName,
			appID=appID,
			AEID=AEID,
			requestReachability=requestReachability,
			instantly=instantly,
			**kwargs
		)


	def addContainer(self, 
					 resourceName: str | None = None, 
					 maxNrOfInstances: int | None = None, 
					 maxByteSize: int | None = None, 
					 maxInstanceAge: int | None = None, 
					 instantly: bool = True, 
					 **kwargs):
		"""
		Convenience function to create a new <container> in the <CSEBase>.
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


	def addGroup(self, 
				 resourceName: str | None = None, 
				 resources: list | None = None, 
				 maxNrOfMembers: int = CON.Grp_def_maxNrOfMembers, 
				 consistencyStrategy: int = CON.Grp_ABANDON_MEMBER, 
				 groupName: str | None = None, 
				 instantly: bool = True, 
				 **kwargs):
		"""
		Convenience function to create a new <group> in the <CSEBase>.
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

	def addFlexContainer(self, 
						 resourceSpecialization: str | None = None, 
						 contentDefinition: str | None = None, 
						 attributes: dict | None = None, 
						 instantly: bool = True, 
						 **kwargs):
		"""
		Convenience function to create a new <flexContainer> in the <CSEBase>.
		"""
		from .FlexContainer import FlexContainer
		return FlexContainer(
			parent=self,
			resourceSpecialization=resourceSpecialization,
			contentDefinition=contentDefinition,
			attributes=attributes,
			instantly=instantly,
			**kwargs
		)


	# --- Resource Discovery Helpers ---

	def accessControlPolicies(self, filter=None):
		"""
		Return a list of &lt;accessControlPolicy> resources from this CSE, or an empty list.
		"""
		return INT._findSubResource(self, CON.Type_ACP, filter=filter)

	def aes(self, filter=None):
		"""
		Return a list of &lt;AE> resources from this CSE, or an empty list.
		"""
		return INT._findSubResource(self, CON.Type_AE, filter=filter)

	def containers(self, filter=None):
		"""
		Return a list of all &lt;container> resources of this &lt;CSEBase>, or an empty list.
		"""
		return INT._findSubResource(self, CON.Type_Container, filter=filter)

	def groups(self, filter=None):
		"""
		Return a list of &lt;group> resources from this CSE, or an empty list.
		"""
		return INT._findSubResource(self, CON.Type_Group, filter=filter)

	def remoteCSEs(self, filter=None):
		return INT._findSubResource(self, CON.Type_RemoteCSE, filter=filter)


	def _copy(self, resource: 'CSEBase'):
		super()._copy(resource)
		self.cseType = resource.cseType
		self.supportedResourceTypes = resource.supportedResourceTypes
		self.pointOfAccess = resource.pointOfAccess