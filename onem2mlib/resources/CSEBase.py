#
#	AE.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module implements the class for the &lt;CSEBase> resource.
#

import logging
import onem2mlib.marshalling as M
from .ResourceBase import *
from .AE import *

logger = logging.getLogger(__name__)


class CSEBase(ResourceBase):
	"""
	CSEBase holds the attributes of a CSE and gives access to resources under it.

	When created and initialized correctly, it is automatically retrieved from the
	CSE immediatly.
	"""

	def __init__(self, session=None, cseID=None, resourceName=None, originator = None, instantly=True):
		"""
		Initialize a CSEBase object.

		Args:

		- *session*: A `onem2mlib.Session` object that holds the information to connect to a CSE.
		- *cseid*: The CSE-ID of the CSE.

		Internally, the *cseID* is assigned to the `onem2mlib.ResourceBase.resourceID` attribute, and the *csename* is handled
		by the *resourceName*. 
		"""
		ResourceBase.__init__(self, None, resourceName, cseID, CON.Type_CSEBase, CON.Type_CSEBase_SN, originator=originator)

		self.session = session # Must assign session manually.
		self._marshallers = [M._CSEBase_parseXML, None, M._CSEBase_parseJSON, None]
		
		self.cseType = None
		""" Integer. The type of the CSE. See also the `Constants.CSE_Type_*` constants.
			Assigned by the CSE. R/O."""
		
		self.supportedResourceTypes = []
		""" List of String. A list of supported resource types of this CSE.	Assigned by the CSE. R/O. """
		
		self.pointOfAccess = []
		""" List of String. A list of physical addresses to be used by remote CSEs to connect to this CSE.
			Assigned by the CSE. R/O. """

		if instantly:
			if not self.retrieveFromCSE():
				logger.critical('Cannot get CSEBase. ' + MCA.lastError)
				raise EXC.CSEOperationError('Cannot get CSEBase. ' + MCA.lastError)


	def __str__(self):
		result = 'CSEBase:\n'
		result += ResourceBase.__str__(self)
		result += INT.strResource('cseType', 'cst', self.cseType)
		result += INT.strResource('supportedResourceTypes', 'srt', self.supportedResourceTypes)
		result += INT.strResource('pointOfAccess', 'poa', self.pointOfAccess)
		return result


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


	def addAE(self, resourceName=None, appID=None, AEID=None, resourceID=None, requestReachability=True, labels=[], originator=None):
		"""
		Add a new AE. This is a convenience function that actually creates a new
		&lt;AE> resource in the &lt;CSEBase>. It returns the new
		*AE* object, or None.
		"""
		return AE(self, resourceName, appID, AEID, resourceID, requestReachability, labels=labels, originator=originator)


	def containers(self, filter=None):
		"""
		Return a list of all &lt;container> resources of this &lt;CSEBase>, or an empty list.
		"""
		return INT._findSubResource(self, CON.Type_Container, filter=filter)


	def addContainer(self, resourceName=None, maxNrOfInstances=None, maxByteSize=None, maxInstanceAge=None, labels=[], originator=None):
		"""
		Add a new container. This is a convenience function that actually creates a new
		&lt;container> resource in the &lt;CSEBase>. It returns the new
		*Container* object, or None.
		"""
		return Container(self, resourceName, maxNrOfInstances=maxNrOfInstances, maxByteSize=maxByteSize, maxInstanceAge=maxInstanceAge, labels=labels, originator=originator)


	def groups(self, filter=None):
		"""
		Return a list of &lt;group> resources from this CSE, or an empty list.
		"""
		return INT._findSubResource(self, CON.Type_Group, filter=filter)


	def addGroup(self, resourceName=None, resources=[], maxNrOfMembers=CON.Grp_def_maxNrOfMembers, consistencyStrategy=CON.Grp_ABANDON_MEMBER, groupName=None, labels = [], originator=None, instantly=True):
		"""
		Add a new group. This is a convenience function that actually creates a new
		&lt;group> resource in the &lt;CSEBase>. It returns the new
		*Group* object, or None.
		"""
		return Group(self, resourceName=resourceName, resources=resources, maxNrOfMembers=maxNrOfMembers, consistencyStrategy=consistencyStrategy, groupName=groupName, labels=labels, originator=originator)


	def remoteCSEs(self, filter=None):
		"""
		Return a list of &lt;remoteCSE> resources from this CSE, or an empty list.
		"""
		return INT._findSubResource(self, CON.Type_RemoteCSE, filter=filter)


	def _copy(self, resource):
		ResourceBase._copy(self, resource)
		self.cseType = resource.cseType
		self.supportedResourceTypes = resource.supportedResourceTypes
		self.pointOfAccess = self.pointOfAccess

