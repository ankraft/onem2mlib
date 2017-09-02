#
#	accessControlPolicy.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This example shows how to create an <accessControlPolicy> resource in an CSE.
#

import uuid, sys
sys.path.append('..')
import onem2mlib.session as SE
import onem2mlib.constants as CON
from onem2mlib.resources import *


if __name__ == '__main__':

	# Create session
	session = SE.Session('http://localhost:8282', 'admin:admin')

	# Get the <CSEBase> resource
	cse = CSEBase(session, 'mn-cse')

	# Create AccessControlRules for privileges and self-privileges
	privileges = [ 
		AccessControlRule(['admin:admin'], CON.Acp_ALL),
		AccessControlRule(['user:user'], CON.Acp_RETRIEVE+CON.Acp_DISCOVER)
	]
	selfPrivileges = [ 
		AccessControlRule(['admin:admin'], CON.Acp_ALL)
	]

	# Create a new accessControlPolicy with the previous created privileges and self-privileges
	acpName = 'exampleACP_'+str(uuid.uuid4().hex)	# unique name
	acp = AccessControlPolicy(cse, resourceName=acpName, privileges=privileges, selfPrivileges=selfPrivileges, instantly=True)
	print(acp)

	# Create a 
	aeName = 'exampleAE_'+str(uuid.uuid4().hex)	# unique name for the <AE>
	ae = AE(cse, resourceName=aeName)
	ae.setAccessControlPolicies(acp)
	ae.createInCSE()
	print(ae)


