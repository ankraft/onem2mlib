#
#	constants.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module defines a constants used in various modules.
#

"""
This sub-module defines various constants used in the onem2mlib module.
"""

#
#	on2M2M resource types
#

Type_Mixed =  0
""" The *Mixed* type, e.g. for &lt;group> resources that point to resources of various types. """
Type_AE =  2
""" The &lt;AE> resource type. """
Type_Container =  3
""" The &lt;container> resource type. """
Type_ContentInstance =  4
""" The &lt;contentInstance> resource type. """
Type_CSEBase = 5
""" The &lt;CSE> resource type. """
Type_Group =  9
""" The &lt;group> resource type. """
Type_FlexContainer = 24
""" The &lt;flexContainer> resource type. """


#
#	CSE
#

Cse_Type_IN = 1
""" Used for the &lt;CSEBase> resource's *cseType* attribute. In indicates an IN-CSE. """
Cse_Type_MN = 2
""" Used for the &lt;CSEBase> resource's *cseType* attribute. In indicates an MN-CSE. """
Cse_Type_ASN = 3
""" Used for the &lt;CSEBase> resource's *cseType* attribute. In indicates an ASN-CSE. """


#
#	Group
#

Grp_ABANDON_MEMBER =  1
""" Used for the &lt;group> resource's *consistencyStrategy* attribute. Abandon group members that 
don't match the groups type. """
Grp_ABANDON_GROUP =  2
""" Used for the &lt;group> resource's *consistencyStrategy* attribute. Abandon the whole group when
there are members that don't match the group type. """
Grp_SET_MIXED =  3
""" Used for the &lt;group> resource's *consistencyStrategy* attribute. Set the group's type to *mixed*
when there are member that don't match the group type. """


Grp_def_maxNrOfMembers = 10
""" Default for the &lt;group> resource's *maxNrOfMembers* attribute. """
