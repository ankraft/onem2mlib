#
#	accessControlPolicy.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This example shows how to create an <accessControlPolicy> resource in an CSE.
#

import uuid, sys, logging
sys.path.append('..')
from onem2mlib import *
import onem2mlib.constants as CON
import conf


if __name__ == '__main__':
	logging.basicConfig(level=conf.LOGGINGLEVEL)
	logging.getLogger('urllib3').setLevel(logging.CRITICAL)

	# Create session
	session = Session(conf.CSEURL, conf.ORIGINATOR)

	# Get the <CSEBase> resource
	cse = CSEBase(session, conf.CSEID)

	# Create AccessControlRules for privileges and self-privileges
	privileges = [ 
		AccessControlRule([conf.ORIGINATOR], CON.Acp_ALL),
		AccessControlRule(['user:user'], CON.Acp_RETRIEVE+CON.Acp_DISCOVER)
	]
	selfPrivileges = [ 
		AccessControlRule([conf.ORIGINATOR], CON.Acp_ALL)
	]

	# Create a new accessControlPolicy with the previous created privileges and self-privileges
	acpName = 'exampleACP_'+str(uuid.uuid4().hex)	# unique name
	acp = AccessControlPolicy(cse, resourceName=acpName, privileges=privileges, selfPrivileges=selfPrivileges)
	print(acp)

	# Create a 
	aeName = 'exampleAE_'+str(uuid.uuid4().hex)	# unique name for the <AE>
	ae = AE(cse, resourceName=aeName, instantly=False)
	ae.setAccessControlPolicies(acp)
	ae.createInCSE()
	print(ae)


