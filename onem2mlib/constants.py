#
#	constants.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This module defines the constants used in various modules.
#

"""
This sub-module defines various constants used in the onem2mlib module.
"""

#
#	library configuration
#

Support_XML = False
""" Enabling or disabling XML serialization support. """

#
#	on2M2M resource types
#

Type_Mixed =  0
""" The *Mixed* type, e.g. for &lt;group> resources that point to resources of various types. """

Type_ACP = 1
""" The &lt>ACP> resource type. """
Type_ACP_SN = 'acp'
""" Shortname for the &lt;ACP> resource type. """

Type_AE =  2
""" The &lt;AE> resource type. """
Type_AE_SN = 'ae'
""" Shortname for the &lt;AE> resource type. """

Type_Container =  3
""" The &lt;container> resource type. """
Type_Container_SN = 'cnt'
""" Shortname for the &lt;container> resource type. """

Type_ContentInstance =  4
""" The &lt;contentInstance> resource type. """
Type_ContentInstance_SN = 'cin'
""" Shortname for the &lt;contentInstance> resource type. """

Type_CSEBase = 5
""" The &lt;CSE> resource type. """
Type_CSEBase_SN = 'cb'
""" The &lt;CSEBase> resource type. """

Type_Group =  9
""" The &lt;group> resource type. """
Type_Group_SN = 'grp'
""" Shortname for the &lt;group> resource type. """

Type_Node = 14
""" The &lt;node> resource type. """
Type_Node_SN = 'nod'
""" Shortname for the &lt;node> resource type. """

Type_RemoteCSE = 16
""" The &lt;remoteCSE> resource type. """
Type_RemoteCSE_SN = 'csr'
""" Shortname for the &lt;remoteCSE> resource type. """

Type_Subscription = 23
""" The &lt;subscription> resource type"""
Type_Subscription_SN = 'sub'
""" Shortname for the &lt;subscription> resource type. """

Type_FlexContainer = 28
""" The &lt;flexContainer> resource type. """
# No implicit shortname for the flexContainer.


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
#	ACP
#
Acp_CREATE = 1
""" Privilege to create a child resource. """
Acp_RETRIEVE = 2
""" Privilege to retrieve the content of an addressed resource. """
Acp_UPDATE = 4
""" Privilege to update the content of an addressed resource. """
Acp_DELETE = 8
""" Privilege to delete an addressed resource. """
Acp_NOTIFY = 16
""" Privilege to receive a notification. """
Acp_DISCOVER = 32
""" Privilege to discover the resource. """
Acp_ALL = 63
""" Shortcut for all privileges. """


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


#
#	Discovery
#
Dsc_AND = 1
""" Used to define the filter operation. Perform a logical conjunction (logical AND) on all filter criteria. """
Dsc_OR = 2
""" Used to define the filter operation. Perform a logical disjunction (logical OR) on all filter criteria. """


#
#	Subscriptions
#
Sub_AllAttributes = 1
""" Constant for notificationContentType: Send all the resource's attributes in a notification. """
Sub_ModefiedAttributes = 2
""" Constant for notificationContentType: Send only the modified resource's attributes in a notification. """
Sub_ResourceID = 3
""" Constant for notificationContentType: Send only the  resource's ID in a notification. """


#
#	Network configurations
#

NETWORK_REQUEST_TIMEOUT = 20
""" Timeout after n seconds in requests. """

Encoding_XML = 1
""" Specify XML as the request encoding format. """

Encoding_JSON = 2
""" Specify JSON as the request encoding format. """
