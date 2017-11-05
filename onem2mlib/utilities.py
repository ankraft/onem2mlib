#
#	util.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module defines various utilitiy classes and functions
#

"""
This sub-module defines the various utility classes and function for the onem2mlib module.

"""
import onem2mlib.exceptions as EXC
import onem2mlib.constants as CON

#
#	Filter
#

def newLabelFilterCriteria(label):
	"""
	Create a new label filter criteria.

	Args:

	- *label*: String. The label to filter for. The format of a label is "key/value".

	This function may throw a *ParameterError* exception when called with an empty or wrong label format.
	"""
	if label is None:
		raise EXC.ParameterError('label must not be empty.')
	if label.count('/') < 1:
		raise EXC.ParameterError('Wrong format: label format is "key/value".')
	return ('lbl', label)


def newTypeFilterCriteria(type):
	"""
	Create a new resource type filter criteria.

	Args:

	- *label*: Integer. The resource type to filter for. It must be one of the valid oneM2M resource types.

	This function may throw a *ParameterError* exception when called with a wrong resource type.
	"""
	if type not in [CON.Type_Mixed, CON.Type_ACP, CON.Type_AE, CON.Type_Container, \
					CON.Type_ContentInstance, CON.Type_CSEBase, CON.Type_Group, CON.Type_RemoteCSE, \
					CON.Type_Subscription, \
					CON.Type_FlexContainer]:
		raise EXC.ParameterError('Wrong or unsupported type: ' + str(type))
	return ('ty', str(type))

#
##
###	TBD: More filter criteria when supported by om2m
##
#


