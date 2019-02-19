#
#	createAE.py
#
#	(c) 2017 by Andreas Kraft
#	License: BSD 3-Clause License. See the LICENSE file for further details.
#
#	This example shows how to create an <AE> resource in an CSE.
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

	#
	# Create and print an <AE> resource on the CSE in one step.
	# This is easier and more useful in most cases, since a new resource
	# is created or, if it already exsists, the existing resource is returned.
	#
	aeName = 'exampleAE_'+str(uuid.uuid4().hex)	# unique name for the <AE>
	ae = AE(cse, resourceName=aeName)	# create or retrieve
	print(ae)	# This should be the same <AE> as before

	#
	# Create an <AE> with the convenient method and print it.
	#
	aeName2 = 'exampleAE_'+str(uuid.uuid4().hex)	# unique name for the <AE>
	ae2 = cse.addAE(aeName2)
	print(ae2)



