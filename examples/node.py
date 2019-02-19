#
#	node.py
#
#	(c) 2019 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This example shows how to handle the <node> resource in an CSE.
#

import uuid, sys, logging
sys.path.append('..')
from onem2mlib import *
import conf


if __name__ == '__main__':
	logging.basicConfig(level=conf.LOGGINGLEVEL)
	logging.getLogger('urllib3').setLevel(logging.CRITICAL)

	# Create session
	session = Session(conf.CSEURL, conf.ORIGINATOR)

	# Get the <CSEBase> resource
	cse = CSEBase(session, conf.CSEID)
	print(cse)

	# Create a Node
	nodeName='exampleNode_'+str(uuid.uuid4().hex)	# unique name for the <AE>
	node = Node(cse, resourceName=nodeName, nodeID='12345')
	print(node)

	# Create an AE
	aeName = 'exampleAE_'+str(uuid.uuid4().hex)	# unique name for the <AE>
	ae = AE(cse, resourceName=aeName)
	ae.nodeLink = node.resourceID
	ae.updateInCSE()
	print(ae)

	node.retrieveFromCSE()
	print(node)
