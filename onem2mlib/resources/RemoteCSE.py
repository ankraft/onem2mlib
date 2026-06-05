#
#	RemoteCSE.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module implements the class for the <RemoteCSE> resource.
#

import logging
import onem2mlib.marshalling as M
import onem2mlib.constants as CON
import onem2mlib.internal as INT
import onem2mlib.mcarequests as MCA
import onem2mlib.exceptions as EXC
from .ResourceBase import ResourceBase

logger = logging.getLogger(__name__)

class RemoteCSE(ResourceBase):
	"""
	This class implements the oneM2M &lt;remoteCSE> resource. 

	It is  a sub-resource of the &lt;CSEBase> resource, and it represents and grants access to a
	remote CSE.
	"""

	def __init__(self, 
				 requestReachability: bool | None = None, 
				 cseID: str | None = None, 
				 cseBase: str | None = None, 
				 instantly: bool = True, 
				 **kwargs):
		"""
		Initialize a RemoteCSE object.

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

		self.pointOfAccess = []
		""" List of String. A list of physical addresses to be used by remote CSEs to connect to this CSE.
			Assigned by the CSE. R/O. """

		self.cseBase = None
		""" URI. The address of the CSEBase resource represented by this &lt;remoteCSE> resource. """

		self.cseID = None
		""" String. The CSE identifier of a remote CSE in SP-relative CSE-ID format. """

		self.requestReachability = requestReachability
		""" Boolean. This indicates the reachability of the RemoteCSE. Assigned by the application or the CSE. """

		if instantly:
			if not self.get():
				logger.critical(f'Cannot get remoteCSE. {MCA.lastError}')
				raise EXC.CSEOperationError(f'Cannot get remoteCSE. {MCA.lastError}')


	def __str__(self):
		result = 'RemoteCSE:\n'
		result += super().__str__()
		result += INT.strResource('requestReachability', 'rr', self.requestReachability)
		result += INT.strResource('pointOfAccess', 'poa', self.pointOfAccess)
		result += INT.strResource('CSEBase', 'cb', self.cseBase)
		result += INT.strResource('cse-ID', 'csi', self.cseID)
		return result


	def cseFromLocalCSE(self, instantly: bool = True):
		"""
		Return a `onem2mlib.CSEBase` resource instance that grants access to the remote CSE via the local
		(the CSE from which this &lt;RemoteCSE> resource originates). This means, that all requests to the
		remote CSE are routed through the local CSE.

		Args:

		- *instantly*: The CSE resource will be instantly retrieved from the CSE. This might throw
			a *CSEOperationError* exception in case of an error.
		"""
  
		from .CSEBase import CSEBase
		return CSEBase(
			session=self.session, 
			cseID=self.cseID, 
			resourceName=self.resourceName, 
			instantly=instantly
		)


	def cseFromRemoteCSE(self, session=None, instantly: bool = True):
		"""
		Return a `onem2mlib.CSEBase` resource instance that grants direct access to the remote CSE.
		This means, that all requests to the remote CSE are directly targeting the remote CSE.

		This might throw a *CSEOperationError* exception if there is a problem with missing or wrong
		parameters for the remote CSE.

		Args:

		- *session*: Optionally provide a `onem2mlib.Session` instance to use for the remote CSE.
			Otherwise the current Session instance is used.
		- *instantly*: The CSE resource will be instantly retrieved from the CSE. This might throw
			a *CSEOperationError* exception in case of an error.
		"""
		from .CSEBase import CSEBase
		from .Session import Session 
		if not self.pointOfAccess:
			logger.error('Missing PointOfAccess of remote CSE.')
			raise EXC.CSEOperationError('Missing PointOfAccess of remote CSE.')

		# Create a new session targeting the remote point of access
		if session is None:
			target_session = Session(self.pointOfAccess[0], self.session.originator, self.session.encoding)
		else:
			target_session = Session(self.pointOfAccess[0], session.originator, session.encoding)
			
		return target_session.getCSEBase()


	def _copy(self, resource: 'RemoteCSE'):
		super()._copy(resource)
		self.cseBase = resource.cseBase
		self.cseID = resource.cseID
		self.pointOfAccess = resource.pointOfAccess.copy() if resource.pointOfAccess else []
		self.requestReachability = resource.requestReachability