#
#	AccessControlPolicy.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module implements the class for the &lt;AccessControlPolicy> resource.
#

import logging
import onem2mlib.marshalling as M
from .ResourceBase import *

logger = logging.getLogger(__name__)


class AccessControlPolicy(ResourceBase):
	"""
	This class implements the oneM2M &lt;accessControlPolicy> resource. 

	It is always a sub-resource of a &lt;CSEBase> or a &lt;remoteCSE> resource, and it contains access right
	privileges to resources.

	**Note**: Delete associated resources first before deleting the	&lt;accessControlPolicy> resource.
	"""

	def __init__(self, parent=None, resourceName=None, resourceID=None, privileges = [], selfPrivileges=[], instantly=True):
		"""
		Initialize the &lt;accessControlPolicy> resource. 

		Args:

		- *parent*: The parent resource object in which the &lt;accessControlPolicy> resource
			will be created. This must be a &lt;CSEBase> or &lt;remoteCSE> resource. This might throw a
			*ParameterError* exception if this is not the case.
		- *instantly*: The resource will be instantly retrieved from or created on the CSE. This might throw
			a *CSEOperationError* exception in case of an error.
		- All other arguments initialize the status variables of the same name in the
			&lt;accessControlPolicy> instance or `onem2mlib.ResourceBase`.
		"""
		ResourceBase.__init__(self, parent, resourceName, resourceID, CON.Type_ACP, CON.Type_ACP_SN)
		self._marshallers = [M._accessControlPolicy_parseXML, M._accessControlPolicy_createXML, 
							 M._accessControlPolicy_parseJSON, M._accessControlPolicy_createJSON]

		if parent is not None and parent.type != CON.Type_CSEBase and parent.type != CON.Type_RemoteCSE:
			logger.error('Parent must be <CSE> or <remoteCSE>.')
			raise EXC.ParameterError('Parent must be <CSE> or <remoteCSE>.')

		self.privileges = privileges
		""" A list of *AccessControlRules* that applies to resources referencing this 
		&lt;accessControlPolicy> resource using the accessControlPolicyID attribute. """
		
		self.selfPrivileges = selfPrivileges
		""" A list of *AccessControlRules* that apply to the &lt;accessControlPolicy> resource itself. """

		if instantly:
			if not self.get():
				logger.critical('Cannot get or create ACP. ' + MCA.lastError)
				raise EXC.CSEOperationError('Cannot get or create ACP. ' + MCA.lastError)


	def __str__(self):
		result = 'ACP:\n'
		result += ResourceBase.__str__(self)
		result += '\tPrivileges:\n'
		for p in self.privileges:
			result += str(p)
		result += '\tSelfPrivileges:\n'
		for p in self.selfPrivileges:
			result += str(p)
		return result


	def _copy(self, resource):
		ResourceBase._copy(self, resource)
		self.privileges = resource.privileges
		self.selfPrivileges = resource.selfPrivileges


class AccessControlRule():
	"""
	This class provides the structure for access control rules that shall be used to define
	privileges in &lt;accessControlPolicy> resources. It contains:

	- *accessControlOriginators* : The accessControlOriginators is a mandatory parameter in an
		AccessControlRule. It represents the list of Originators that shall be allowed to use
		an access control rule. The list of Originators is described as a list of parameters, where the
		types of the parameter can vary within the list.
		See also table Table 9.6.2.1-1 of oneM2M's TS-0001.
	- *accessControlOperations* : The accessControlOperations is a mandatory parameter in an
		AccessControlRule structure that represents the set of operations that are authorized
		using this access control rule.
	"""

	def __init__(self, accessControlOriginators=[], accessControlOperations=0):
		"""
		Initialize the AccessControlRule. 

		Args:

		- *accessControlOriginators*: A list of originators.
		- *accessControlOperations*: The combination of operation privileges.
		"""

		self.accessControlOriginators = accessControlOriginators
		""" List of string. This attribute specifies the list of originators. R/W. """
		
		self.accessControlOperations = accessControlOperations
		""" Integer. This attribute is an OR'ed combination of the operation privileges for this AccessControlRule. R/W. """

	def __str__(self):
		result =  '\t  accessControlRule(acr):\n'
		result += INT.strResource('    ' + 'accessControlOriginators', 'acor', self.accessControlOriginators)
		result += INT.strResource('    ' + 'accessControlOperations', 'acop', self.accessControlOperations)
		return result
