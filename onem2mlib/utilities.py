#
#	utilities.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module defines various utility functions.
#


from lxml import etree as ET


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
		return result
	return default


# Find all subtree elements from the tree. Returns a list
# If relative is set to True then the search is done relatively to the provided
# element.
def getElements(tree, elemName, relative=False):
	return tree.xpath(_searchExpression(elemName, relative), namespaces=_ns)


def getElementWithChildren(tree, elemName):
	result = getElements(tree, elemName)
	if result is not None and len(result) > 0:
		return result[0]
	return None


# Find an attribute value from the tree/element or, if not found, return the default
def getAttribute(tree, elemName, attrName, default=None):
	elem = tree.xpath('//'+elemName, namespaces=_ns)
	if elem and len(elem)>0:
		if attrName in elem[0].attrib:
			return elem[0].attrib[attrName]
	return default


def createElement(elemName, namespace=None):
	if namespace:
		return ET.Element('{%s}%s' % (_ns['m2m'], elemName), nsmap=_ns)
	else:
		return ET.Element(elemName)


def addElement(root, name):
	elem = createElement(name)
	root.append(elem)
	return elem


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
			return ('\t%s:' % (name)).ljust(_width) + str(resource-minusIndent) + '\n'			
	return ''


# Convert to an integer, except when it is None, then return None.
def toInt(value):
	if value is None:
		return None
	return int(value)



