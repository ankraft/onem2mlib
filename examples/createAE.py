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

	# Create session
	session = SE.Session('http://localhost:8282', 'admin', 'admin')

	# Get the <CSEBase> resource
	cse = CSEBase(session, 'mn-cse')

	#
	# Create and print an <AE> resource on the CSE in one step.
	# This is easier and more useful in most cases, since a new resource
	# is created or, if it already exsists, the existing resource is returned.
	#
	aeName = 'exampleAE_'+str(uuid.uuid4().hex)	# unique name for the <AE>
	ae = AE(cse, resourceName=aeName, instantly=True)	# create or retrieve
	print(ae)	# This should be the same <AE> as before

	#
	# Create and print an <AE> resource on the CSE step-by-step. 
	# This way one can make modifications to the ae object before 
	# creating it in the CSE
	#
	aeName2 = 'exampleAE_'+str(uuid.uuid4().hex)	# unique name for the <AE>
	ae2 = AE(cse, resourceName=aeName2, instantly=True)
	ae2.createInCSE()
	print(ae2)



