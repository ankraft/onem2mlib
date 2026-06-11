#
#	RemoteCSE.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
""" This module implements the class for the <RemoteCSE> resource. """

from __future__ import annotations
from typing import Optional, Any, override

import logging
import onem2mlib.marshalling as M
import onem2mlib.constants as CON
import onem2mlib.internal as INT
import onem2mlib.mcarequests as MCA
import onem2mlib.exceptions as EXC
from .ResourceBase import ResourceBase

from .Session import Session
from .CSEBase import CSEBase

logger = logging.getLogger(__name__)
""" Logger for this module. """

class RemoteCSE(ResourceBase):
	"""
	This class implements the oneM2M <remoteCSE> resource. 

	It is  a child-resource of the <CSEBase> resource, and it represents and grants access to a
	remote CSE.
	"""

	def __init__(self, 
				 requestReachability: bool = False, 
				 cseID: Optional[str] = None, 
				 cseBase: Optional[str] = None, 
				 instantly: Optional[bool] = True, 
				 **kwargs: Any) -> None:
		"""	Initialize a RemoteCSE object.

			Args:
				requestReachability: Indicates the reachability of the RemoteCSE.
				cseID: The CSE identifier of the remote CSE (SP-relative).
				cseBase: The URI of the remote CSEBase resource.
				instantly: If True, the resource is immediately retrieved from the CSE.
				**kwargs: Inherited attributes (parent, resourceName, labels, originator, etc.)
		"""
		super().__init__(type=CON.Type_RemoteCSE, typeShortName=CON.Type_RemoteCSE_SN, **kwargs)

		self._marshallers = [M._remoteCSE_parseXML, None, M._remoteCSE_parseJSON, None]

		if self.parent is not None and self.parent.type not in [CON.Type_CSEBase, CON.Type_RemoteCSE]:
			msg = f'Parent of <remoteCSE> must be <CSEBase> or <remoteCSE>: {INT.nameAndType(self)}'
			logger.error(msg)
			raise EXC.ParameterError(msg)

		self.requestReachability: bool = requestReachability
		""" This indicates the reachability of the RemoteCSE. Assigned by the application or the CSE. """

		self.pointOfAccess: list[str] = []
		""" A list of physical addresses to be used by remote CSEs to connect to this CSE. Assigned by the CSE. R/O. """

		self.cseBase: Optional[str] = cseBase
		""" URI. The address of the CSEBase resource represented by this <remoteCSE> resource. """

		self.cseID: Optional[str] = cseID
		""" The CSE identifier of a remote CSE in SP-relative CSE-ID format. """


		if instantly:
			if not self.get():
				logger.critical(f'Cannot get remoteCSE. {MCA.lastError}')
				raise EXC.CSEOperationError(f'Cannot get remoteCSE. {MCA.lastError}')


	def __str__(self) -> str:
		return	'RemoteCSE: \n' +\
			 	super().__str__() +\
				INT.strResource('requestReachability', 'rr', self.requestReachability) +\
				INT.strResource('pointOfAccess', 'poa', self.pointOfAccess) +\
				INT.strResource('CSEBase', 'cb', self.cseBase) +\
				INT.strResource('cse-ID', 'csi', self.cseID)


	def cseFromLocalCSE(self, instantly: bool = True) -> CSEBase:
		"""	Return a `onem2mlib.CSEBase` resource instance that grants access to the remote CSE via the local
			(the CSE from which this <RemoteCSE> resource originates). This means, that all requests to the
			remote CSE are routed through the local CSE.

			Args:
				instantly: The CSE resource will be instantly retrieved from the CSE. 
				
			Raises:
				*CSEOperationError*: In case of an error.
		"""
  
		from .CSEBase import CSEBase
		return CSEBase(
			session=self.session, 
			cseID=self.cseID, 
			resourceName=self.resourceName, 
			instantly=instantly
		)


	def cseFromRemoteCSE(self, session: Optional[Session] = None) -> CSEBase:
		"""	Return a `onem2mlib.CSEBase` resource instance that grants direct access to the remote CSE.
			This means, that all requests to the remote CSE are directly targeting the remote CSE.

			Args:
				session: Optionally provide a `onem2mlib.Session` instance to use for the remote CSE.
					Otherwise the current Session instance is used.
			Raises:
				CSEOperationError: This might be raised if there is a problem with missing or wrong

		"""
		if not self.pointOfAccess:
			logger.error('Missing PointOfAccess of remote CSE.')
			raise EXC.CSEOperationError('Missing PointOfAccess of remote CSE.')

		# Create a new session targeting the remote point of access
		if session is None:
			target_session = Session(self.pointOfAccess[0], self.session.originator, self.session.encoding)
		else:
			target_session = Session(self.pointOfAccess[0], session.originator, session.encoding)
			
		return target_session.getCSEBase()


	@override
	def _copy(self, resource: RemoteCSE) -> None:	# type: ignore[override]
		super()._copy(resource)
		self.cseBase = resource.cseBase
		self.cseID = resource.cseID
		self.pointOfAccess = resource.pointOfAccess.copy() if resource.pointOfAccess else []
		self.requestReachability = resource.requestReachability