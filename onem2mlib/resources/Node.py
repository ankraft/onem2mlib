#
#	Node.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
""" This module implements the class for the <Node> resource. """

from __future__ import annotations
from typing import Optional, Any, override

import logging
import onem2mlib.marshalling as M
import onem2mlib.constants as CON
import onem2mlib.internal as INT
import onem2mlib.mcarequests as MCA
import onem2mlib.exceptions as EXC
from .ResourceBase import ResourceBase

logger = logging.getLogger(__name__)
""" Logger for this module. """

class Node(ResourceBase):
	"""	This class implements the oneM2M <node> resource. 
	
		It is used to represent nodes, or devices.
	"""

	def __init__(self, 
				 nodeID: Optional[str] = None, 
				 mgmtClientAddress: Optional[str] = None, 
				 instantly: bool = True, 
				 **kwargs: Any) -> None:
		"""	Initialize the <node> resource. 

			Args:
				nodeID: The M2M-Node-ID (Mandatory).
				mgmtClientAddress: Physical address of the management client.
				instantly: If True, immediately sync with the CSE.
				**kwargs: Inherited attributes (parent, resourceName, labels, originator, etc.)

			Raises:
				ParameterError: If the parent resource is not a <CSEBase> or if nodeID is not provided.
		"""
		super().__init__(type=CON.Type_Node, typeShortName=CON.Type_Node_SN, **kwargs)

		self._marshallers = [M._Node_parseXML, M._Node_createXML,
							 M._Node_parseJSON, M._Node_createJSON]

		if self.parent is not None and self.parent.type not in [CON.Type_CSEBase]:
			logger.error('Parent of <Node> must be <CSEBase>.')
			raise EXC.ParameterError('Parent must be <CSEBase>.')

		if not nodeID:
			raise EXC.ParameterError('nodeID is mandatory for <node> resources.')
		
		self.nodeID: str = nodeID
		"""	The M2M-Node-ID of the node which is represented by this <node> resource."""

		self.hostedCSELink: Optional[str] = None
		"""	This attribute allows to find the <CSEBase> or <remoteCSE> resource representing
			the CSE that is residing on the node that is represented by this <node> resource. R/O.
		"""

		self.hostedAELinks: Optional[list[str]] = None
		"""	This attribute allows to find the AEs hosted by the node that is represented by this
			<node> resource. The attribute shall contain a list of resource identifiers of
			<AE> resources representing the ADN-AEs residing on the node that is represented
			by the current <node> resource. R/O.
		"""

		self.hostedServiceLinks: Optional[list[str]] = None
		"""	This attribute allows to find <flexContainer> resources that have been created by an
			IPE to represent services hosted on a NoDN, the NoDN being represented by this <node>
			resource.
			
			If the NoDN hosts a set of services represented by <flexContainer>s, then the attribute
			shall contain the list of resource identifiers of these <flexContainer> resources. R/O.
		"""

		self.mgmtClientAddress: Optional[str] = mgmtClientAddress
		""" Represents the physical address of management client of the node which is represented 
			by this <node> resource.
		"""

		self.roamingStatus: Optional[str] = None
		"""	Indicates if the M2M Node is currently roaming from the perspective of the underlying
			network. R/O.
		"""

		self.networkID: Optional[str] = None
		"""	Configured with the identity of the underlying network which the M2M Node is currently
			attached to. R/O.
		"""
		
		if instantly:
			if not self.get():
				logger.error(f'Cannot get or create Node. {MCA.lastError}')
				raise EXC.CSEOperationError(f'Cannot get or create Node. {MCA.lastError}')


	def __str__(self) -> str:
		return	'Node:\n' + \
				super().__str__() + \
				INT.strResource('nodeID', 'ni', self.nodeID) + \
				INT.strResource('hostedCSELink', 'hcl', self.hostedCSELink) + \
				INT.strResource('hostedAELinks', 'hael', self.hostedAELinks) + \
				INT.strResource('hostedServiceLinks', 'hsl', self.hostedServiceLinks) + \
				INT.strResource('mgmtClientAddress', 'mgca', self.mgmtClientAddress) + \
				INT.strResource('roamingStatus', 'rms', self.roamingStatus) + \
				INT.strResource('networkID', 'nid', self.networkID)


	@override
	def _copy(self, resource: Node) -> None:	# type: ignore[override]
		super()._copy(resource)
		self.nodeID = resource.nodeID
		self.hostedCSELink = resource.hostedCSELink
		self.hostedAELinks = resource.hostedAELinks
		self.hostedServiceLinks = resource.hostedServiceLinks
		self.mgmtClientAddress = resource.mgmtClientAddress
		self.roamingStatus = resource.roamingStatus
		self.networkID = resource.networkID