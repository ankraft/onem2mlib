#
#	Container.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module implements the class for the &lt;Container> resource.
#

import logging
import onem2mlib.marshalling as M
import onem2mlib.constants as CON
import onem2mlib.internal as INT
import onem2mlib.mcarequests as MCA

from .ResourceBase import ResourceBase

logger = logging.getLogger(__name__)

class Container(ResourceBase):
	"""
	This class implements the oneM2M &lt;container> resource. 

	It is usually a sub-resource of the &lt;AE> or other resources.
	"""

	def __init__(self, parent=None, resourceName=None, resourceID=None, maxNrOfInstances=None, maxByteSize=None, maxInstanceAge=None, labels=[], instantly=True):
		"""
		Initialize the &lt;container> resource. 

		Args:

		- *parent*: The parent resource object in which the &lt;container> resource
			will be created.
		- *instantly*: The resource will be instantly retrieved from or created on the CSE. This might throw
			a `onem2mlib.exceptions.CSEOperationError` exception in case of an error.
		- All other arguments initialize the status variables of the same name in the
			&lt;container> instance or `onem2mlib.ResourceBase`.
		"""	

		ResourceBase.__init__(self, parent, resourceName, resourceID, CON.Type_Container, CON.Type_Container_SN, labels=labels)
		self._marshallers = [M._Container_parseXML, M._Container_createXML,
							 M._Container_parseJSON, M._Container_createJSON]

		self.maxNrOfInstances = maxNrOfInstances
		""" Integer. Maximum number of direct child &lt;contentInstance> resources in the 
		&lt;container> resource."""

		self.maxByteSize = maxByteSize
		""" Integer. Maximum size in bytes of data (i.e. content attribute of a &lt;contentInstance>
		resource) that is allocated for the &lt;container> resource for all direct child 
		&lt;contentInstance> resources in the &lt;container> resource."""

		self.maxInstanceAge = maxInstanceAge
		""" Integer.Maximum age of a direct child &lt;contentInstance> resource in the &lt;container>
		resource. The value is expressed in seconds. R/O."""

		self.currentNrOfInstances = None
		""" Integer. Current number of direct child &lt;contentInstance> resource in the &lt;container> 
		resource. It is limited by the `onem2mlib.Container.maxNrOfInstances` property. R/O."""
		
		self.currentByteSize = None
		""" Integer. Current size in bytes of data (i.e. content attribute of a &lt;contentInstance>
		resource) stored in all direct child <contentInstance> resources of a &lt;container> resource.
		This is the summation of contentSize attribute values of the &lt;contentInstance> resources. 
		It is limited by the `onem2mlib.Container.maxByteSize` property. R/O."""

		self.oldest = None
		""" String. The resourceID of the oldest &lt;contentInstance> resource in this &lt;container>
		resource. R/O. """

		self.latest = None
		""" String. The resourceID of the latest (newest) &lt;contentInstance> resource in this 
		&lt;container>. R/O. """

		if instantly:
			if not self.get():
				logger.critical('Cannot get or create Container. '  + MCA.lastError)
				raise EXC.CSEOperationError('Cannot get or create Container. '  + MCA.lastError)


	def __str__(self):
		result = 'Container:\n'
		result += ResourceBase.__str__(self)
		result += INT.strResource('maxNrOfInstances', 'mni', self.maxNrOfInstances)
		result += INT.strResource('maxByteSize', 'mbs', self.maxByteSize)
		result += INT.strResource('maxInstanceAge', 'mia', self.maxInstanceAge)
		result += INT.strResource('currentNrOfInstances', 'cni', self.currentNrOfInstances)
		result += INT.strResource('currentByteSize', 'cbs', self.currentByteSize)
		result += INT.strResource('oldest', 'ol', self.oldest)
		result += INT.strResource('latest', 'la', self.latest)
		return result


	def containers(self):
		"""
		Return all &lt;container> sub-resources from this container, or an empty list.
		"""
		return INT._findSubResource(self, CON.Type_Container)


	def addContainer(self, resourceName=None, maxNrOfInstances=None, maxByteSize=None, maxInstanceAge=None, labels=[]):
		"""
		Add a new container. This is a convenience function that actually creates a new
		&lt;container> resource in the &lt;container>. It returns the new
		*Container* object, or None.
		"""
		return Container(self, resourceName, maxNrOfInstances=maxNrOfInstances, maxByteSize=maxByteSize, maxInstanceAge=maxInstanceAge, labels=labels)


	def contentInstances(self):
		"""
		Return all &lt;contentInstance> sub-resources from this container, or an empty list.
		"""
		return INT._findSubResource(self, CON.Type_ContentInstance)


	def contents(self):
		"""
		Return all content from all &lt;contentInstance>'s in list, or an empty list.
		"""
		return [cin.content for cin in self.contentInstances()]


	def addContent(self, value, labels=[]):
		"""
		Add a new value to a container. The value is automatically converted to its string
		representation.
		This is a convenience function that actually creates a new&lt;contentInstance> resource
		for that value in the &lt;container>. returns the new *ContentInstance* object, or None.
		"""

		from .ContentInstance import ContentInstance
 
		if not isinstance(value, str):
			value = str(value)
		return ContentInstance(self, content=value, labels=labels)


	def latestContentInstance(self):
		"""
		Return the latest (newest) &lt;contentInstance> sub-resource from this container, or None.
		"""

		from .ContentInstance import ContentInstance
 
		return self._getContentInstance(self.latest)


	def oldestContentInstance(self):
		"""
		Return the oldest &lt;contentInstance> sub-resource from this container, or None.
		"""
		return self._getContentInstance(self.oldest)


	def latestContent(self):
		"""
		Return the value of the latest (newest) &lt;contentInstance> sub-resource from this container, or None.
		This is a convenience function to access content values. It actually retrieves the latest &lt;contentInsnace>
		resource from a CSE.
		"""
		cin = self.latestContentInstance()
		if cin:
			return cin.content
		return None


	def oldestContent(self):
		"""
		Return the value of the oldest &lt;contentInstance> sub-resource from this container, or None.
		This is a convenience function to access content values. It actually retrieves the oldest &lt;contentInsnace>
		resource from a CSE.
		"""
		cin = self.oldestContentInstance()
		if cin:
			return cin.content
		return None


	def _getContentInstance(self, path):

		from .ContentInstance import ContentInstance
 
		if not self.session or not path: return None
		response = MCA.get(self.session, path)
		if response and response.status_code == 200:
			contentInstance = ContentInstance(self, instantly=False)
			contentInstance._parseResponse(response)
			return contentInstance
		return None


	def _copy(self, resource):
		ResourceBase._copy(self, resource)
		self.maxNrOfInstances = resource.maxNrOfInstances
		self.maxByteSize = resource.maxByteSize
		self.maxInstanceAge = resource.maxInstanceAge
		self.currentNrOfInstances = resource.currentNrOfInstances
		self.currentByteSize = resource.currentByteSize
		self.oldest = resource.oldest
		self.latest = resource.latest
