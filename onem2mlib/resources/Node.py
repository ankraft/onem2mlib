#
#	Node.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module implements the class for the &lt;Node> resource.
#

import logging
import onem2mlib.marshalling as M
import onem2mlib.constants as CON
import onem2mlib.internal as INT
from .ResourceBase import ResourceBase

logger = logging.getLogger(__name__)
# TODO: support mgmtObjects

class Node(ResourceBase):
	"""
	This class implements the oneM2M &lt;node> resource. 

	It is used represent nodes, or devices.
	"""

	def __init__(self, parent=None, resourceName=None, resourceID=None, nodeID=None, mgmtClientAddress=None, labels = [], instantly=True):
		"""
		Initialize the &lt;node> resource. 

		Args:

		- *parent*: The parent resource object in which the &lt;contentInstance> resource
			will be created.
		- *instantly*: The resource will be instantly retrieved from or created on the CSE. This might throw
			a `onem2mlib.exceptions.CSEOperationError` exception in case of an error.
		- All other arguments initialize the status variables of the same name in
			&lt;subscription> instance or `onem2mlib.ResourceBase`.
		"""
	
		ResourceBase.__init__(self, parent, resourceName, resourceID, CON.Type_Node, CON.Type_Node_SN, labels=labels)
		self._marshallers = [M._Node_parseXML, M._Node_createXML,
							 M._Node_parseJSON, M._Node_createJSON]

		if nodeID == None or len(nodeID) == 0:
			raise EXC.ParameterError('nodeID is mandatory.')
		self.nodeID = nodeID
		"""The M2M-Node-ID of the node which is represented by this &lt;node> resource."""

		self.hostedCSELink = None
		"""
		This attribute allows to find the &lt;CSEBase> or &lt;remoteCSE> resource representing
		the CSE that is residing on the node that is represented by this &lt;node> resource. R/O.
		"""

		self.hostedAELinks = None
		"""
		This attribute allows to find the AEs hosted by the node that is represented by this
		&lt;node> resource. The attribute shall contain a list of resource identifiers of
		&lt;AE> resources representing the ADN-AEs residing on the node that is represented
		by the current &lt;node> resource. R/O.
		"""

		self.hostedServiceLinks = None
		"""
		This attribute allows to find &lt;flexContainer> resources that have been created by an
		IPE to represent services hosted on a NoDN, the NoDN being represented by this &lt;node>
		resource.
		If the NoDN hosts a set of services represented by &lt;flexContainer>s, then the attribute
		shall contain the list of resource identifiers of these &lt;flexContainer> resources. R/O.
		"""

		self.mgmtClientAddress = mgmtClientAddress
		"""
		Represents the physical address of management client of the node which is represented 
		by this &lt;node> resource.
		"""

		self.roamingStatus = None
		"""
		Indicates if the M2M Node is currently roaming from the perspective of the underlying
		network. R/O.
		"""

		self.networkID = None
		"""
		Configured with the identity of the underlying network which the M2M Node is currently
		attached to. R/O.
		"""
		
		if instantly:
			if not self.get():
				logger.error('Cannot get or create Node. '  + MCA.lastError)
				raise EXC.CSEOperationError('Cannot get or create Node. '  + MCA.lastError)


	def __str__(self):
		result = 'Node:\n'
		result += ResourceBase.__str__(self)
		result += INT.strResource('nodeID', 'ni', self.nodeID)
		if self.hostedCSELink:
			result += INT.strResource('hostedCSELink', 'hcl', self.hostedCSELink)
		if self.hostedAELinks != -1:
			result += INT.strResource('hostedAELinks', 'hael', self.hostedAELinks)
		if self.hostedServiceLinks:
			result += INT.strResource('hostedServiceLinks', 'hsl', self.hostedServiceLinks)
		if self.mgmtClientAddress:
			result += INT.strResource('mgmtClientAddress', 'mgca', self.mgmtClientAddress)
		if self.roamingStatus:
			result += INT.strResource('roamingStatus', 'rms', self.roamingStatus)
		if self.networkID:
			result += INT.strResource('networkID', 'nid', self.networkID)
		return result


	def _copy(self, resource):
		ResourceBase._copy(self, resource)
		self.nodeID = resource.nodeID
		self.hostedCSELink = resource.hostedCSELink
		self.hostedAELinks = resource.hostedAELinks
		self.hostedServiceLinks = resource.hostedServiceLinks
		self.mgmtClientAddress = resource.mgmtClientAddress
		self.roamingStatus = resource.roamingStatus
		self.networkID = resource.networkID

