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
import onem2mlib.exceptions as EXC

from .ResourceBase import ResourceBase

logger = logging.getLogger(__name__)

class Container(ResourceBase):
	"""
	This class implements the oneM2M &lt;container> resource. 

	It is usually a sub-resource of the &lt;AE> or other resources.
	"""

	def __init__(self,
                 maxNrOfInstances: int | None = None,
                 maxByteSize: int | None = None, 
				 maxInstanceAge: int |None = None,
     			 instantly: bool = True,
        		 **kwargs):
		"""
		Initialize the &lt;container> resource. 

		Args:
			maxNrOfInstances: Maximum number of direct child <contentInstance> resources.
			maxByteSize: Maximum size in bytes of data allocated for the container.
			maxInstanceAge: Maximum age (seconds) of a child <contentInstance>.
			instantly: If True, the resource is immediately synced with the CSE.
			**kwargs: Inherited attributes (parent, resourceName, resourceID, labels, originator, etc.)
		"""
		super().__init__(type=CON.Type_Container, typeShortName=CON.Type_Container_SN, **kwargs)

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
				logger.critical(f'Cannot get or create Container. {MCA.lastError}')
				raise EXC.CSEOperationError(f'Cannot get or create Container. {MCA.lastError}')


	def __str__(self):
		result = 'Container:\n'
		result += super().__str__()
		result += INT.strResource('maxNrOfInstances', 'mni', self.maxNrOfInstances)
		result += INT.strResource('maxByteSize', 'mbs', self.maxByteSize)
		result += INT.strResource('maxInstanceAge', 'mia', self.maxInstanceAge)
		result += INT.strResource('currentNrOfInstances', 'cni', self.currentNrOfInstances)
		result += INT.strResource('currentByteSize', 'cbs', self.currentByteSize)
		result += INT.strResource('oldest', 'ol', self.oldest)
		result += INT.strResource('latest', 'la', self.latest)
		return result


	def containers(self, filter=None):
		"""
		Return all &lt;container> sub-resources from this container, or an empty list.
		"""
		return INT._findSubResource(self, CON.Type_Container, filter=filter)


	def addContainer(self,
                     resourceName: str | None = None,
                     maxNrOfInstances: int | None = None, 
                 	 maxByteSize: int | None = None,
                     maxInstanceAge: int | None = None,
                     **kwargs):
		"""
		Add a new <container> sub-resource. 

		Args:
			resourceName: The name of the new container.
			maxNrOfInstances: Maximum number of child contentInstances.
			maxByteSize: Maximum byte size of all child contentInstances.
			maxInstanceAge: Maximum age of child contentInstances (seconds).
			**kwargs: Optional base attributes (labels, originator, accessControlPolicies, etc.)
		
		Returns:
			The new Container object.
		"""

		return Container(
			parent=self,
			resourceName=resourceName,
			maxNrOfInstances=maxNrOfInstances,
			maxByteSize=maxByteSize,
			maxInstanceAge=maxInstanceAge,
			**kwargs
		)


	def contentInstances(self, filter=None):
		"""
		Return all &lt;contentInstance> sub-resources from this container, or an empty list.
		"""
		return INT._findSubResource(self, CON.Type_ContentInstance, filter=filter)


	def contents(self, filter=None):
		"""
		Return all content from all &lt;contentInstance>'s in list, or an empty list.
		"""
		return [cin.content for cin in self.contentInstances(filter=filter)]


	def addContent(self,
                   value,
                   contentInfo: str | None = None,
                   **kwargs):
		"""
		Add a new value to a container as a <contentInstance>.
		
		Args:
			value: The content to be added (converted to str if necessary).
			contentInfo: Optional metadata (e.g., 'text/plain:0').
			**kwargs: Optional attributes common to all resources (resourceName, labels, originator).
		"""
		from .ContentInstance import ContentInstance
		
		if value is not None and not isinstance(value, str):
			value = str(value)
			
		return ContentInstance(
			parent=self, 
			content=value, 
			contentInfo=contentInfo, 
			**kwargs
		)


	def latestContentInstance(self):
		"""
		Return the latest (newest) &lt;contentInstance> sub-resource from this container, or None.
		"""

		from .ContentInstance import ContentInstance
 
		latest = self._structuredResourceID() + "/la"
		return self._getContentInstance(latest)


	def oldestContentInstance(self):
		"""
		Return the oldest &lt;contentInstance> sub-resource from this container, or None.
		"""
		oldest = self._structuredResourceID() + "/ol"
		return self._getContentInstance(oldest)


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
		""" Internal helper to retrieve a child resource by its path (URI). """
		from .ContentInstance import ContentInstance
		
		if not self.session or not path: 
			return None
		
		response = MCA.get(self.session, path, originator=self.originator)
		if response and response.status_code == 200:
			contentInstance = ContentInstance(
				parent=self, 
				instantly=False
			)
			contentInstance._parseResponse(response)
			return contentInstance
		return None


	def _copy(self, resource: 'Container'):
		super()._copy(resource)
		self.maxNrOfInstances = resource.maxNrOfInstances
		self.maxByteSize = resource.maxByteSize
		self.maxInstanceAge = resource.maxInstanceAge
		self.currentNrOfInstances = resource.currentNrOfInstances
		self.currentByteSize = resource.currentByteSize
		self.oldest = resource.oldest
		self.latest = resource.latest