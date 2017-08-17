#
#	createAE.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This example shows how to create an <AE> resource in an CSE.
#

import uuid, sys
sys.path.append('..')
import onem2mlib.session as SE
from onem2mlib.resources import *


if __name__ == '__main__':
	# create session
	session = SE.Session('http://localhost:8282', 'admin', 'admin')

	# get the <CSEBase> resource
	cse = CSEBase(session, 'mn-cse')

	# create and print an <AE> resource
	aeName = 'exampleAE_'+str(uuid.uuid4().hex)	# unique name for the <AE>
	ae = AE(cse, resourceName=aeName)
	ae.createInCSE()
	print(ae)