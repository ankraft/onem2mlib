#
#	AccessControlPolicy.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#
""" This module implements the class for the <AccessControlPolicy> resource. """

from __future__ import annotations
from typing import Optional, Any, override
import logging
import onem2mlib
import onem2mlib.constants as CON
import onem2mlib.internal as INT
import onem2mlib.mcarequests as MCA
import onem2mlib.exceptions as EXC

from .ResourceBase import ResourceBase

logger = logging.getLogger(__name__)
""" Logger for this module. """

class AccessControlPolicy(ResourceBase):
	"""	This class implements the oneM2M <accessControlPolicy> resource. 

		It is always a child-resource of a <CSEBase>, <AE> or a <remoteCSE> resource, and it holds the access right
		privileges to resources.
	"""

	def __init__(self,
              	 privileges: Optional[list] = None,
                 selfPrivileges: Optional[list] = None, 
				 instantly: bool = True, 
				 **kwargs: Any) -> None:
		"""	Initialize the <accessControlPolicy> resource. 

			Args:
				privileges: List of AccessControlRules for external resources.
				selfPrivileges: List of AccessControlRules for this ACP itself.
				instantly: If True, sync immediately with the CSE.
				**kwargs: Inherited attributes (parent, resourceName, labels, originator, etc.)

			Raises:
				onem2mlib.exceptions.ParameterError: If the parent resource is not a <CSEBase>, <AE> or <remoteCSE>.
				onem2mlib.exceptions.CSEOperationError: If the resource cannot be retrieved or created on the CSE.
			
			Note:
				The parent resource must be a <CSEBase>, <AE> or <remoteCSE>.
		"""
		super().__init__(type=CON.Type_ACP, typeShortName=CON.Type_ACP_SN, **kwargs)
		
		if self.parent is not None and self.parent.type not in [CON.Type_CSEBase, CON.Type_AE, CON.Type_RemoteCSE]:
			logger.error('Parent of <ACP> must be <CSEBase>, <AE> or <remoteCSE>.')
			raise EXC.ParameterError('Parent must be <CSEBase>, <AE> or <remoteCSE>.')

		self.privileges = privileges if privileges is not None else []
		""" A list of *AccessControlRules* that applies to resources referencing this 
			<accessControlPolicy> resource using the accessControlPolicyID attribute. """

		self.selfPrivileges = selfPrivileges if selfPrivileges is not None else []
		""" A list of *AccessControlRules* that apply to the <accessControlPolicy> resource itself. """

		if instantly:
			if not self.get():
				logger.critical(f'Cannot get or create ACP. {MCA.lastError}')
				raise EXC.CSEOperationError(f'Cannot get or create ACP. {MCA.lastError}')

	def __str__(self) -> str:
		return	'AccessControlPolicy:\n' + \
				super().__str__() + \
				'\tprivileges:\n' + \
				''.join(str(p) for p in self.privileges) + \
				'\tselfPrivileges:\n' + \
				''.join(str(p) for p in self.selfPrivileges)


	@override
	def _copy(self, resource: AccessControlPolicy) -> None: # type: ignore[override]
		super()._copy(resource)
		self.privileges = resource.privileges.copy() if resource.privileges else []
		self.selfPrivileges = resource.selfPrivileges.copy() if resource.selfPrivileges else []


	def _fromCSE(self, jsn: dict) -> None:
		""" Update the attributes of this AE resource from a JSON representation.

				Args:
					jsn: The JSON representation of the resource as a dictionary.
		"""
		_jsn = super()._fromCSE(jsn)
		self.privileges = []
		pv = INT.getElementJSON(_jsn, 'pv')
		if pv:
			acrs = INT.getElementJSON(pv, 'acr')
			if acrs:
				for ajsn in acrs:
					acr = onem2mlib.AccessControlRule()
					acr._fromCSE(ajsn)
					self.privileges.append(acr)	
		self.selfPrivileges = []
		pvs = INT.getElementJSON(_jsn, 'pvs')
		if pvs:
			acrs = INT.getElementJSON(pvs, 'acr')
			if acrs:
				for ajsn in acrs:
					acr = onem2mlib.AccessControlRule()
					acr._fromCSE(ajsn)
					#acr._parseJSON(ajsn)
					self.selfPrivileges.append(acr)	


	def _toCSE(self, isUpdate: bool = False, isAcpiUpdate: bool = False) -> dict:
		""" Return a JSON representation of this ACP resource as a dictionary, to be sent to the CSE.

			Returns:
				A JSON representation of this ACP resource as a dictionary, to be sent to the CSE.
		"""
		jsn = super()._toCSE(isUpdate, isAcpiUpdate)
		if self.privileges:
			pv = {}
			#pv['acr'] = [ p._createJSON() for p in obj.privileges ]
			pv['acr'] = [ p._toCSE() for p in self.privileges ]
			jsn['pv'] = pv
		if self.selfPrivileges:
			pvs = {}
			#pvs['acr'] = [ p._createJSON() for p in obj.selfPrivileges ]
			pvs['acr'] = [ p._toCSE() for p in self.selfPrivileges ]
			jsn['pvs'] = pvs
		return INT.wrapJSON(self, jsn)

class AccessControlRule:
	"""	Structure for access control rules (acr) used in <ACP> resources."""

	def __init__(self,
                 accessControlOriginators: Optional[list[str]] = None,
                 accessControlOperations: int = 0) -> None:
		"""	Initialize an AccessControlRule.

			Args:
				accessControlOriginators: A list of originators.
				accessControlOperations: The combination of operation privileges.
		"""
		self.accessControlOriginators = accessControlOriginators if accessControlOriginators is not None else []
		""" List of string. This attribute specifies the list of originators. R/W. """

		self.accessControlOperations = accessControlOperations
		""" Integer. This attribute is an OR'ed combination of the operation privileges for this AccessControlRule. R/W. """
  

	def __str__(self) -> str:
		return	'\t  accessControlRule:\n' + \
				INT.strResource('    ' + 'accessControlOriginators', 'acor', self.accessControlOriginators) + \
				INT.strResource('    ' + 'accessControlOperations', 'acop', self.accessControlOperations)



	def _fromCSE(self, jsn: dict) -> None:
		""" Update the attributes of this AccessControlRule structure from a JSON representation.

				Args:
					jsn: The JSON representation of the structure as a dictionary.
		"""
		self.accessControlOriginators = INT.getElementJSON(jsn, 'acor', [])
		self.accessControlOperations = INT.getElementJSON(jsn, 'acop', 0)


	def _toCSE(self, isUpdate: bool = False, isAcpiUpdate: bool = False) -> dict:
		""" Return a JSON representation of this AccessControlRule structure as a dictionary, to be sent to the CSE.

			Args:
				isUpdate: If True, this JSON is for an update operation. 
				isAcpiUpdate: If True, this JSON is for an ACP update operation.

			Returns:
				A JSON representation of this AccessControlRule structure as a dictionary, to be sent to the CSE.
		"""
		jsn: dict = {}
		INT.addToElementJSON(jsn, 'acor', self.accessControlOriginators)
		INT.addToElementJSON(jsn, 'acop', self.accessControlOperations)
		return jsn

