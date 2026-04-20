#
#	AccessControlPolicy.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module implements the class for the <AccessControlPolicy> resource.
#

import logging
import onem2mlib.marshalling as M
import onem2mlib.constants as CON
import onem2mlib.internal as INT
import onem2mlib.mcarequests as MCA
import onem2mlib.exceptions as EXC
from .ResourceBase import ResourceBase

logger = logging.getLogger(__name__)

class AccessControlPolicy(ResourceBase):
	"""
	This class implements the oneM2M &lt;accessControlPolicy> resource. 

	It is always a sub-resource of a &lt;CSEBase> or a &lt;remoteCSE> resource, and it contains access right
	privileges to resources.

	**Note**: Delete associated resources first before deleting the	&lt;accessControlPolicy> resource.
	"""

	def __init__(self,
              	 privileges: list | None = None,
                 selfPrivileges: list | None = None, 
				 instantly: bool = True, **kwargs):
		"""
		Initialize the <accessControlPolicy> resource. 

		Args:
			privileges: List of AccessControlRules for external resources.
			selfPrivileges: List of AccessControlRules for this ACP itself.
			instantly: If True, sync immediately with the CSE.
			**kwargs: Inherited attributes (parent, resourceName, labels, originator, etc.)
		"""
		super().__init__(type=CON.Type_ACP, typeShortName=CON.Type_ACP_SN, **kwargs)
		
		self._marshallers = [M._accessControlPolicy_parseXML, M._accessControlPolicy_createXML, 
							 M._accessControlPolicy_parseJSON, M._accessControlPolicy_createJSON]

		if self.parent is not None and self.parent.type not in [CON.Type_CSEBase, CON.Type_RemoteCSE]:
			logger.error('Parent of <ACP> must be <CSEBase> or <remoteCSE>.')
			raise EXC.ParameterError('Parent must be <CSEBase> or <remoteCSE>.')

		self.privileges = privileges if privileges is not None else []
		""" A list of *AccessControlRules* that applies to resources referencing this 
		&lt;accessControlPolicy> resource using the accessControlPolicyID attribute. """
		self.selfPrivileges = selfPrivileges if selfPrivileges is not None else []
		""" A list of *AccessControlRules* that apply to the &lt;accessControlPolicy> resource itself. """

		if instantly:
			if not self.get():
				logger.critical(f'Cannot get or create ACP. {MCA.lastError}')
				raise EXC.CSEOperationError(f'Cannot get or create ACP. {MCA.lastError}')

	def __str__(self):
		result = 'ACP:\n'
		result += super().__str__()
		result += '\tPrivileges:\n'
		for p in self.privileges:
			result += str(p)
		result += '\tSelfPrivileges:\n'
		for p in self.selfPrivileges:
			result += str(p)
		return result

	def _copy(self, resource: 'AccessControlPolicy'):
		super()._copy(resource)
		self.privileges = resource.privileges.copy() if resource.privileges else []
		self.selfPrivileges = resource.selfPrivileges.copy() if resource.selfPrivileges else []


class AccessControlRule:
	"""
	Structure for access control rules (acr) used in <ACP> resources.
	"""

	def __init__(self,
                 accessControlOriginators: list[str] | None = None,
                 accessControlOperations: int = 0):
		"""
		Args:
			accessControlOriginators: A list of originators.
			accessControlOperations: The combination of operation privileges.
		"""
		self.accessControlOriginators = accessControlOriginators if accessControlOriginators is not None else []
		""" List of string. This attribute specifies the list of originators. R/W. """

		self.accessControlOperations = accessControlOperations
		""" Integer. This attribute is an OR'ed combination of the operation privileges for this AccessControlRule. R/W. """
  

	def __str__(self):
		result =  '\t  accessControlRule(acr):\n'
		result += INT.strResource('    ' + 'accessControlOriginators', 'acor', self.accessControlOriginators)
		result += INT.strResource('    ' + 'accessControlOperations', 'acop', self.accessControlOperations)
		return result