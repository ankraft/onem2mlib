#
#	utilities.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module defines various internal utility functions for the library.
#


from lxml import etree as ET
import onem2mlib.constants as CON
import onem2mlib.utilities as UT
import onem2mlib.mcarequests


# define the namespace
_ns = {'m2m' : 'http://www.onem2m.org/xml/protocols'}

###############################################################################
#
#	XML Utilities
#

def _searchExpression(elemName, relative):
	if relative:
		return './/'+elemName
	return '//'+elemName


# Find a tag value (string) from the tree or, if not found, return the default.
# If relative is set to True then the search is done relatively to the provided
# element.
def getElement(tree, elemName, default=None, relative=False):
	elem = tree.xpath(_searchExpression(elemName, relative), namespaces=_ns)
	if elem and len(elem)>0 and elem[0].text:
		result = elem[0].text
		if isinstance(default, list):
			result = result.split()
		elif isinstance(default, bool):	# bool must be checked before int!
			result = bool(result)
		elif isinstance(default, int):
			result = int(result)
		return result
	return default


# Find all subtree elements from the tree. Returns a list.
# If relative is set to True then the search is done relatively to the provided
# element.
def getElements(tree, elemName, relative=False):
	return tree.xpath(_searchExpression(elemName, relative), namespaces=_ns)


# Find the children elements of a specific XML element.
def getElementWithChildren(tree, elemName):
	result = getElements(tree, elemName)
	if result is not None:
		return result
	return None


# Find an attribute value from the tree/element or, if not found, return the default
def getAttribute(tree, elemName, attrName, default=None):
	elem = tree.xpath('//'+elemName, namespaces=_ns)
	if elem and len(elem)>0:
		if attrName in elem[0].attrib:
			return elem[0].attrib[attrName]
	return default


# Create an XML element, including an optional namespace. Return the element
def createElement(elemName, namespace=None):
	if namespace:
		return ET.Element('{%s}%s' % (_ns['m2m'], elemName), nsmap=_ns)
	else:
		return ET.Element(elemName)


# Create and add an element with the given name to the root. Return the new element.
def addElement(root, name):
	elem = createElement(name)
	root.append(elem)
	return elem


# Create and add an element with the given name to the root. Add content to it when
# the content is not None, or add the content nevertheless when mandatory is True.
def addToElement(root, name, content, mandatory=False):
	if isinstance(content, int) or (content and len(content) > 0) or mandatory:
		elem = createElement(name)
		if isinstance(content, list):
			elem.text = ' '.join(content)
		else:
		 	elem.text = str(content)
		root.append(elem)
		return elem
	return None


# Create a new ElementTree from a sub-tree
def elementAsNewTree(tree):
	return ET.ElementTree(tree).getroot()


# Create an XML structure out of a response
def responseToXML(response):
	if response and response.content and len(response.content) > 0:
		return stringToXML(response.content)
	return None


# Return the qualified name of an element
def xmlQualifiedName(element, stripNameSpace=False):
	qname = ET.QName(element)
	if stripNameSpace:
		return qname.localname
	return qname


# Return the XML structure as a string
def xmlToString(xml):
	return ET.tostring(xml)


# create a new XML structure from a string
def stringToXML(value):
	return ET.fromstring(value)


###############################################################################

#
#	JSON Utilities
#

# Find a tag value (string) from the JSON dictionaty or, if not found, return the default.
def getElementJSON(jsn, elemName, default=None):
	if elemName in jsn:
		elem = jsn[elemName]
		return elem
	return default


# Add an elememt to the jsn content
def addToElementJSON(jsn, name, content, mandatory=False):
	if isinstance(content, int) or (content and len(content) > 0) or mandatory:
		jsn[name] = content

# Find all the sub-structures of a specific name inside a JSON document
# TODO: Replace this with some xpath-like query package
def getALLSubElementsJSON(jsn, name):
	result = []
	for elemName in jsn:
		elem = jsn[elemName]
		if elemName == name:
			result.append(elem)
		elif isinstance(elem, dict):
			result.extend(getALLSubElementsJSON(elem, name))
		elif isinstance(elem, list):
			for e in elem:
				if isinstance(e, dict):
					result.extend(getALLSubElementsJSON(e, name))
	return result


###############################################################################
#
#	Utilities
#

# Get the type from a response, for JSON and XML
def getTypeFromResponse(response, encoding):
	if encoding == CON.Encoding_XML:
		root = responseToXML(response)
		return toInt(getElement(root, 'ty'))
	elif encoding == CON.Encoding_JSON:
		jsn = response.json()
		# This is a bit complicated. We need to get to the type, which is hidden under an
		# unknown object definition key. So, we asume that the JSON we get has the object
		# definition in the first element (as it should be).
		inner = list(jsn.values())[0]
		return getElementJSON(inner, 'ty')
	return -1

###############################################################################
#
#	Formating
#

_width = 45

def strResource(name, shortName, resource, minusIndent=0):
	if resource == None:
		return ''
	if isinstance(resource, list) and len(resource) == 0:
		return '' 
	if not isinstance(resource, str):
		resource = str(resource)
	if resource and len(resource) > 0:
		if shortName:
			return ('\t%s(%s):' % (name, shortName)).ljust(_width-minusIndent) + str(resource) + '\n'
		else:
			return ('\t%s:' % (name)).ljust(_width-minusIndent) + str(resource) + '\n'			
	return ''


# Convert to an integer, except when it is None, then return None.
def toInt(value):
	if value is None:
		return None
	return int(value)


###############################################################################
#
#	Search
#

# Find a sub-resource
def _findSubResource(resource, type):
	if not resource or not resource.session or not resource.resourceID: 
		return None
	result = []
	ris = onem2mlib.mcarequests.discoverInCSE(resource, filter=[UT.newTypeFilterCriteria(int(type))], structuredResult=True)
	if ris:
		#	The following is a hack to restrict the search result to the direct child
		#	level. Yes, the oneM2M "level" attribute could be used for that, but it
		#	doesn't seem to be supported that much (at least not in om2m).
		#	Anyway, the hack works like that: count the forward slashes, ie. the 
		#	number of path elements, and only add those from the response to the result
		#	which have count+1 path elements.

		sid = resource._structuredResourceID()
		count = sid.count('/') + 1

		for ri in ris:
			if ri.count('/') == count:	# <- hack s.o.
				subResource = _newResourceFromRID(type, ri, resource)
				subResource.retrieveFromCSE()
				result.append(subResource)

		# Still a hack: sort the list by the ct attribute
		result.sort(key=lambda x: x.creationTime)

	return result


# Find a resource from a list by its resource name
def _findResourceInList(resources, resourceName):
	if resources and len(resources)>0:
		for res in resources:
			if res.resourceName == resourceName:
				return res
	return None


# Create a new resource object with a given type, RI and parent
def _newResourceFromRID(type, ri, parent):
	res = _newResourceFromType(type, parent)
	if res:
		res.resourceID = ri
	return res


def _newResourceFromType(type, parent):
	if type == CON.Type_ContentInstance:	return onem2mlib.ContentInstance(parent, instantly=False)
	elif type == CON.Type_Container:		return onem2mlib.Container(parent, instantly=False)
	elif type == CON.Type_AE:				return onem2mlib.AE(parent, instantly=False)
	elif type == CON.Type_Group:			return onem2mlib.Group(parent, instantly=False)
	elif type == CON.Type_ACP:				return onem2mlib.AccessControlPolicy(parent, instantly=False)
	elif type == CON.Type_Subscription:		return onem2mlib.Subscription(parent, instantly=False)
	elif type == CON.Type_RemoteCSE:		return onem2mlib.RemoteCSE(parent, instantly=False)
	return None


def _newResourceFromTypeString(typeString, parent):
	if typeString == 'cin':		return _newResourceFromType(CON.Type_ContentInstance, parent)
	elif typeString == 'cnt':	return _newResourceFromType(CON.Type_Container, parent)
	elif typeString == 'ae':	return _newResourceFromType(CON.Type_AE, parent)
	elif typeString == 'grp':	return _newResourceFromType(CON.Type_Group, parent)
	elif typeString == 'acp':	return _newResourceFromType(CON.Type_ACP, parent)
	elif typeString == 'sub':	return _newResourceFromType(CON.Type_Subscription, parent)
	elif typeString == 'csr':	return _newResourceFromType(CON.Type_RemoteCSE, parent)
	return None


# Get a resource from the CSE by its resourceName
def _getResourceFromCSEByResourceName(type, rn, parent):
	res = None
	if type == CON.Type_ContentInstance:		res = onem2mlib.ContentInstance(parent, resourceName=rn, instantly=False)
	elif type == CON.Type_Container:			res = onem2mlib.Container(parent, resourceName=rn, instantly=False)
	elif type == CON.Type_AE:					res = onem2mlib.AE(parent, resourceName=rn, instantly=False)
	elif type == CON.Type_Group:				res = onem2mlib.Group(parent, resourceName=rn, instantly=False)
	elif type == CON.Type_ACP:					res = onem2mlib.AccessControlPolicy(parent, resourceName=rn, instantly=False)
	elif type == CON.Type_Subscription:			res = onem2mlib.Subscription(parent, resourceName=rn, instantly=False)
	elif type == CON.Type_RemoteCSE:			res = onem2mlib.RemoteCSE(parent, resourceName=rn, instantly=False)
	if res is not None and res.retrieveFromCSE():
		return res
	return None




