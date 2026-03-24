#
#	AE.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module implements the class for the &lt;AE> resource.
#

import logging
import onem2mlib.marshalling as M
from .ResourceBase import *

logger = logging.getLogger(__name__)


class AE(ResourceBase):
	"""
	This class implements the oneM2M &lt;AE> resource. 

	It is usually a sub-resource of the &lt;CSEBase> resource, and it represents an 
	application and the sub-structure of resources beneath it.
	"""

	def __init__(self, parent=None, resourceName=None, appID=None, AEID=None, resourceID=None, requestReachability=True, nodeLink=None, labels=[], originator=None, instantly=True):
		"""
		Initialize the &lt;AE> resource. 

		Args:

		- *parent*: The parent resource object in which the &lt;AE> resource
			will be created.
		- *instantly*: The resource will be instantly retrieved from or created on the CSE. This might throw
			a `onem2mlib.exceptions.CSEOperationError` exception in case of an error.
		- All other arguments initialize the status variables of the same name in the
			&lt;AE> instance or `onem2mlib.ResourceBase`.
		"""
		ResourceBase.__init__(self, parent, resourceName, resourceID, CON.Type_AE, CON.Type_AE_SN, labels=labels, originator=originator,)
		self._marshallers = [M._AE_parseXML, M._AE_createXML,
							 M._AE_parseJSON, M._AE_createJSON]

		self.appID = appID
		""" String. The identifier of the Application. Assigned by the application or the CSE. """
		if not self.appID:
			if self.resourceName is not None:
				self.appID = self.resourceName
			else:
				self.appID = None

		if self.appID:
			self.appID = 'N' + self.appID

		# For non-registered entities, the appID has to start with an 'N'


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

		# TODO more attributes

		if instantly:
			if not self.get():
				EXC.CSEOperationError('Cannot get or create AE. '  + MCA.lastError)


	def __str__(self):
		result = 'AE:\n'
		result += ResourceBase.__str__(self)
		result += INT.strResource('appID', 'api', self.appID)
		result += INT.strResource('AEID', 'aei', self.AEID)
		result += INT.strResource('requestReachability', 'rr', self.requestReachability)
		result += INT.strResource('pointOfAccess', 'poa', self.pointOfAccess)
		result += INT.strResource('nodeLink', 'nl', self.nodeLink)
		result += INT.strResource('supportedReleaseVersions', 'srv', self.supportedReleaseVersions)
		return result


	def containers(self):
		"""
		Return a list of all &lt;container> resources of this &lt;AE>, or an empty list.
		"""
		return INT._findSubResource(self, CON.Type_Container)


	def addContainer(self, resourceName=None, maxNrOfInstances=None, maxByteSize=None, maxInstanceAge=None, labels=[], originator=None):
		"""
		Add a new container. This is a convenience function that actually creates a new
		&lt;container> resource in the &lt;AE>. It returns the new
		*Container* object, or None.
		"""
		return Container(self, resourceName, maxNrOfInstances=maxNrOfInstances, maxByteSize=maxByteSize, maxInstanceAge=maxInstanceAge, labels=labels, originator=originator)


	# def flexContainers(self):
	# 	"""
	# 	Return a list of all &lt;flexContainer> resources of this &lt;AE>, or an empty list.
	# 	"""
	# 	return _findSubResource(self, CON.Type_FlexContainer)


	# def findFlexContainer(self, resourceName):
	# 	"""
	# 	Find a &lt;flexContainer> resource by its *resourceName*, or None.
	# 	"""
	# 	return _getResourceFromCSEByResourceName(CON.Type_FlexContainer, resourceName, self)


	def groups(self):
		"""
		Return a list of all &lt;group> resources of this &lt;AE>, or an empty list.
		"""
		return INT._findSubResource(self, CON.Type_Group)


	def addGroup(self, resourceName=None, resources=[], maxNrOfMembers=CON.Grp_def_maxNrOfMembers, consistencyStrategy=CON.Grp_ABANDON_MEMBER, groupName=None, labels = [], originator=None,  instantly=True):
		"""
		Add a new group. This is a convenience function that actually creates a new
		&lt;group> resource in the &lt;AE>. It returns the new
		*Group* object, or None.
		"""
		return Group(self, resourceName=resourceName, resources=resources, maxNrOfMembers=maxNrOfMembers, consistencyStrategy=consistencyStrategy, groupName=groupName, labels=labels, originator=originator)


	def _copy(self, resource):
		ResourceBase._copy(self, resource)
		self.appID = resource.appID
		self.AEID = resource.AEID
		self.requestReachability = resource.requestReachability
		self.pointOfAccess = resource.pointOfAccess

