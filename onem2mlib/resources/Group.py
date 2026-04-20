#
#	Group.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module implements the class for the <Group> resource.
#

import logging
import onem2mlib.marshalling as M
import onem2mlib.constants as CON
import onem2mlib.internal as INT
import onem2mlib.mcarequests as MCA
import onem2mlib.exceptions as EXC
from .ResourceBase import ResourceBase

logger = logging.getLogger(__name__)

class Group(ResourceBase):
	"""
	This class implements the oneM2M &lt;group> resource. 

	The &lt;group> resource represents a group of resources of the same or mixed types. 
	The &lt;group> resource can be used to do bulk manipulations on the resources represented by the
	`onem2mlib.Group.memberIDs` attribute. The &lt;group> resource contains an attribute that represents the members of 
	the group and the &lt;fanOutPoint> virtual resource that enables generic operations to be applied 
	to all the resources represented by those members.
	"""

	def __init__(self, resources: list | None = None, maxNrOfMembers: int = CON.Grp_def_maxNrOfMembers, 
				consistencyStrategy: int = CON.Grp_ABANDON_MEMBER, groupName: str | None = None, 
				instantly: bool = True, **kwargs):
		"""
		Initialize the &lt;group> resource. 

		Args:
			resources: A list of resource instances to be members of the group.
			maxNrOfMembers: Maximum number of members allowed.
			consistencyStrategy: How to handle type inconsistencies.
			groupName: Human readable name of the group.
			instantly: If True, the resource is immediately synced with the CSE.
			**kwargs: Inherited attributes (parent, resourceName, labels, originator, etc.)
		"""
		super().__init__(type=CON.Type_Group, typeShortName=CON.Type_Group_SN, **kwargs)

		self._marshallers = [M._Group_parseXML, M._Group_createXML,
							M._Group_parseJSON, M._Group_createJSON]

		self.maxNrOfMembers = maxNrOfMembers
		""" Integer. Maximum number of members in the &lt;group>. """

		self.resources = resources
		""" List of resource instances. The resources in this &lt;group>. """
		
		self.currentNrOfMembers = len(resources)
		""" Integer. Current number of members in a &lt;group>. It shall not be larger than 
		`onem2mlib.Group.maxNrOfMembers`. R/O. """
		
		self.memberTypeValidated = None
		""" Boolean, or None. Denotes if the resource types of all members resources 
		of the &lt;group> has been validated by the Hosting CSE. In the case that the `onem2mlib.Group.memberType` 
		attribute of the &lt;group> resource is not 'mixed', then this attribute shall be set. """

		self.consistencyStrategy = consistencyStrategy
		""" Integer. This attribute determines how to deal with the &lt;group> resource if the `onem2mlib.Group.memberType`
		validation fails. Its possible values (from the `onem2mlib.constants` sub-module) are

		- *Grp_ABANDON_MEMBER* : delete the inconsistent member
		- *Grp_ABANDON_GROUP* : delete the group
		- *Grp_SET_MIXED* : set the *memberType* to "mixed"

		The default is *Grp_ABANDON_MEMBER*. """
		
		self.groupName = groupName
		""" String. Human readable name of the &lt;group>. """

		self.fanOutPoint = None
		""" String. The resourceID of the virtial &lt;fanOutPoint> resource. Whenever a request is sent 
		to the &lt;fanOutPoint> resource, the request is fanned out to each of the members of the
		&lt;group> resource indicated by the `onem2mlib.Group.memberIDs` attribute of the &lt;group> resource. R/O. """

		self.memberType = self._determineMemberType()
		""" Integer. This is the resource type of the member resources of the group, if all member
		resources (including the member resources in any sub-groups) are of the same type.
		Otherwise, it is of type 'mixed'. W/O. """

		# assign the resource ids
		self.memberIDs = [ res.resourceID for res in self.resources ]
		""" List String, member resource IDs. Each memberID should refer to a member resource or a 
		(sub-) &lt;group> resource of the &lt;group>. """

		if instantly:
			if not self.get():
				logger.critical(f'Cannot get or create Group. {MCA.lastError}')
				raise EXC.CSEOperationError(f'Cannot get or create Group. {MCA.lastError}')


	def _determineMemberType(self) -> int:
		""" Internal helper to determine if the group is of a specific type or 'Mixed'. """
		if not self.resources:
			return CON.Type_Mixed
		
		first_type = self.resources[0].type
		for res in self.resources:
			if res.type != first_type:
				return CON.Type_Mixed
		return first_type


	def __str__(self):
		result = 'Group:\n'
		result += super().__str__()
		result += INT.strResource('maxNrOfMembers', 'mnm', self.maxNrOfMembers)
		result += INT.strResource('memberType', 'mt', self.memberType)
		result += INT.strResource('currentNrOfMembers', 'cnm', self.currentNrOfMembers)
		result += INT.strResource('memberIDs', 'mid', self.memberIDs)
		result += INT.strResource('memberTypeValidated', 'mtv', self.memberTypeValidated)
		result += INT.strResource('consistencyStrategy', 'csy', self.consistencyStrategy)
		result += INT.strResource('groupName', 'gn', self.groupName)
		result += INT.strResource('fanOutPoint', 'fopt', self.fanOutPoint)
		return result


	def getGroupResources(self):
		"""
		Return the resources that are managed by this &lt;group> resource. This method returns a list of
		the resources, or *None*.
		"""
		if not self._isValidFanOutPoint(): return None
		response = MCA.get(self.session, self.fanOutPoint, originator=self.originator)
		return self._parseFanOutPointResponse(response)


	def deleteGroupResources(self):
		"""
		Delete the resources that are managed by this &lt;group> resource. 
		It returns *True* or *False* respectively.

		Note, that the &lt;group> itself is not deleted or altered. It must be deleted separately, 
		if necessary.
		"""
		if not self._isValidFanOutPoint():
			return False
		response = MCA.delete(self.session, self.fanOutPoint, originator=self.originator)
		return response and response.status_code == 200


	def updateGroupResources(self, resource):
		"""
		Update the resources that are managed by this &lt;group> resource.

		Args:

		- *resource*: A resource object that acts as a template to update the group resources.

		It returns a list of the updated resources, or *None* in case of an error.
		Please note, that in the returned resource instances only the properties are set that have been
		updated either by the update operation or as a side effect by the CSE, such as the
		`onem2mlib.ResourceBase.lastModifiedTime`. The order of the instances in the result list is the same as the order of 
		the resource identifiers in `onem2mlib.Group.memberIDs`.
		"""
		if not self._isValidFanOutPoint(): return None
		
		# Use internal helper to generate body based on encoding
		body = resource._createContent(isUpdate=True)
		response = MCA.update(self.session, self.fanOutPoint, resource.type, body, originator=self.originator)
		return self._parseFanOutPointResponse(response)


	def createGroupResources(self, resource):
		"""
		Create/add a resource at all the resources managed by this &lt;group> resource.

		It returns a list of the created resources, or *None* in case of an error.
		"""
		if not self._isValidFanOutPoint(): return None
		body = resource._createContent(isUpdate=True)
		response = MCA.create(self.session, self.fanOutPoint, resource.type, body, originator=self.originator)
		return self._parseFanOutPointResponse(response)


	def _parseFanOutPointResponse(self, response):
		# Get the resources from the answer
		if response and response.status_code == 200:
			if self.session.encoding == CON.Encoding_XML:
				rsps = INT.getElements(INT.responseToXML(response), 'pc')	# deep-search the tree for all <pc> elements
				if not rsps or not len(rsps) > 0: return None
				resources = []
				for rsp in rsps: # each <pc>  contains a onem2m resource 

					# The following is a hack to get a stand-alone XML tree. Otherwise the XML parser always only
					# finds the first resource in the whole response tree.
					# Take the XML as a string and parse it again.
					xml = INT.stringToXML(INT.xmlToString(rsp[0]))
					(tag, ns) = INT.xmlQualifiedName(xml)
					# The resources get the group as a parent to pass on the Session.
					# Yes, this is halfway wrong, it will not result in a fully qualified path later.
					# But at least the resources can be used by the application
					resource = INT._newResourceFromTypeString(tag, self, namespace=ns)
					if resource:
						resource._parseXML(xml)
						resources.append(resource)
				return resources
			elif self.session.encoding == CON.Encoding_JSON:
				elements = INT.getALLSubElementsJSON(response.json(), 'm2m:pc')
				resources = []
				for elem in elements:
					keyWithoutPrefix = list(elem.keys())[0].replace('m2m:','')		# TODO check this for other domains, eg. hd
					resource = INT._newResourceFromTypeString(keyWithoutPrefix, self)
					if resource:
						resource._parseJSON(elem)
						resources.append(resource)
				return resources
			else:
				logger.error('Encoding not supported: ' + str(self.session.encoding))
				raise EXC.NotSupportedError('Encoding not supported: ' + str(self.session.encoding))
		return None


	def _isValidFanOutPoint(self):
		return  self.fanOutPoint and len(self.fanOutPoint) > 0 and self.session


	def _copy(self, resource: 'Group'):
		super()._copy(resource)
		self.maxNrOfMembers = resource.maxNrOfMembers
		self.memberType = resource.memberType
		self.currentNrOfMembers = resource.currentNrOfMembers
		self.memberIDs = resource.memberIDs
		self.memberTypeValidated = resource.memberTypeValidated
		self.consistencyStrategy = resource.consistencyStrategy
		self.groupName = resource.groupName
		self.fanOutPoint = resource.fanOutPoint
