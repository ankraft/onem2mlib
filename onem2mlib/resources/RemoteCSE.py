#
#	RemoteCSE.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module implements the class for the &lt;RemoteCSE> resource.
#

import logging
import onem2mlib.marshalling as M
from .ResourceBase import *

logger = logging.getLogger(__name__)

class RemoteCSE(ResourceBase):
	"""
	This class implements the oneM2M &lt;remoteCSE> resource. 

	It is  a sub-resource of the &lt;CSEBase> resource, and it represents and grants access to a
	remote CSE.
	"""
	def __init__(self, parent=None, resourceName=None, resourceID=None, requestReachability=None, instantly=True):
	
		"""
		Initialize a RemoteCSE object.
		Usually, objects of this class are created only by the onem2m lib..

		Args:

		- *parent*: The parent resource object in which the &lt;remoteCSE> resource
			will be created. This must be a &lt;CSEBase>. This might throw a *ParameterError*
			exception if this is not the case.
		- *instantly*: The resource will be instantly retrieved from the CSE. This might throw
			a *CSEOperationError* exception in case of an error.
		- All other arguments initialize the status variables of the same name in the
			&lt;remoteCSE> instance or `onem2mlib.ResourceBase`.
		"""
		ResourceBase.__init__(self, parent, resourceName, resourceID, CON.Type_RemoteCSE, CON.Type_RemoteCSE_SN)
		self._marshallers = [M._remoteCSE_parseXML, None, M._remoteCSE_parseJSON, None]

		if parent is not None and parent.type != CON.Type_CSEBase and parent.type != CON.Type_RemoteCSE:
			logger.error('Parent must be <CSE> or <remoteCSE>: ' + INT.nameAndType(self))
			raise EXC.ParameterError('Parent must be <CSE> or <remoteCSE>: ' + INT.nameAndType(self))

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
				logger.critical('Cannot get remoteCSE.' + MCA.lastError)
				raise EXC.CSEOperationError('Cannot get remoteCSE.' + MCA.lastError)


	def __str__(self):
		result = 'RemoteCSE:\n'
		result += ResourceBase.__str__(self)
		result += INT.strResource('requestReachability', 'rr', self.requestReachability)
		result += INT.strResource('pointOfAccess', 'poa', self.pointOfAccess)
		result += INT.strResource('CSEBase', 'cb', self.cseBase)
		result += INT.strResource('cse-ID', 'csi', self.cseID)
		return result


	def cseFromLocalCSE(self, instantly=True):
		"""
		Return a `onem2mlib.CSEBase` resource instance that grants access to the remote CSE via the local
		(the CSE from which this &lt;RemoteCSE> resource originates). This means, that all requests to the
		remote CSE are routed through the local CSE.

		Args:

		- *instantly*: The CSE resource will be instantly retrieved from the CSE. This might throw
			a *CSEOperationError* exception in case of an error.
		"""
		return CSEBase(self.session, self.cseID, self.resourceName, instantly=instantly)


	def cseFromRemoteCSE(self, session=None, instantly=True):
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
		if self.pointOfAccess == None or len(self.pointOfAccess) == 0:
			logger.error('Missing PointOfAccess of remote CSE.')
			raise EXC.CSEOperationError('Missing PointOfAccess of remote CSE.')

		if session is None:
			nSession = Session(self.pointOfAccess[0], self.session.originator, self.session.encoding)
		else:
			nSession = Session(self.pointOfAccess[0], session.originator, session.encoding)
		return CSEBase(nSession, self.cseID, instantly=instantly)


	def _copy(self, resource):
		ResourceBase._copy(self, resource)
		self.cseBase = resource.cseBase
		self.cseID = resource.cseID
		self.pointOfAccess = resource.pointOfAccess
		self.requestReachability = resource.requestReachability

